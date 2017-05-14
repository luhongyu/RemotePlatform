#!flask/bin/python
from app import app
from flask_sslify import SSLify

# from OpenSSL import SSL
# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('/Users/luhongyu/server.key')
# context.use_certificate_file('/Users/luhongyu/server.crt')
#
# context = ('/Users/luhongyu/server.key', '/Users/luhongyu/server.crt')

import ssl
ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
ctx.load_cert_chain('/Users/luhongyu/ssl.cert', '/Users/luhongyu/ssl.key')

app.run(host="0.0.0.0", port=1024, debug=True, threaded=True, ssl_context=ctx)
# app.run(host='localhost', debug=True, threaded=True, port=5000)
# use_reloader=False,
