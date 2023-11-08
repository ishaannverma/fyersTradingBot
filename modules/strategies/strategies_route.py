from modules.login.login_route import fyers_model_class_obj

from modules.strategies.Symbols import Symbols
from modules.strategies.strategiesHandler import StrategyHandler

from flask import Blueprint, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from modules.logging.logging import loggerObject as logger
from modules.logic.templates import LogType
from modules.logic.dateParsing import dateStringFromTimestamp
import pandas as pd

symbolsHandler = Symbols()
strategiesHandler = StrategyHandler(symbolsHandler)

# import supported strategies
from modules.strategies.supported.monthStraddle import MonthStraddle

supportedStrategies = {
    "Month Straddle": {
        "description": "Month Straddle",
    }
}


class AddStratForm(FlaskForm):
    paperTrade = BooleanField('Is this a paper trade?', validators=[DataRequired()])
    stratName = SelectField('Strat Name', choices=supportedStrategies.keys(), validators=[DataRequired()])
    submit = SubmitField("Submit")


strategies_blueprint = Blueprint('strategies', __name__, url_prefix="/strategies", template_folder="templates")


@strategies_blueprint.route('supported')
def getSupportedStrategies():
    return render_template('supported_strats.html', strats=supportedStrategies)


@strategies_blueprint.route('running')
def getRunningStrategies():
    response = []

    for i, (stratID, strategy) in enumerate(strategiesHandler.strategies_dict.items()):
        response.append({
            'id': stratID,
            "intro": strategy.getIntro(short=True),
            "pnl": strategy.getPnL()
        })

    return render_template('active_strats.html', strats=response)


@strategies_blueprint.route('add', methods=['GET', 'POST'])
def addStrategy():
    paperTrade = True
    stratName = None
    form = AddStratForm()

    if form.validate_on_submit():
        paperTrade = form.paperTrade.data
        stratName = form.stratName.data
        # TODO add stock option in form
        try:
            strategiesHandler.addStrategy(
                MonthStraddle(symbolsHandler.get('nifty50'), symbolsHandler.get('indiavix'), symbolsHandler,
                              paperTrade))
        except Exception as e:
            logger.add_log(LogType.ERROR, f"Failed to add strategy '{stratName}' with error: {e}")
        return redirect(url_for('server.strategies.getRunningStrategies'))

    return render_template('add_strat.html', stratName=stratName, paperTrade=paperTrade, form=form)


@strategies_blueprint.route('positions/<stratID>')
def position(stratID):
    strategy = strategiesHandler.getStrategy(stratID)
    if strategy is None:
        return None

    positionsIntro = []
    for pos in strategy.positions.values():
        positionsIntro.append(pos.getIntro(json=True))

    realized, unrealized = strategy.getPnL()

    stratJSON = {
        'strategyName': strategy.strategyName,
        'id': strategy.id,
        'paperTrade': strategy.paperTrade,
        'realizedPnL': realized,
        'unrealized': unrealized,
        'positions': positionsIntro
    }
    return render_template('strategy_info.html', stratjson=stratJSON)

@strategies_blueprint.route('activeSymbols')
def activeSymbols():
    symbolsList = []
    lstSymbolsResponse = symbolsHandler.getAll()
    for objSymbol in lstSymbolsResponse.values():
        symbolsList.append([objSymbol.ticker, objSymbol.ltp, dateStringFromTimestamp(objSymbol.time)])

    return render_template('active_symbols.html', symbols = symbolsList)