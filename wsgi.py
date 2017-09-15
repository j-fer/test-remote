#!/usr/bin/python
import os
from datetime import datetime
import mimetypes

virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass
#
# IMPORTANT: Put any additional includes below this line.  If placed above this
# line, it's possible required libraries won't be in your searchable path
#




def show_404_app(environ, start_response):
    ctype = 'text/html'
    response_headers = [('Content-Type', ctype)]
    start_response('404 Not Found', response_headers)
    response_body = '<html><head><title>Not found</title></head><body><p>Page not found in our servers. <a href="/">Visit the main page</a>.</p></body></html>'
    return response_body


def content_type(path):
    """Return a guess at the mime type for this path
    based on the file extension"""
    mime_type, discard = mimetypes.guess_type(path)
    if mime_type != None:
        return mime_type
    return "application/octet-stream"

def last_modified(path):
    return datetime.utcfromtimestamp(os.path.getmtime(path)).strftime('%a, %d %b %Y %H:%M:%S GMT')

def static_app(environ, start_response):
    """Serve static files"""
    mypath = os.path.dirname(os.path.realpath(__file__))
    
    path = environ['PATH_INFO']

    for char in ('..', '*', '!', '`', '$', '<', '>'):
        path = path.replace(char, '')

    path = mypath + '/static' + path

    
    if path.endswith(('py', 'pyc', 'sh')):
        return show_404_app(environ, start_response)
    elif path.endswith('/'):
        path += 'index.html'
    if os.path.exists(path):
        with open(path, 'rb') as f:
            content = f.read()
        ctype = content_type(path)
        headers = [('Content-Type', ctype), \
                   ('Last-Modified', last_modified(path)), \
                   ('Content-Length', str(len(content)))]
        start_response('200 OK', headers)
        # if ctype == 'application/pdf' and os.path.exists(mypath + '/../logs'):
        return [content]            
    else:
        return show_404_app(environ, start_response)    

    
# the main WSGI application
def application(environ, start_response):
    pi = environ['PATH_INFO']
    qs = environ['QUERY_STRING']
    return static_app(environ, start_response)
   
    
#
# Below for testing only
#
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    # httpd.handle_request()

    # Serve until process is killed
    httpd.serve_forever()

    
