from modules.login.route import fyers_model
from flask import Blueprint
import pandas as pd

funds_blueprint = Blueprint('funds', __name__, url_prefix='/funds')

@funds_blueprint.route('')
def funds():
    rsp = fyers_model.model.funds()
    if rsp['code'] == 200:
        fund_limits =  rsp['fund_limit']
        data = []
        cols = ['Type', 'Funds']
        for limit in fund_limits:
            row = [limit['title'], limit['equityAmount']]
            data.append(row)

        return pd.DataFrame(data, columns=cols).to_html()
    else:
        return 'problem'