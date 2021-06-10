import logging
from os import access
from pprint import pprint
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import yfinance as yf
import datetime
from datetime import date
import time

logging.basicConfig(level=logging.DEBUG)

api_key = "sb88rkw84xfd2fg2"
api_secret = "1sbeha4b7vlcgnuo5fhbblgo4k9skey3"

time_start = time.time()

def generate_access_token(request_token):
    kite = KiteConnect(api_key=api_key)

    # Redirect the user to the login url obtained from kite.login_url(), and receive the request_token from the
    # registered redirect url after the login flow.Once you have the request_token, obtain the access_tokenas follows.

    data = kite.generate_session(request_token, api_secret=api_secret)
    return data["access_token"]


kite = KiteConnect(api_key=api_key)
# print(kite.login_url())
# request_token=input('Enter request token: ')
# access_token=generate_access_token(request_token)
# print(access_token)
access_token = "edOAfknGHQ9Xd7QffTjm0mu7RoIhkhB1"
kite.set_access_token(access_token)


# 321283:{'name': 'CDS:USDINR21MAYFUT', 'exp_date': date(2021,5,27)}, 270076166:{'name': 'BCD:USDINR21MAYFUT', 'exp_date': date(2021,5,27)},
instrument_dic = {
    412675: {"name": "CDS:USDINR21JUNFUT", "exp_date": date(2021, 6, 28)},
    270351622: {"name": "BCD:USDINR21JUNFUT", "exp_date": date(2021, 6, 28)},
    709379: {"name": "CDS:USDINR21JULFUT", "exp_date": date(2021, 7, 28)},
    270593798: {"name": "BCD:USDINR21JULFUT", "exp_date": date(2021, 7, 28)},
    1893123: {"name": "CDS:USDINR21AUGFUT", "exp_date": date(2021, 8, 27)},
    270992646: {"name": "BCD:USDINR21AUGFUT", "exp_date": date(2021, 8, 27)},
    346627: {"name": "CDS:USDINR21SEPFUT", "exp_date": date(2021, 9, 28)},
    271336454: {"name": "BCD:USDINR21SEPFUT", "exp_date": date(2021, 9, 28)},
    417027: {"name": "CDS:USDINR21OCTFUT", "exp_date": date(2021, 10, 27)},
    271672838: {"name": "BCD:USDINR21OCTFUT", "exp_date": date(2021, 10, 27)},
    830467: {"name": "CDS:USDINR21NOVFUT", "exp_date": date(2021, 11, 26)},
    272085766: {"name": "BCD:USDINR21NOVFUT", "exp_date": date(2021, 11, 26)},
    363779: {"name": "CDS:USDINR21DECFUT", "exp_date": date(2021, 12, 29)},
    272375558: {"name": "BCD:USDINR21DECFUT", "exp_date": date(2021, 12, 29)},
    289539: {"name": "CDS:USDINR22JANFUT", "exp_date": date(2022, 1, 27)},
    273521414: {"name": "BCD:USDINR22JANFUT", "exp_date": date(2022, 1, 27)},
    2613763: {"name": "CDS:USDINR22FEBFUT", "exp_date": date(2022, 2, 24)},
    274296838: {"name": "BCD:USDINR22FEBFUT", "exp_date": date(2022, 2, 24)},
    455427: {"name": "CDS:USDINR22MARFUT", "exp_date": date(2022, 3, 29)},
    275053318: {"name": "BCD:USDINR22MARFUT", "exp_date": date(2022, 3, 29)},
    299523: {"name": "CDS:USDINR22APRFUT", "exp_date": date(2022, 4, 27)},
    275854598: {"name": "BCD:USDINR22APRFUT", "exp_date": date(2022, 4, 27)},
}

# instrument_dic = {
#     270351622: {"name": "BCD:USDINR21JUNFUT", "exp_date": date(2021, 6, 28)},
# }

instrument_tokens = list(instrument_dic.keys())
for e in instrument_tokens:
    instrument_dic[e]["order_id_sell"] = False
    instrument_dic[e]["order_id_buy"] = False


def place_future_orders(ticks):
    data = yf.download(tickers="INR=X", period="15m", interval="1m")
    if len(data.index) > 0:
        current_rate = data.iloc[-1]["Close"]
    else:
        return
    current_date = datetime.datetime.now().date()

    discount_rate_sell = 0.065
    discount_rate_buy = 0.035
    for e in ticks:
        token = e["instrument_token"]
        instrument = instrument_dic[token]
        instrument_info = instrument_dic[token]["name"].split(":")
        if instrument_info[0] == "CDS":
            exchange = "CDS"
        else:
            exchange = "BCD"
        tradingsymbol = instrument_info[1]

        spot_price_sell = (
            current_rate * ( 1 + discount_rate_sell * (instrument["exp_date"] - current_date).days / 365 ) + 0.2
        )
        spot_price_buy = ( 
            current_rate * ( 1 + discount_rate_buy * (instrument["exp_date"] - current_date).days / 365 ) - 0.2
        )

        spot_price_sell = round(spot_price_sell / 0.0025) * 0.0025
        spot_price_buy = round(spot_price_buy / 0.0025) * 0.0025

        # debug depth
        # print('\nMarket Sell Depth: ',e["depth"]["sell"],'/n')
        # print('\nMarket Buy Depth: ',e["depth"]["buy"],'/n')

        if e["depth"]["sell"][0]["price"] == 0:
            sell_price = round(spot_price_sell + 2, 4)
        else:
            depth_price = e["depth"]["sell"][0]["price"]
            if exchange == 'BCD':
                depth_price = depth_price/100
            sell_price = round(
                max(depth_price - 0.0025, spot_price_sell), 4
            )

        if e["depth"]["buy"][0]["price"] == 0:
            buy_price = round(spot_price_buy - 2, 4)
        else:
            depth_price = e["depth"]["buy"][0]["price"]
            if exchange == 'BCD':
                depth_price = depth_price/100
            buy_price = round(
                min(depth_price + 0.0025, spot_price_buy), 4
            )

        print('\nPlacing orders for: ',current_rate, buy_price, sell_price, tradingsymbol, exchange)

######  Placing Sell Orders
        place_sell_order = True
        if instrument["order_id_sell"] != False:
            try:
                order = kite.order_history(instrument["order_id_sell"])
            except Exception as e:
                print("An exception occured during fetching order", e)
                place_sell_order = False

            if order[-1]["status"] == "OPEN":
                place_sell_order = False
                order_id_before = instrument["order_id_sell"]
                try:
                    if order[-1]["price"] != sell_price:
                        order_id = kite.modify_order(
                            order_id=instrument["order_id_sell"],
                            variety=kite.VARIETY_REGULAR,
                            quantity=1,
                            price=sell_price,
                            order_type=kite.ORDER_TYPE_LIMIT,
                            validity=kite.VALIDITY_DAY,
                            disclosed_quantity=1,
                        )
                        print("Order Modified")
                        instrument_dic[token]["order_id_sell"] = order_id
                except Exception as e:
                    print("An exception occured during modyfying order", e)
                    instrument_dic[token]["order_id_buy"] = order_id_before

        if place_sell_order == True:
            order_id_before = instrument["order_id_sell"]
            try:
                order_id = kite.place_order(
                    variety=kite.VARIETY_REGULAR,
                    tradingsymbol=tradingsymbol,
                    exchange=exchange,
                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                    quantity=1,
                    order_type=kite.ORDER_TYPE_LIMIT,
                    product=kite.PRODUCT_NRML,
                    price=sell_price,
                    disclosed_quantity=1,
                    validity=kite.VALIDITY_DAY,
                )
                instrument_dic[token]["order_id_sell"] = order_id
                print("Order Placed")
            except Exception as e:
                print("An exception occured during placing order", e)
                instrument_dic[token]["order_id_buy"] = order_id_before

######  Placing Buy Orders
        place_buy_order = True

        if instrument["order_id_buy"] != False:
            try:
                order = kite.order_history(instrument["order_id_buy"])
            except Exception as e:
                print("An exception occured during fetching order: ", e)
                place_buy_order = False

            if order[-1]["status"] == "OPEN":
                place_buy_order = False
                order_id_before = instrument["order_id_buy"]
                if order[-1]["price"] != buy_price:
                    try:
                        order_id = kite.modify_order(
                            order_id=instrument["order_id_buy"],
                            variety=kite.VARIETY_REGULAR,
                            quantity=1,
                            price=buy_price,
                            order_type=kite.ORDER_TYPE_LIMIT,
                            validity=kite.VALIDITY_DAY,
                            disclosed_quantity=1,
                        )
                        print("Order Modified")
                        instrument_dic[token]["order_id_buy"] = order_id
                    except Exception as e:
                        print("An exception occured during modyfying order", e)
                        instrument_dic[token]["order_id_buy"] = order_id_before

        if place_buy_order == True:
            order_id_before = instrument["order_id_buy"]
            try:
                order_id = kite.place_order(
                    variety=kite.VARIETY_REGULAR,
                    tradingsymbol=tradingsymbol,
                    exchange=exchange,
                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                    quantity=1,
                    order_type=kite.ORDER_TYPE_LIMIT,
                    product=kite.PRODUCT_NRML,
                    price=buy_price,
                    disclosed_quantity=1,
                    validity=kite.VALIDITY_DAY,
                )
                print("Order Placed")
                instrument_dic[token]["order_id_buy"] = order_id
            except Exception as e:
                print("An exception occured during placing order", e)
                instrument_dic[token]["order_id_buy"] = order_id_before

    return True


# Initialise
kws = KiteTicker(api_key, access_token)


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    # logging.debug("Ticks: {}".format(ticks))
    # pprint(ticks)
    place_future_orders(ticks)
    # print('\n')


def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    # ws.subscribe([412675])
    ws.subscribe(instrument_tokens)

    # Set RELIANCE to tick in `full` mode.
    # ws.set_mode(ws.MODE_LTP, [412675])
    ws.set_mode(ws.MODE_FULL, instrument_tokens)


def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    # if time.time()-time_start > 180:
    #     ws.stop()
    pass


# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect()
