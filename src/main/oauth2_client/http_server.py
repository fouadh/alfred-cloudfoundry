import logging
import threading
import json
from oauth2_client.imported import *

_logger = logging.getLogger(__name__)


class _ReuseAddressTcpServer(TCPServer):
    def __init__(self, host, port, handler_class):
        self.allow_reuse_address = True
        TCPServer.__init__(self, (host, port), handler_class)


def read_request_parameters(path):
    params_received = dict()
    idx = path.find('?')
    if idx >= 0 and (idx < len(path) - 1):
        for params in path[idx + 1:].split('&'):
            param_splitted = params.split('=')
            if len(param_splitted) == 2:
                params_received[param_splitted[0]] = unquote(param_splitted[1])
    return params_received


def start_http_server(port, host='', callback=None):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            _logger.debug('GET - %s' % self.path)
            params_received = read_request_parameters(self.path)
            response = 'Response received (%s). Result was transmitted to the original thread. You can close this window.' % json.dumps(params_received)
            self.send_response(OK, 'OK')
            self.send_header("Content-type", 'text/plain')
            self.send_header("Content-Length", len(response))
            self.end_headers()
            try:
                self.wfile.write(bufferize_string(response))
            finally:
                if callback is not None:
                    callback(params_received)
                self.wfile.flush()

    _logger.debug('start_http_server - instantiating server to listen on "%s:%d"', host, port)
    httpd = _ReuseAddressTcpServer(host, port, Handler)

    def serve():
        _logger.debug('server daemon - starting server')
        httpd.serve_forever()
        _logger.debug('server daemon - server stopped')

    thread_type = threading.Thread(target=serve)
    thread_type.start()
    return httpd


def stop_http_server(httpd):
    _logger.debug('stop_http_server - stopping server')
    httpd.shutdown()
