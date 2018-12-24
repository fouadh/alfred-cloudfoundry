import sys

import requests

if sys.version_info.major == 2:
    from SocketServer import TCPServer
    from BaseHTTPServer import BaseHTTPRequestHandler

    from httplib import UNAUTHORIZED, INTERNAL_SERVER_ERROR, OK
    from urlparse import urlparse
    from urllib import quote
    from urllib2 import unquote

    requests.packages.urllib3.disable_warnings()


    def bufferize_string(content):
        return content

    def unbufferize_buffer(content):
        return content

elif sys.version_info.major == 3:
    from socketserver import TCPServer
    from http.server import BaseHTTPRequestHandler
    from http.client import UNAUTHORIZED, INTERNAL_SERVER_ERROR, OK
    from urllib.parse import urlparse, quote
    from urllib.parse import unquote


    def bufferize_string(content):
        return bytes(content, 'UTF-8')

    def unbufferize_buffer(content):
        return content.decode('UTF-8')

else:
    raise ImportError('Invalid major version: %d' % sys.version_info.major)
