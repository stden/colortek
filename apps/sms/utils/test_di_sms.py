# -*- coding: utf-8
import re
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import SocketServer
from hashlib import md5
from urlparse import urlparse
import cgi


PORT = 8990
HOST = ""

re_schema = re.compile('^/$', re.M|re.U)

class B3BanServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super(B3BanServer, self).__init__(*args, **kwargs)

class B3BanRequestHandler(BaseHTTPRequestHandler):
    def proceed_query(self, query_string):
        if not query_string:
            self.wfile.write('ERR 100')
            return

        query_string += '&password=1233123'
        data = cgi.parse_qs(query_string)

        md5_hash_dst = data.get('md5', [''])[0] # it's some sort of trick

        # proceeding pre ERRORS
        if 'ta' in data:
            if data['ta'][0] not in ('pv', 'bc', 'ds',):
                self.wfile.write('ERR 101')
                return

        if data['ta'][0] == 'pv']:
            # proceeding required fields missing
            required_fields = ['ta', 'u', 'from', 'md5']
            for field in required_fields:
                if not field in data:
                    self.wfile.write('ERR 102')
                    return

            # proceeding blank addressee and message fields
            message_fields = ['to', 'msg', ]
            for field in message_fields:
                if not field in data:
                    self.wfile.write('ERR 200')
                    return

        # clean md5 data to proceed
        if 'md5' in data:
            del data['md5']

        md5_string = ''
        fields = [
            'u', 'ta', 'last', 'c', 'slid',
            'to', 'from', 'type', 'password'
        ]
        md5_string = "".join([data[f][0] if f in data else '' for f in fields])
        md5_hash_src = md5(md5_string).hexdigest()
        
        if md5_hash_src != md5_hash_dst:
            self.wfile.write('ERR 100')
            return
        self.wfile.write('OK 100')
        #hash_string = self.path.split('?')[1]
        #keys = hash_string.split('&')
        return

    def do_GET(self):
        # proceed get param
        if re.match(re_schema, self.path):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            # proceed data
            query_string = urlparse(self.path).query
            self.proceed_query(query_string)
            return

        self.send_response(404)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write('not ok')
        return
        super(B3BanServer, self).do_GET()

    def do_POST(self):
        if re.match(re_schema, self.path):
            length = int(self.headers.getheader('Content-Length'))
            data = self.rfile.read(length)
            self.send_response(200)
            self.send_header("Content-Type", 'text/html')
            self.end_headers()
            self.proceed_query(data)
            #self.wfile.write('')
            return
        self.send_response(403)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write("POST not permitted here")
        return

Handler = B3BanRequestHandler

httpd = SocketServer.TCPServer((HOST, PORT), Handler)

print "serving at port", PORT
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print "Exiting"
    httpd.socket.close()
