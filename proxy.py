#!/usr/bin/env python3
import http.server, http.client, socketserver, threading, sys, re

def proxyConfig(handler):
  headers = [('Content-Type', 'application/x-javascript-config')]
  data = b'''function FindProxyForURL(url, host) {
    if (/^http:\/\/boards\.4chan\.org\//.test(url)) {
      return 'PROXY localhost:8000';
    }
    return 'DIRECT';
  }
  '''
  return headers, data

def localScript(filename):
  def callback(handler):
    headers = [
      ('Content-Type', 'application/javascript'),
      ('Expires', handler.date_time_string())
    ]
    with open(filename, 'rb') as f:
      data = f.read()
    return headers, data
  return callback

port = 8000
resources = {'/proxy.pac': proxyConfig}

for arg in sys.argv[1:]:
  if re.match(r'^\d+$', arg):
    port = int(arg)
  else:
    resources['/script.js'] = localScript(arg)

class RequestHandler(http.server.BaseHTTPRequestHandler):
  def do_HEAD(self):
    self.do_GET()

  def do_GET(self):
    if self.headers.get('Host', '').split(':')[0] == 'localhost':
      self.local()
    else:
      self.proxy()

  def local(self):
    if self.path in resources:
      headers, data = resources[self.path](self)
      self.send_response(200)
      for header in headers:
        self.send_header(*header)
      self.send_header('Content-Length', len(data))
      self.end_headers()
      if self.command != 'HEAD':
        self.wfile.write(data)
    else:
      self.send_error(404)

  def proxy(self):
    del self.headers['Accept-Encoding']
    try:
      conn = http.client.HTTPConnection('boards.4chan.org')
      conn.request('GET', self.path, headers=self.headers)
      response = conn.getresponse()
      body = response.read()
    finally:
      conn.close()
    url = b'https://ccd0.github.io/4chan-x/builds/4chan-X.user.js'
    if '/script.js' in resources:
      url = b'http://localhost:8000/script.js'
    body = body.replace(b'<head>', b'<head><script src="' + url + b'"></script>', 1)
    self.send_response(response.status, response.reason)
    for header, value in response.getheaders():
      if header.lower() not in ('date', 'connection', 'transfer-encoding', 'content-length'):
        self.send_header(header, value)
    self.send_header('Content-Length', len(body))
    self.end_headers()
    if self.command != 'HEAD':
      self.wfile.write(body)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
  pass

server = ThreadedHTTPServer(('localhost', port), RequestHandler)
thread = threading.Thread(target=server.serve_forever)
thread.start()
