from modules.login.login_route import fyers_model_class_obj
from flask import Blueprint
import pandas as pd

positions_blueprint = Blueprint('positions', __name__, url_prefix='/positions')


@positions_blueprint.route('')
def positions():
    status, response = fyers_model_class_obj.positions()
    if status is True:
        positions = response['netPositions']
        data = []
        cols = ['Side', 'Symbol', 'NetQty', 'Average', 'LTP', 'PL']
        for pos in positions:
            side = "BUY" if pos['side'] == 1 else "SELL"
            row = [side, pos['symbol'], pos['netQty'], pos['avgPrice'], pos['ltp'], pos['pl']]
            data.append(row)

        return pd.DataFrame(data, columns=cols).to_html()
    else:
        return f'problem {response}'
