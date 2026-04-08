# Native WSGI entry point (no Flask dependency)
# If this works, then Flask was the problem.
def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'application/json')]
    start_response(status, headers)
    return [b'{"status": "native-wsgi-working"}']

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    print("Serving on port 8000...")
    httpd.serve_forever()
