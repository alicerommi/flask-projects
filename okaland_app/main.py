from websites import create_app
from waitress import serve

app=create_app()
from waitress import serve
serve(app, host='0.0.0.0', port=5010)
