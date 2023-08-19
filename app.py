from flask import Flask, render_template

from modules.login.route import login_blueprint, fyers_model
from modules.display.server import server_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = "password"  # TODO make better and save in keyvault

app.register_blueprint(login_blueprint)
app.register_blueprint(server_blueprint)


@app.route('/')
def index():
    return render_template('index.html', loginStatus=fyers_model.checkConnection())


if __name__ == '__main__':
    app.run(debug=True, port=5000)
