from modules.login.route import fyers_model

from modules.strategies.Symbols import Symbols
from modules.strategies.strategiesHandler import StrategyHandler

from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField, SubmitField
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


class AddStratForm(FlaskForm):
    paperTrade = BooleanField('Is this a paper trade?', validators=[DataRequired()])
    stratName = SelectField('Strat Name', choices=supportedStrategies.keys(), validators=[DataRequired()])
    submit = SubmitField("Submit")


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


@strategies_blueprint.route('add', methods=['GET', 'POST'])
def addStrategy():
    paperTrade = True
    stratName = None
    form = AddStratForm()

    if form.validate_on_submit():
        paperTrade = form.paperTrade.data
        stratName = form.stratName.data
        print(f"{paperTrade}, {stratName}")

        return "Success message"

        # set this to none, empty here TODO

    return render_template('add_strat.html', stratName=stratName, paperTrade=paperTrade, form=form)
