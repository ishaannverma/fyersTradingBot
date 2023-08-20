# FYERS API PROJECT TO TRADE USING ALGORITHM
from flask import Blueprint

from modules.display.funds import funds_blueprint
from modules.display.positions import positions_blueprint
from modules.strategies.strategies_route import strategies_blueprint

server_blueprint = Blueprint('server', __name__, url_prefix="/server")
server_blueprint.register_blueprint(funds_blueprint)
server_blueprint.register_blueprint(positions_blueprint)
server_blueprint.register_blueprint(strategies_blueprint)

# TODO add button or form to start any strategy
