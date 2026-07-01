from flask import Flask

app = Flask(__name__)

from routes.whatsapp import *

if __name__ == "__main__":
    app.run(port=5000)