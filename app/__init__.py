from flask import Flask, Blueprint

app = Flask(__name__)

# app.url_map.default_subdomain = 'www'
# app.config['SERVER_NAME'] = 'guochengtsinghua.com'

# member = Blueprint('member', __name__)
# app.register_blueprint(member, subdomain='static')

import views
