#!/usr/bin/env python
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# kdb lib
from qpython import qconnection
from qpython.qtype import QException
from qpython.qconnection import MessageType
from qpython.qcollection import QDictionary

import os, sys
import pandas as pd
import numpy as np
import json
import configparser
from collections import defaultdict


import alpaca_trade_api as tradeapi
import threading
import time
import datetime
from threading import Lock


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


# global properties
config = {}

# config utils
def load_app_config(config_file):
    try:
        appconfig = configparser.ConfigParser()
        base_dir = os.path.abspath(os.path.dirname('__file__'))
        appconfig.read(os.path.join(base_dir, config_file))

        print('==================')
        for c in appconfig['DEFAULT']:
            config[c] = appconfig['DEFAULT'][c]

        print("DEFAULT configs: ", config)
    except Exception as e:
        raise Exception('Error init/start Services. %s' %e)



### position management ###

pos = {}

def get_account_info():
    account = api.get_account()
    print(f'0000: {account}')

    # open orders
    orders = api.list_orders(status="open")
    for order in orders:
        print(f'xxxx ord: {order}')

    positions = api.list_positions()
    for position in positions:
        print(f'$$$$ pos: {position}')


# Submit an order if quantity is above 0.
def submitOrder(qty, stock, side, resp):
    if(qty > 0):
        try:
            api.submit_order(stock, qty, side, "market", "day")
            print("Market order of | " + str(qty) + " " + stock + " " + side + " | completed.")
            resp.append(True)
        except:
            print("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
            resp.append(False)
    else:
        print("Quantity is 0, order of | " + str(qty) + " " + stock + " " + side + " | not completed.")
        resp.append(True)


def send_basic_order(api, sym, qty, side):
    qty = int(qty)
    if(qty == 0):
        return

    q2 = 0
    try:
        position = api.get_position(sym)
        curr_pos = int(position.qty)
        if((curr_pos + qty > 0) != (curr_pos > 0)):
            q2 = curr_pos
            qty = curr_pos + qty
    except BaseException:
        pass

    try:
        if q2 != 0:
            api.submit_order(sym, abs(q2), side, "market", "gtc")
            try:
                api.submit_order(sym, abs(qty), side, "market", "gtc")
            except Exception as e:
                print(
                    f"Error: {str(e)}. Order of | {abs(qty) + abs(q2)} {sym} {side} | partially sent ({abs(q2)} shares sent).")
                return False
        else:
            api.submit_order(sym, abs(qty), side, "market", "gtc")
        print(f"Order of | {abs(qty) + abs(q2)} {sym} {side} | submitted.")
        return True
    except Exception as e:
        print(
            f"Error: {str(e)}. Order of | {abs(qty) + abs(q2)} {sym} {side} | not sent.")
        return False


def initQ():
    # initialize connection
    q.open()

    print(q)
    print('IPC version: %s. Is connected: %s' % (q.protocol_version, q.is_connected()))


def update_signals_count(signals_count_map, signals_count_dict, signals_df):
    #### update signals_rank -- $$$ IMPL
    for i, row in signals_df.iterrows():
        
        if signals_count_dict[row['sym']] == 0:
            signals_count_dict[row['sym']] += 1
            signals_count_map[row['sym']] = row
        else:
            prev = signals_count_map[row['sym']]
            
            if prev['qtm'] != row['qtm']:
                signals_count_dict[row['sym']] += 1

    print(f'$$$$: signals_count_dict: {signals_count_dict}')


#### stats module 
def rebase_series(series):
    return (series / series.iloc[0]) * 100


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    signals_hist = []
    signals_hist_df = pd.DataFrame()

    long_signals_count_dict = defaultdict(int)
    long_signals_count_map = {}
    short_signals_count_dict = defaultdict(int)
    short_signals_count_map = {}

    while True:
        #query = "0!update l2dv:open-2*dv, r2dv:open+2*dv, qtm:string qtm, atr:mx-mn  from select last qtm, n:count i, open:first price, mn:min price, mu:avg price, md:med price, mx:max price, dv:sdev price, vwap:size wavg price, close:last price, chg:last deltas price, volume:sum size by sym from trade"
        stats = q("get_summary2[]")
        stats['count'] = count

        #print('xxxx: stats -')
        #print(stats.tail())
        stats_json = stats.to_json(orient='records')
        #print(stats_json)
        #stats_html = stats.to_html(classes="table table-hover table-bordered table-striped",header=True)

        # APPLY signals and send orders to Alpaca, update real-time postions
        #print(stats.dtypes)
        signal_long = stats.loc[(stats.n>=30) & (stats.close==stats.mx) & (stats.close>stats.open)].copy()
        #signal_long = stats.loc[(stats.n<1000)].copy() # testing mode
        #, ['sym', 'qtm', 'n', 'open', 'mn', 'mu', 'md', 'mx', 'vwap', 'close', 'dv', 'atr']]
        signal_long['signal'] = 'Mom_Long'

        # send to order event queue -
        if len(signal_long) > 0:
            print('$$$$ got mom LONG signals: (send to Alexa) ')
            #print(signal_long)
            # check if any active positions -
            update_signals_count(long_signals_count_map, long_signals_count_dict, signal_long)
        
        signals_short = stats.loc[(stats.n>=30) & (stats.close==stats.mn) & (stats.close<stats.open)].copy()
        signals_short['signal'] = 'Mom_Short'

        if len(signals_short) > 0:
            print('$$$$ got SHORT signals: (send to Alexa) ')
            #print(signals_short)
            update_signals_count(short_signals_count_map, short_signals_count_dict, signals_short)

        # merge Long/Short signals -
        signals_df = pd.concat([signal_long, signals_short])

        if len(signals_df) > 0:
            signals_ui = signals_df[['count', 'sym', 'qtm', 'n', 'open', 'mn', 'mu', 'md', 'mx', 'vwap', 'close', 'dv', 'atr', 'signal']]
            print('xxxx signals_ui: ')
            print(signals_ui)

            # #### update signals_rank -- $$$ IMPL
            # for i, row in signals_df.iterrows():
                
            #     if signals_count_dict[row['sym']] == 0:
            #         signals_count_dict[row['sym']] += 1
            #         signals_count_map[row['sym']] = row
            #     else:
            #         prev = signals_count_map[row['sym']]
                    
            #         if prev['qtm'] != row['qtm']:
            #             signals_count_dict[row['sym']] += 1

            # print(f'$$$$: signals_count_dict: {signals_count_dict}')

            signals_hist.append(signals_ui)
            # keep just the last 5 signals
            if len(signals_hist) > 5:
                signals_hist = signals_hist[-5:]

            # display only the last n signals -        
            signals_hist_df = pd.concat(signals_hist).sort_values(by='count', ascending=False)
            print('xxxx signal_hist_df')
            print(signals_hist_df)

        # last 5 signals
        signals_html = signals_hist_df.to_html(classes="table table-hover table-bordered table-striped",header=True)
        
        # latest signals -
        signals_tbl = signals_df[['id', 'qtm', 'src', 'sym', 'price', 'volume', 'ps', 'tick', 'signal']]
        signals_json = signals_tbl.to_json(orient='records')
        #print('$$$$ signals_json')
        #print(signals_json)

        # minute price series -
        #query = '0!select data:100*price % first price by name:sym  from select last price by sym, qtm.minute from trade where sym like "XL*"'
        #prices_df = q(query)
        #prices_json = prices_df.to_json(orient='records')
        #print('xxxx prices_json:')
        #print(prices_json)


        # publish kdb upd time:
        tm = q("max exec qtm from select by sym from trade")
        print(f'count: {count}, qtime: {tm}')

        long_signals_rank = sorted(long_signals_count_dict.items(), key=lambda x: x[1], reverse=True) 
        short_signals_rank = sorted(short_signals_count_dict.items(), key=lambda x: x[1], reverse=True)

        socketio.emit('my_response',
                        {'count': count,
                        'time':str(tm).split(" ")[0],

                        'signals_rank_long': str(long_signals_rank),
                        'signals_rank_short': str(short_signals_rank),
                        'signals_html': signals_html,
                        'signal': signals_json,                       
                        'summary': stats_json,

                        #'prices_series': prices_json,

                        }, namespace='/test')


        # set update period
        socketio.sleep(10)
        count += 1



@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    # enrich this message - do a stock price update banner -    
    emit('my_pong', {'data': 'kdb_time', 'hehe': 'haha'})



@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

    # initQ
    initQ()

    emit('my_response', {'data': 'Connected, Q is ready to publish data...', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


### API info -
load_app_config('app.config')

API_KEY = config['key_id']
API_SECRET = config['secret_key']
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"
api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

#get_account_info()
# send test order -


print('xxxx connect to Kdb...')

# create connection object
#q = qconnection.QConnection(host='localhost', port=5001, pandas=True)
q = qconnection.QConnection(host='aq101', port=6002, pandas=True)


#### main ####
if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
