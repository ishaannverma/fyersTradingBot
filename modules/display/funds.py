from modules.login.login_route import fyers_model_class_obj
from flask import Blueprint
import pandas as pd

funds_blueprint = Blueprint('funds', __name__, url_prefix='/funds')


@funds_blueprint.route('')
def funds():
    status, response = fyers_model_class_obj.funds()
    if status is True:
        fund_limits = response['fund_limit']
        data = []
        cols = ['Type', 'Funds']
        for limit in fund_limits:
            row = [limit['title'], limit['equityAmount']]
            data.append(row)

        return pd.DataFrame(data, columns=cols).to_html()
    else:
        return f'problem {response}'
