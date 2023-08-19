from modules.login.route import fyers_model

from modules.strategies.Symbols import Symbols
from modules.strategies.strategiesHandler import StrategyHandler

from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from modules.logging.logging import loggerObject as logger

symbolsHandler = Symbols(fyers_model, logger)
strategiesHandler = StrategyHandler(fyers_model, symbolsHandler, logger)

# import supported strategies
from modules.strategies.supported.monthStraddle import MonthStraddle

supportedStrategies = {
    "Month Straddle": {
        "description": "Month Straddle",
        "class": MonthStraddle,
    }
}

strategies_blueprint = Blueprint('strategies', __name__, url_prefix="/strategies", template_folder="templates")


# nifty50 = symbolsHandler.get('nifty50')
# indiavix = symbolsHandler.get('indiavix')

@strategies_blueprint.route('supported')
def getSupportedStrategies():
    return list(supportedStrategies.keys())

@strategies_blueprint.route('running')
def getRunningStrategies():
    response = []

    for i, (stratID, strategy) in enumerate(strategiesHandler.strategies_dict.items()):
        response.append([strategy.getIntro(), strategy.getPnL()])

    return response
@strategies_blueprint.route('add')
def addStrategy():
    return render_template('add_strat.html', strategies=supportedStrategies.keys())