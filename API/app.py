from core.api import bp
from sanic import Sanic

client = None
app = Sanic(__name__)
app.blueprint(bp)

if __name__ == '__main__':
	app.run(host="127.0.0.1", port=5000, debug=True)