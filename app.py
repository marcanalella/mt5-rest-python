# pip install MetaTrader5
# pip install --upgrade MetaTrader5
import MetaTrader5 as mt5
from flask import Flask, request
import pandas as pd

import constants

app = Flask(__name__)

ea_magic_number = 1000


@app.post('/signal')
def signal():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    signal = request.get_json()
    pair = signal["pair"]
    action = signal["action"]

    if not mt5.initialize(constants.path):
        print("initialize() failed")
        mt5.shutdown()
        return {"error": "MT5 Terminal initialize() failed"}, 500

    if mt5.login(constants.login, constants.password, constants.server):
        print("logged in succesffully")
        account_info_dict = mt5.account_info()._asdict()
        account_info_df = pd.DataFrame(account_info_dict, index=[0])
        print("Profit:", account_info_df["profit"].iloc[0])
        print("Equity:", account_info_df["equity"].iloc[0])
        print("Margin:", account_info_df["margin"].iloc[0])
        print("Margin Free:", account_info_df["margin_free"].iloc[0])


    else:
        print("login failed, error code: {}".format(mt5.last_error()))
        return {"error": "login failed"}, 500

    # request connection status and parameters
    print(mt5.terminal_info())
    # get data on MetaTrader 5 version
    print(mt5.version())

    open_position(pair, action, constants.size, 50, 100)
    return None


def open_position(pair, order_type, size, tp_distance=None, stop_distance=None):
    global order, price, sl, tp
    symbol_info = mt5.symbol_info(pair)
    if symbol_info is None:
        print(pair, "not found")
        return {"error": "Symbol not found "}, 500

    if not symbol_info.visible:
        print(pair, "is not visible, trying to switch on")
        if not mt5.symbol_select(pair, True):
            print("symbol_select({}}) failed, exit", pair)
            return {"error": "symbol_select({}}) failed, exit "}, 500

    print(pair, "found!")

    point = symbol_info.point

    if order_type == "BUY":
        order = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(pair).ask
        if stop_distance:
            sl = price - (stop_distance * point)
        if tp_distance:
            tp = price + (tp_distance * point)

    if order_type == "SELL":
        order = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(pair).bid
        if stop_distance:
            sl = price + (stop_distance * point)
        if tp_distance:
            tp = price - (tp_distance * point)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pair,
        "volume": float(size),
        "type": order,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": ea_magic_number,
        "comment": "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to send order :(")
        return {"error": "Failed to send order :( "}, 500
    else:
        print("Order successfully placed!")
        return {"success": "Order successfully placed! "}, 201


if __name__ == '__main__':
    app.run()
