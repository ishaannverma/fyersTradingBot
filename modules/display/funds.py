from modules.login.login_route import fyers_model_class_obj
from flask import Blueprint
import pandas as pd

funds_blueprint = Blueprint('funds', __name__, url_prefix='/funds')

@funds_blueprint.route('')
def funds():
    rsp = fyers_model_class_obj.getModel().funds()
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