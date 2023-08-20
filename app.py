from flask import Flask, render_template

from modules.login.login_route import login_blueprint, fyers_model_class_obj
from modules.display.server import server_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = "password"  # TODO make better and save in keyvault

app.register_blueprint(login_blueprint)
app.register_blueprint(server_blueprint)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False, port=5000)
