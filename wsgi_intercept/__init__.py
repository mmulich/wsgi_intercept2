import sys
import urllib.request, urllib.parse, urllib.error
import traceback
from socket import _GLOBAL_DEFAULT_TIMEOUT
from io import BytesIO, StringIO
from http.client import _strict_sentinel
from http.client import HTTPConnection


debuglevel = 0
# 1 basic
# 2 verbose

####

#
# Specify which hosts/ports to target for interception to a given WSGI app.
#
# For simplicity's sake, intercept ENTIRE host/port combinations;
# intercepting only specific URL subtrees gets complicated, because we don't
# have that information in the HTTPConnection.connect() function that does the
# redirection.
#
# format: key=(host, port), value=(create_app, top_url)
#
# (top_url becomes the SCRIPT_NAME)

_intercepts = {}

def add_intercept(host, port, app_create_fn, script_name=''):
    """
    Add a WSGI intercept call for host:port, using the app returned
    by app_create_fn with a SCRIPT_NAME of 'script_name' (default '').
    """
    _intercepts[(host, port)] = (app_create_fn, script_name)

def remove_intercept(*args):
    """
    Remove the WSGI intercept call for (host, port).  If no arguments are
    given, removes all intercepts
    """
    global _intercepts
    if len(args) == 0:
        _intercepts = {}
    else:
        key = (args[0], args[1])
        if key in _intercepts:
            del _intercepts[key]

def bytes_to_str(value):
    """Convert a bytestring to a unicode string."""
    return value.decode('utf-8')

def make_environ(inp, host, port, script_name):
    """
    Take `inp` (input) like a web server would receive it on a host and port.
    Parse the input into a WSGI environment dictionary.

    Set 'SCRIPT_NAME' from the 'script_name' input, and, if present,
    remove it from the beginning of the PATH_INFO variable.
    """
    environ = {}
    content_type = None
    content_length = None
    cookies = []
    method_line = bytes_to_str(inp.readline())    
    
    # Parse the input up to the first blank line (or its end).
    for line in inp:
        line = bytes_to_str(line)  # inp is a bytestring.
        if not line.strip():
            # The HTTP protocol has a blank between the header information
            # and the message body.
            break
        k, v = line.strip().split(':', 1)
        v = v.lstrip()

        # Take care of special headers. Put the remaining headers
        # into the environ with the HTTP_ prefix.
        if k.lower() == 'content-type':
            content_type = v
        elif k.lower() == 'content-length':
            content_length = v
        elif k.lower() == 'cookie' or k.lower() == 'cookie2':
            cookies.append(v)
        else:
            h = k.upper()
            h = h.replace('-', '_')
            environ['HTTP_' + h] = v

        if debuglevel >= 2:
            print('HEADER:', k, v)

    # Decode the method line
    if debuglevel >= 2:
        print('METHOD LINE:', method_line)
    method, url, protocol = method_line.split(' ')

    # Capture and remove the script_name from the url, if it's there.
    if not url.startswith(script_name):
        script_name = ''  # @CTB what to do -- bad URL.  scrap?
    else:
        url = url[len(script_name):]

    # Capture the query string that has optionally been passed along with
    # the url.
    url = url.split('?', 1)
    path_info = url[0]
    query_string = ""
    if len(url) == 2:
        query_string = url[1]

    if debuglevel:
        # Print all know information.
        print("method: %s; script_name: %s; path_info: %s; query_string: %s" \
            % (method, script_name, path_info, query_string))

    r = inp.read()
    inp = BytesIO(r)

    # Fill out our environment dictionary.
    environ.update({ "wsgi.version" : (1,0),
                     "wsgi.url_scheme": "http",
                     "wsgi.input" : inp,  # to read for POSTs
                     "wsgi.errors" : StringIO(),
                     "wsgi.multithread" : 0,
                     "wsgi.multiprocess" : 0,
                     "wsgi.run_once" : 0,
    
                     "PATH_INFO" : path_info,
                     "QUERY_STRING" : query_string,
                     "REMOTE_ADDR" : '127.0.0.1',
                     "REQUEST_METHOD" : method,
                     "SCRIPT_NAME" : script_name,
                     "SERVER_NAME" : host,
                     "SERVER_PORT" : str(port),
                     "SERVER_PROTOCOL" : protocol,
                     })

    # Optional environment variables: query_string, content_type & length.
    if query_string:
        environ['QUERY_STRING'] = query_string        
    if content_type:
        environ['CONTENT_TYPE'] = content_type
        if debuglevel >= 2:
            print('CONTENT-TYPE:', content_type)
    if content_length:
        environ['CONTENT_LENGTH'] = content_length
        if debuglevel >= 2:
            print('CONTENT-LENGTH:', content_length)

    # Handle cookies.
    if cookies:
        environ['HTTP_COOKIE'] = "; ".join(cookies)

    if debuglevel:
        print('WSGI environ dictionary:', environ)
    return environ


class FakeWSGISocket:
    """
    Handle HTTP traffic and stuff into a WSGI application object instead.

    Note that this class assumes:
    
     1. 'makefile' is called (by the response class) only after all of the
        data has been sent to the socket by the request class;
     2. non-persistent (i.e. non-HTTP/1.1) connections.
    """
    def __init__(self, app, host, port, script_name):
        self.app = app                  # WSGI app object
        self.host = host
        self.port = port
        self.script_name = script_name  # SCRIPT_NAME (app mount point)

        self.inp = BytesIO()           # stuff written into this "socket"
        self.write_results = []          # results from the 'write_fn'
        self.results = None             # results from running the app
        self.output = BytesIO()        # all output from the app, incl headers

    def makefile(self, *args, **kwargs):
        """
        'makefile' is called by the HTTPResponse class once all of the
        data has been written.  So, in this interceptor class, we need to:
        
          1. build a start_response function that grabs all the headers
             returned by the WSGI app;
          2. create a wsgi.input file object 'inp', containing all of the
             traffic;
          3. build an environment dict out of the traffic in inp;
          4. run the WSGI app & grab the result object;
          5. concatenate & return the result(s) read from the result object.

        @CTB: 'start_response' should return a function that writes
        directly to self.result, too.
        """
        # dynamically construct the start_response function for no good reason.

        def start_response(status, headers, exc_info=None):
            # construct the HTTP request.
            self.output.write(b"HTTP/1.0 " + status.encode('iso-8859-1') + b"\n")
            
            for k, v in headers:
                header_line = '%s: %s\n' % (k, v,)
                self.output.write(header_line.encode('iso-8859-1'))
            self.output.write(b'\n')

            def write_fn(s):
                self.write_results.append(s)
            return write_fn

        # construct the wsgi.input file from everything that's been
        # written to this "socket".
        inp = BytesIO(self.inp.getvalue())

        # build the environ dictionary.
        environ = make_environ(inp, self.host, self.port, self.script_name)

        # run the application.
        app_result = self.app(environ, start_response)
        self.result = iter(app_result)

        ###

        # read all of the results.  the trick here is to get the *first*
        # bit of data from the app via the generator, *then* grab & return
        # the data passed back from the 'write' function, and then return
        # the generator data.  this is because the 'write' fn doesn't
        # necessarily get called until the first result is requested from
        # the app function.
        #
        # see twill tests, 'test_wrapper_intercept' for a test that breaks
        # if this is done incorrectly.

        try:
            generator_data = None
            try:
                generator_data = next(self.result)
            finally:
                for data in self.write_results:
                    self.output.write(data)

            if generator_data:
                self.output.write(generator_data)
                while 1:
                    data = next(self.result)
                    self.output.write(data)
        except StopIteration:
            pass

        if hasattr(app_result, 'close'):
            app_result.close()
            
        if debuglevel >= 2:
            print("***", self.output.getvalue(), "***")

        # return the concatenated results.
        return BytesIO(self.output.getvalue())

    def sendall(self, str):
        """
        Save all the traffic to self.inp.
        """
        if debuglevel >= 2:
            print(">>>", str, ">>>")

        self.inp.write(str)

    def close(self):
        "Do nothing, for now."
        pass


class InterceptedHTTPConnection(HTTPConnection):
    """
    Intercept all traffic to certain hosts & redirect into a WSGI
    application object.
    """
    def get_app(self, host, port):
        """
        Return the app object for the given (host, port).
        """
        key = (host, int(port))

        app, script_name = None, None
        
        if key in _intercepts:
            (app_fn, script_name) = _intercepts[key]
            app = app_fn()

        return app, script_name        
    
    def connect(self):
        """
        Override the connect() function to intercept calls to certain
        host/ports.
        
        If no app at host/port has been registered for interception then 
        a normal HTTPConnection is made.
        """
        if debuglevel:
            sys.stderr.write('connect: %s, %s\n' % (self.host, self.port,))
                             
        try:
            (app, script_name) = self.get_app(self.host, self.port)
            if app:
                if debuglevel:
                    sys.stderr.write('INTERCEPTING call to %s:%s\n' % \
                                     (self.host, self.port,))
                self.sock = FakeWSGISocket(app, self.host, self.port,
                                           script_name)
            else:
                HTTPConnection.connect(self)
                
        except Exception as e:
            if debuglevel:  # intercept & print out tracebacks
                traceback.print_exc()
            raise


try:
    import ssl
    from http.client import HTTPSConnection
except ImportError:
    pass
else:
    class InterceptedHTTPSConnection(HTTPSConnection):
        """
        Intercept all traffic to certain hosts & redirect into a WSGI
        application object.
        """

        # XXX http://bugs.python.org/issue13771
        def __init__(self, host, port=None, key_file=None, cert_file=None,
                     strict=_strict_sentinel, timeout=_GLOBAL_DEFAULT_TIMEOUT,
                     source_address=None, *, context=None, check_hostname=None):
            # The original line as of Python 3.2 reads:
            # super(HTTPSConnection, self).__init__(host, port, strict, timeout,
            #                                       source_address)
            # We modify it to call the subclass directly to avoid a recursion error.
            HTTPConnection.__init__(self, host, port, strict, timeout, source_address)

            self.key_file = key_file
            self.cert_file = cert_file
            if context is None:
                # Some reasonable defaults
                context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                context.options |= ssl.OP_NO_SSLv2
            will_verify = context.verify_mode != ssl.CERT_NONE
            if check_hostname is None:
                check_hostname = will_verify
            elif check_hostname and not will_verify:
                raise ValueError("check_hostname needs a SSL context with "
                                 "either CERT_OPTIONAL or CERT_REQUIRED")
            if key_file or cert_file:
                context.load_cert_chain(cert_file, key_file)
            self._context = context
            self._check_hostname = check_hostname

        def get_app(self, host, port):
            """
            Return the app object for the given (host, port).
            """
            key = (host, int(port))

            app, script_name = None, None

            if key in _intercepts:
                (app_fn, script_name) = _intercepts[key]
                app = app_fn()

            return app, script_name        

        def connect(self):
            """
            Override the connect() function to intercept calls to certain
            host/ports.

            If no app at host/port has been registered for interception then 
            a normal HTTPSConnection is made.
            """
            if debuglevel:
                sys.stderr.write('connect: %s, %s\n' % (self.host, self.port,))

            try:
                (app, script_name) = self.get_app(self.host, self.port)
                if app:
                    if debuglevel:
                        sys.stderr.write('INTERCEPTING call to %s:%s\n' % \
                                         (self.host, self.port,))
                    self.sock = FakeWSGISocket(app, self.host, self.port,
                                               script_name)
                else:
                    HTTPSConnection.connect(self)

            except Exception as e:
                if debuglevel:  # intercept & print out tracebacks
                    traceback.print_exc()
                raise

