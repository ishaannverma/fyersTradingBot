from flask import Flask, url_for
from modules.login.login import login_blueprint

app = Flask(__name__)

app.register_blueprint(login_blueprint)


@app.route('/')
def index():
    return f'<a href="{url_for("login.loginStarter")}">Click me </a>'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
