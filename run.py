#!flask/bin/python
from app import app

# app.run(debug=True, use_reloader=False)
app.run(host='10.129.248.53', port=80)
