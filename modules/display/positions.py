from modules.login.route import fyers_model
from flask import Blueprint
import pandas as pd

positions_blueprint = Blueprint('positions', __name__, url_prefix='/positions')

@positions_blueprint.route('')
def positions():
    rsp = fyers_model.model.positions()
    if rsp['code'] == 200:
        positions =  rsp['netPositions']
        data = []
        cols = ['Side', 'Symbol', 'NetQty', 'Average', 'LTP', 'PL']
        for pos in positions:
            side = "BUY" if pos['side']==1 else "SELL"
            row = [side, pos['symbol'],pos['netQty'], pos['avgPrice'], pos['ltp'], pos['pl']]
            data.append(row)

        return pd.DataFrame(data, columns=cols).to_html()
    else:
        return 'problem'