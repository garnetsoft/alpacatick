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
from datetime import datetime
import traceback


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


def initQ():
    # initialize connection
    q.open()

    print(q)
    print('IPC version: %s. Is connected: %s' % (q.protocol_version, q.is_connected()))


### position management ###

acct_balance = []


def get_account_info():
    account = api.get_account()
    print(f'0000: {account}')

    # open orders
    orders = api.list_orders(status="open")
    for order in orders:
        print(f'xxxx ord: {order}')

    positions = api.list_positions()
    notional = 0.0
    for i, position in enumerate(positions):
        print(f'$$$$ {i} pos: {position}')
        notional += float(position.market_value)
    print(f'$$$$ total USD: {notional}')


def get_live_positions():
    pos_list = []

    positions = api.list_positions()
    notional = 0.0
    if len(positions) == 0:
        print(f'xxxx no positions')
    else:
        for i, pos in enumerate(positions):
            print(f'$$$$ {i} pos: {pos.symbol}, qty: {pos.qty},  market_value: {pos.market_value}, unrealized_pnl: {pos.unrealized_pl}, side: {pos.side}, \
                avg_entry_price:{pos.avg_entry_price}, current_price: {pos.current_price}' )

            pos_list.append([pos.symbol, pos.qty, pos.market_value, pos.unrealized_pl, pos.side, pos.avg_entry_price, pos.current_price])
            notional += float(pos.market_value)

        print(f'$$$$ total USD: {notional}')

    pos_df = pd.DataFrame(pos_list, columns=['symbol', 'qty', 'market_value', 'unrealized_pn', 'side', 'avg_entry_price', 'current_price'])

    return pos_df


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
    if isinstance(sym, bytes):
        sym = sym.decode('utf-8')

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
                print(f"Error: {str(e)}. Order of | {abs(qty) + abs(q2)} {sym} {side} | partially sent ({abs(q2)} shares sent).")
                return False
        else:
            api.submit_order(sym, abs(qty), side, "market", "gtc")

        print(f"Order of | {abs(qty) + abs(q2)} {sym} {side} | submitted.")
        #pos[sym] = [datetime.now(), sym, qty, side, "market", "gtc"]
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}. Order of | {abs(qty) + abs(q2)} {sym} {side} | not sent.")
        # publish as a Bootstrap alert
        return False


def send_entry_order(sym, size, side):
    if isinstance(sym, bytes):
        sym = sym.decode('utf-8')

    status = send_basic_order(api, sym, size, side)
    print(f'$$$$ entry order: {sym}, {side}, {size} executed. status: {status}')
    return None


def send_exit_order(sym, size, side):
    if isinstance(sym, bytes):
        sym = sym.decode('utf-8')

    status = send_basic_order(api, sym, size, side)
    print(f'$$$$ exit order: {sym}, {side}, {size} executed. status: {status}')
    return None



#### stats module 
def rebase_series(series):
    return (series / series.iloc[0]) * 100



### app routes -
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test2')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test2')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('my_ping', namespace='/test2')
def ping_pong():
    # enrich this message - do a stock price update banner -    
    emit('my_pong', {'data': 'kdb_time', 'hehe': 'haha'})


### THIS RESETS WHEN BROWSER REFRESHES -
@socketio.on('connect', namespace='/test2')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

    # initQ
    initQ()

    # send data
    emit('my_response', {'data': 'Connected, Q is ready to publish data...', 'count': 0})


@socketio.on('disconnect', namespace='/test2')
def test_disconnect():
    print('Client disconnected', request.sid)



## ajax callback to provide minute bar data
@app.route('/sectorbar')
def get_sector_bar():
    print(f'xxxx get_sector_bar {q}, {q.is_connected()}')

    if not q.is_connected():
        return {'error:': 'not connected to kdb'}

    s = '`SPY`XLK`XLU`XLY`XLP`XLF`XLI`XLV`XLB`XLE`XLC`XLRE'
    query = f'exec ({s})#sym!price by tm:minute from 0!select last price by sym, 1 xbar qtm.minute from trade where sym in {s}, qtm.minute>=?[.z.T>=13:35;13:30;13:01]'        
    print(f'xxxx get_sector_bar query: {query}')
    
    td = datetime.today().date().strftime('%m/%d/%Y')

    try:        
        df = q(query)
        df = rebase_series(df.dropna())
        data_json = [{"name": s, "data": list(map(list, zip([int(pd.to_datetime(datetime.strptime("{} {}".format(td, str(x)[-8:]), '%m/%d/%Y %H:%M:%S')).value / 1000000) for x in mdata.index], mdata))) } for s, mdata in df.items()]
        #print(f'XXXX get_sector_bar: {data_json}')

        return {'msg_type': 'minute_bar', 'minute_data': json.dumps(data_json) }

    except Exception as e:
        print(f'ERROR: in querying Kdb get_sector_bar, {e}, query: {query}')
        traceback.print_exc(file=sys.stdout)

    return {'error:': 'kdb data not available.', 'query': query}


@app.route('/sectorstats')
def compute_sector_stats():
    print(f'xxxx compute_sector_stats {q}, {q.is_connected()}')

    if not q.is_connected():
        return {'error:': 'not connected to kdb'}
    
    s = '`SPY`XLK`XLU`XLY`XLP`XLF`XLI`XLV`XLB`XLE`XLC`XLRE'
    query = f'exec ({s})#sym!price by tm:minute from 0!select last price by sym, 1 xbar qtm.minute from trade where sym in {s}, qtm.minute>=?[.z.T>=13:35;13:30;13:01]'
    #query = f'exec ({s})#sym!price by tm:qtm from 0!select price:last lastSalePrice by sym:symbol, qtm:lastUpdatedz.minute from iextops where symbol in {s}'

    print(f'xxxx compute_sector_stats query: {query}')

    try:        
        df = q(query)
        #df = rebase_series(df.bfill()).dropna()
        df = rebase_series(df.bfill().ffill())
        df_stats = df.describe()

        df_stats.loc['open'] = df.iloc[0]
        df_stats.loc['close'] = df.iloc[-1]
        df_stats.loc['return'] = df_stats.loc['close'] - 100
        #df_stats.loc['retdv'] = (df_stats.loc['close'] - 100) / df_stats.loc['std']
        df_stats.loc['sharpe'] = np.divide(df_stats.loc['mean']-100, df_stats.loc['std'])

        stats_data = [{'name': s, 'x': data['sharpe'], 'y': data['return'], 'z': data['std'], 'country': s} for s, data in  df_stats.items()]
        #print(f'XXXX stats_data: {stats_data}')

        # relative to SPY -
        spy = df_stats.loc[:,['SPY']]
        df_stats.loc['return2'] = df_stats.loc['close'] - np.mean(spy.loc['close'])
        df_stats.loc['sharpe2'] = np.divide(df_stats.loc['return'] - np.mean(spy.loc['return']), df_stats.loc['std'])
        stats_data2 = [{'name': s, 'x': data['sharpe2'], 'y': data['return2'], 'z': data['std'], 'country': s} for s, data in  df_stats.items()]

        stats_series = [{'group':'Actual', 'data': stats_data}, {'group':'Relative', 'data': stats_data2}]

        return {'msg_type': 'stats_data', 'stats_data': json.dumps(stats_series) }

    except Exception as e:
        print(f'ERROR: in querying Kdb compute_sector_stats, {e}, query: {query}')
        traceback.print_exc(file=sys.stdout)

    return {'error:': 'kdb data not available.', 'query': query}


@app.route('/statsbar2')
def compute_minute_stats2():
    print(f'xxxx compute_minute_stats2 {q}, {q.is_connected()}')

    if not q.is_connected():
        return {'error:': 'not connected to kdb'}
    
    s = '`SPY`MMM`AXP`AAPL`BA`CAT`CVX`CSCO`KO`DOW`XOM`GS`HD`IBM`INTC`JNJ`JPM`MCD`MRK`MSFT`NKE`PFE`PG`RTX`TRV`UNH`VZ`V`WMT`WBA`DIS'
    #s = '`SPY`AAPK`GS`XOM`TSLA'
    print(f'xxxx compute_minute_stats2: {s}')

    try:
        # query = f'exec ({s})#sym!price by tm:minute from 0!select last price by sym, 1 xbar qtm.minute from trade where sym in {s}, qtm.minute>=?[.z.T>=13:35;13:30;13:01]'
        #query = f'exec {s}#sym!close by tm:"T"$minute from intraday where sym in {s}'
        query = f'exec ({s})#sym!price by tm:qtm from 0!select price:last lastSalePrice by sym:symbol, qtm:lastSaleTimez.minute from iextops where lastSaleTimez.minute>=13:30, symbol in {s}'
        print(f'xxxx statsbar2 query: {query}')
        
        df = q(query)
        #df = rebase_series(df.bfill()).dropna()
        df = df.replace(0, np.nan).bfill().ffill()
        df = rebase_series(df)
        df_stats = df.describe()

        df_stats.loc['open'] = df.iloc[0]
        df_stats.loc['close'] = df.iloc[-1]
        df_stats.loc['return'] = df_stats.loc['close'] - 100
        #df_stats.loc['retdv'] = (df_stats.loc['close'] - 100) / df_stats.loc['std']
        df_stats.loc['sharpe'] = np.divide(df_stats.loc['mean']-100, df_stats.loc['std'])

        spy = df_stats.loc[:,['SPY']]
        df_stats.loc['return2'] = df_stats.loc['close'] - np.mean(spy.loc['close'])
        df_stats.loc['sharpe2'] = np.divide(df_stats.loc['return'] - np.mean(spy.loc['return']), df_stats.loc['std'])

        df_stats2 = df_stats.T
        df_g1 = df_stats2.loc[df_stats2.sharpe2 > 0] # check both sharpe2 and return2 
        df_g2 = df_stats2.loc[df_stats2.sharpe2 <= 0]

        stats_data = [{'name': s, 'x': data['sharpe'], 'y': data['return'], 'z': data['std'], 'country': s} for s, data in  df_g1.iterrows()]
        stats_data2 = [{'name': s, 'x': data['sharpe2'], 'y': data['return2'], 'z': data['std'], 'country': s} for s, data in  df_g2.iterrows()]
        stats_series = [{'group':'Actual', 'data': stats_data}, {'group':'Relative', 'data': stats_data2}]

        return {'msg_type': 'stats_data', 'stats_data': json.dumps(stats_series) }

    except Exception as e:
        print(f'ERROR: in querying Kdb compute_minute_stats2, {e}, query: {query}')
        traceback.print_exc(file=sys.stdout)

    return {'error:': 'kdb data not available.', 'query': query}


## ajax callback to provide minute bar data
@app.route('/minutebar')
def get_minute_bar():
    print(f'xxxx minutebar {q}, {q.is_connected()}')

    # create minute bar series -
    # exec (`SPY`AAPL)#sym!price by mm:minute from 0!select last price by sym, 5 xbar qtm.minute from trade where sym in `SPY`AAPL
    # data_json = [{"name": s, "data": list(map(list, zip([datetime.strptime(str(x)[-8:], '%H:%M:%S') for x in mdata.index], mdata))) } for s, mdata in df.items()]

    if not q.is_connected():
        return {'error:': 'not connected to kdb'}
    
    s = '`SPY`MMM`AXP`AAPL`BA`CAT`CVX`CSCO`KO`DOW`XOM`GS`HD`IBM`INTC`JNJ`JPM`MCD`MRK`MSFT`NKE`PFE`PG`RTX`TRV`UNH`VZ`V`WMT`WBA`DIS'
    print(f'xxxx querying minutebar: {s}')
    td = datetime.today().date().strftime('%m/%d/%Y')
    #dt2 = datetime.strptime("{} {}".format(td, str(tm)[-8:]), "%m/%d/%Y %H:%M:%S")

    #query = f'exec ({s})#sym!price by tm:minute from 0!select last price by sym, 1 xbar qtm.minute from trade where sym in {s}, qtm.minute>=?[.z.T>=13:35;13:30;13:01]'
    #query = f'select by 30 xbar tm:tm.minute from  exec {s}#sym!close by tm:"T"$minute from intraday where sym in {s}'
    query = f'exec ({s})#sym!price by tm:qtm from 0!select price:last lastSalePrice by sym:symbol, qtm:lastSaleTimez.minute from iextops where  lastSaleTimez.minute>=13:30, symbol in {s}'
    print(f'xxxx minutebar query: {query}')

    try:
        df = q(query)
        print('xxxx minute_df:')
        #print(df.head())
        df = df.replace(0, np.nan).bfill().ffill()
        #df = df.replace(0, np.nan).ffill()
        df = rebase_series(df)
        print('xxxx minute_df rebased:')
        print(df.tail())

        #data_json = [{"name": s, "data": list(map(list, zip([datetime.strptime(str(x)[-8:], '%H:%M:%S') for x in mdata.index], mdata))) } for s, mdata in df.items()]
        data_json = [{"name": s, "data": list(map(list, zip([int(pd.to_datetime(datetime.strptime("{} {}".format(td, str(x)[-8:]), '%m/%d/%Y %H:%M:%S')).value / 1000000) for x in mdata.index], mdata))) } for s, mdata in df.items()]
        #print(f'XXXX minute_data: {data_json}')

        return {'msg_type': 'minute_bar', 'minute_data': json.dumps(data_json) }

    except Exception as e:
        print(f'ERROR: in querying Kdb get_minute_bar, {e}, query: {query}')
        traceback.print_exc(file=sys.stdout)

    return {'error:': 'kdb data not available.', 'query': query}


@app.route('/tickupdate')
def get_tick_update():
    print(f'xxxx get_tick_update {q}, {q.is_connected()}')

    if not q.is_connected():
        return {'error:': 'not connected to kdb'}
    
    try:
        query = f'0!update dftp:"t"$"z"$(qtm-"z"$wstm), dftz:"t"$(.z.p-wstm), kdbtime:.z.z, wstz:"z"$wstm from update wstm:"p"$1970.01.01D+tms from select by sym from trade where sym in `SPY`AAPL'
        #query = f'0!update wstz:"z"$wstm, kdbtime:.z.z from update wstm:"p"$1970.01.01D+1000000*lastSaleTime, qtm:"z"$lastUpdatedz, price:lastSalePrice from select by sym:symbol from iextops where symbol in `SPY`AAPL'
        tm = q(query)
        print(f'xxxx tickupdate: {query}, qtime: {tm}')
        
        return {'msg_type': 'tick_update', 'data': tm.to_json(orient='records') }

    except Exception as e:
        print(f'ERROR: in querying Kdb tickupdate, {e}')

    return {'error:': 'kdb data not available.'}


@app.route('/tickupdate2')
def get_tick_update2():
    print(f'xxxx get_tick_update2 {q}, {q.is_connected()}')

    if not q.is_connected():
        return {'error:': 'not connected to kdb'}
    
    try:
        query2 = '0!select tm:qtm, price:lastSalePrice by sym:symbol from  update qtm:"j"$(lastSaleTimez-1970.01.01D)%1000000, qtmz:"z"$lastSaleTimez from select from iextops where symbol in `SPY`AAPL, lastSaleTimez.minute>=13:30'
        df = q(query2)
        print(f'xxxx tickupdate2: {query2}, df:')
        #print(df.head())

        #tops_data = [{'name':row.sym.decode('utf-8'), 'data':list(map(list, zip(row['tm'].astype(int), row['price'])))} for i, row in df.iterrows()]
        tops_data = [{'name':row.sym.decode('utf-8'), 'data':list(map(list, zip(row['tm'], row['price'])))} for i, row in df.iterrows()]
        #print(f'xxxx tickupdate2: {query2}, tops_data: {tops_data} ')

        #tops_data20 = json.dumps(tops_data)
        #print(f'xxxx tickupdate2: {query2}, tops_data20: {tops_data20} ')        
        tops_json = '[{"name": "AAPL", "data": [[1592323719865, 349.72], [1592323778164, 349.75], [1592323856421, 349.365], [1592323917619, 349.5], [1592323975537, 350.0]]}, {"name": "SPY", "data": [[1592323735266, 311.54], [1592323797892, 311.59], [1592323853178, 311.44], [1592323919910, 311.65], [1592323978168, 311.92]]}]'
        #print(f'xxxx tickupdate2: {query2}, tops_json: {tops_json} ')
        
        return {'msg_type': 'tick_update2', 'tops_data': tops_json, 'tops_data20': json.dumps(tops_data) }

    except Exception as e:
        print(f'ERROR: in querying Kdb tickupdate, {e}')
        traceback.print_exc(file=sys.stdout)

    return {'error:': 'kdb data not available.'}


### query alpaca api for acct_bal and pnl
@app.route('/pnlupdate')
def get_pnl_update():
    acct = api.get_account()
    print(f'xxxx get_pnl_update acct status: {acct.status}, equity: {acct.equity}')

    if acct.status != "ACTIVE":
        # generate a boost alert msg -
        return {'api error:': 'account is not ACTIVE'}
    
    try:
        # get total unrealized pnl
        #int(pd.to_datetime(datetime.now()).value / 1000000)
        #pnl_data = [{'sym': 'XXX', 'pnl': [int(datetime.now().timestamp()*1000), float(acct.portfolio_value)] }]
        pnl_data = [{'sym': 'XXX', 'pnl': [int(datetime.now().timestamp()*1000), float(acct.portfolio_value)] }] 
        #, {'sym': 'AAPL', 'pnl': [int(pd.to_datetime(datetime.now()).value / 1000000), float(acct.equity)] }]
        print(f'xxxx pnlupdate: {pnl_data}')
        
        return {'msg_type': 'pnl_update', 'data': json.dumps(pnl_data) }

    except Exception as e:
        print(f'ERROR: in getting pnl update, {e}')
        traceback.print_exc(file=sys.stdout)

    return {'error:': '(api) account is not available.'}



### global signal map - so it doesn't get overwritten when browser refreshes ###
## IMPL
long_signals_count_dict = defaultdict(int)
long_signals_count_map = {}
short_signals_count_dict = defaultdict(int)
short_signals_count_map = {}

# track all signals that result into orders -
orders_hist = []
orders_hist_df = pd.DataFrame()

# track every position's pnl
acct_pnl = {}
pos = {}


def update_signals_count(signals_count_map, signals_count_dict, signals_df, long_or_short):
    #### update signals_rank -- $$$ IMPL
    
    for i, row in signals_df.iterrows():
        sym = row['sym']
        if isinstance(sym, bytes):
            sym = sym.decode('utf-8')

        if signals_count_dict[sym] == 0:
            signals_count_dict[sym] += 1
            signals_count_map[sym] = row
        else:
            prev = signals_count_map[sym]
            
            if prev['qtm'] != row['qtm']:
                signals_count_dict[sym] += 1
                signals_count_map[sym] = row  # update to the latest signal details -


                if signals_count_dict[sym] == 5:  # only sent entry order once

                    #if len(orders_hist) > int(config['orders_threshold']):
                    if len(pos) >= int(config['orders_threshold']):
                        print(f'KKKK daily orders_threshold reached, not sending order for signal: {sym}')

                    elif pos.get(sym, None) is not None:
                        print(f'FFFF already has position for signal: {sym}')

                    elif long_or_short > 0:
                        print(f'$$$$ sending Buy (entry) order for signal: {sym}')

                        #if config.get('enable_trading', False) == 'True':
                        status = send_basic_order(api, sym, init_order_size, 'buy')
                        print(f"$$$$ sent order for signal: {sym}, status: {status}")

                        #orders_hist.append(row.to_dict('records'))
                        pos[sym] = row
                        orders_hist.append([datetime.now(), sym, init_order_size, 'buy', 'ENTRY', row['close'], row['qtm']])

                    elif long_or_short < 0:
                        print(f'XXXX system does not support SHORT SELL orders, skip signal: {sym}')

                        """
                        if pos.get(row['sym'], None) is not None:
                            print(f'$$$$ sending Sell (exit) order for signal: {row}')
                            #send_basic_order(api, row['sym'], init_order_size, 'sell')
                            send_exit_order(row['sym'].decode('utf-8'), init_order_size, 'sell')
                            del pos[row['sym']]

                            orders_hist.append([datetime.now(), row['sym'].decode('utf-8'), init_order_size, 'sell', 'mkt', row['close'], row['qtm']])
                        else:
                            print(f'XXXX system does not support SHORT SELL orders, skip signal: {row}')
                        """

                    else:
                        print(f'XXXX Unkown state, skip signal: {row}')


                # exit for profit
                elif signals_count_dict[sym] > 9:
                    if not bool(config.get('enable_trading', False)):
                        pass
                    elif pos.get(sym, None) is None:
                        pass
                    else:

                        if signals_count_dict[sym] == 10:
                            # taking profit on existing order - do 1/2, 1/4, 1/4 method?
                            send_exit_order(sym, init_order_size/2, 'sell')
                            print('$$$$ exiting 1/2 profitable position0: sell {init_order_size/2} {sym}')
                            orders_hist.append([datetime.now(), sym, init_order_size/2, 'sell', 'TAKE_PROFIT1', row['close'], row['qtm']])

                        elif signals_count_dict[sym] == 15:
                            # taking profit on existing order - do 1/2, 1/4, 1/4 method?
                            send_exit_order(sym, init_order_size/4, 'sell')
                            print('$$$$ exiting 1/2 profitable position1: sell {init_order_size/4} {sym}')
                            orders_hist.append([datetime.now(), sym, init_order_size/4, 'sell', 'TAKE_PROFIT2', row['close'], row['qtm']])

                        elif signals_count_dict[sym] == 20:
                            # taking profit on existing order - do 1/2, 1/4, 1/4 method?
                            send_exit_order(sym, init_order_size/4, 'sell')
                            print('$$$$ exiting 1/2 profitable position2: sell {init_order_size/4} {sym}')
                            orders_hist.append([datetime.now(), sym, init_order_size/4, 'sell', 'TAKE_PROFIT3', row['close'], row['qtm']])

                            del pos[sym]

                            ## start over - reset cache so we can trade this again if momentum builds up
                            removed = signals_count_map.pop(sym, None)
                            if removed is not None:
                                signals_count_dict.pop(sym)
                                print(f'AAAA removed signal {sym} from cache so it can be traded again $$$.')


    print(f'$$$$: signals_count_dict: {signals_count_dict}')


def remove_signals_count(signals_count_map, signals_count_dict, signals_df):
    #### remove signal from opposite map if trend reverse -- $$$$ IMPL
    # exit_at_loss  - for long positions, going down to low of the day
    #               - for short positions, going up to high of the day

    for i, row in signals_df.iterrows():
        sym = row['sym']
        if isinstance(sym, bytes):
            sym = sym.decode('utf-8')

        removed = signals_count_map.pop(sym, None)
        if removed is not None:
            signals_count_dict.pop(sym)
            print(f'XXXX removed sig {sym} from opposite signals map.')

            ### NEED TO EXIT ACTIVE POSTION COMPLETELY $$$
            if pos.get(row['sym'], None) is not None:
                print(f'$$$$ sending Sell (exit) order for signal: {sym}')
                #send_basic_order(api, row['sym'], init_order_size, 'sell')
                send_exit_order(sym, init_order_size, 'sell')
                del pos[sym]

                orders_hist.append([datetime.now(), sym, init_order_size, 'sell', 'STOP_LOSS', row['close'], row['qtm']])



def create_long_short_signals(stats):
    # APPLY signals and send orders to Alpaca, update real-time postions
    signal_long = stats.loc[(stats.n>=30) & (stats.close==stats.mx) & (stats.close>stats.open)].copy()
    signal_long['signal'] = 'Mom_Long'

    # send to order event queue -
    if len(signal_long) > 0:
        print('$$$$ got mom LONG signals: (send to Alexa) ')
        #print(signal_long)
        # check if any active positions -
        update_signals_count(long_signals_count_map, long_signals_count_dict, signal_long, 1)
        remove_signals_count(short_signals_count_map, short_signals_count_dict, signal_long)


    signals_short = stats.loc[(stats.n>=30) & (stats.close==stats.mn) & (stats.close<stats.open)].copy()
    signals_short['signal'] = 'Mom_Short'

    if len(signals_short) > 0:
        print('$$$$ got SHORT signals: (send to Alexa) ')
        #print(signals_short)
        update_signals_count(short_signals_count_map, short_signals_count_dict, signals_short, -1)
        remove_signals_count(long_signals_count_map, long_signals_count_dict, signals_short)


    ## print any live pos - 
    print(f'$$$$ create_long_short_signals, position count: {len(pos)}, active positions: {pos.keys()}')

    # merge Long/Short signals -
    #signals_df = pd.concat([signal_long, signals_short])
    return pd.concat([signal_long, signals_short])


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    signals_hist = []
    signals_hist_df = pd.DataFrame()
    # track order hist change
    orders_hist_len = 0

    try:
        while True:
            print(f'################################# background thread running {datetime.now()} ###############')

            stats = q("get_summary2[]")
            stats['count'] = count

            #print('xxxx: stats -')
            #print(stats.tail())
            stats_json = stats.to_json(orient='records')
            #print(stats.dtypes)
            #stats_html = stats.to_html(classes="table table-hover table-bordered table-striped",header=True)
            #print(stats_json)
            #print(stats_html)

            # merge Long/Short signals -
            signals_df = create_long_short_signals(stats)

            if len(signals_df) > 0:
                signals_ui = signals_df[['count', 'sym', 'qtm', 'n', 'open', 'mn', 'mu', 'md', 'mx', 'vwap', 'close', 'dv', 'atr', 'signal']]
                print('xxxx signals_ui: ')
                print(signals_ui)

                signals_hist.append(signals_df)
                # keep just the last 5 signals
                if len(signals_hist) > 5:
                    signals_hist = signals_hist[-5:]

                # display only the last n signals -        
                signals_hist_df = pd.concat(signals_hist).sort_values(by='count', ascending=False)
                #print('xxxx signal_hist_df')
                #print(signals_hist_df)

            # keep last 5 signals
            hist_cols = ['count', 'sym', 'qtm', 'n', 'open', 'mn', 'mu', 'md', 'mx', 'vwap', 'close', 'dv', 'atr', 'signal']
            signals_cols = ['id', 'qtm', 'src', 'sym', 'price', 'volume', 'ps', 'tick', 'signal']

            if len(signals_hist_df) > 0:
                signals_html = signals_hist_df[hist_cols].to_html(classes="table table-hover table-bordered table-striped",header=True)
                signals_tbl = signals_hist_df[list(set(signals_cols) | set(hist_cols))]
            else:
                signals_html = signals_hist_df.to_html(classes="table table-hover table-bordered table-striped",header=True)
                signals_tbl = signals_hist_df

            # latest signals -
            signals_json = signals_tbl.to_json(orient='records')
            #print('$$$$ signals_json')
            #print(signals_json)

            # orders_hist_df
            orders_hist_html = f"<div>Daily order count: {len(orders_hist)}</div>"
            print(orders_hist_html)            
            
            if len(orders_hist) > 0:
                #orders_hist_df = pd.concat(orders_hist)
                orders_hist_df = pd.DataFrame(orders_hist, columns=['order_time', 'symbol', 'size', 'side', 'ord_type', 'ref_price', 'signal_time'])
                #print(orders_hist_df)
                
                ## save to file
                if orders_hist_len < len(orders_hist_df):
                    orders_hist_df.to_csv('/tmp/alpaca_paperlive_{}.csv'.format(datetime.today().date().strftime('%m%d%Y')))
                    orders_hist_len = len(orders_hist_df)
                    print(orders_hist_df)

                # send to html
                orders_hist_html += orders_hist_df.to_html(classes="table table-hover table-bordered table-striped",header=True)
                #print(orders_hist_html)


            # minute price series -
            query = '0!select data:100*price % first price by name:sym  from select last price by sym, qtm.minute from trade where sym like "XL*"'
            prices_df = q(query)
            prices_json = prices_df.to_json(orient='records')
            print('xxxx prices_json:')
            #print(prices_json)

            # create time series JSON obj for Highchart -
            query = """
            { 
            tm:0!select last price by sym, 5 xbar qtm.minute from trade where sym in x, qtm.minute>=?[.z.T>=13:35;13:30;12:01];
            exec (distinct tm`sym)#sym!price by mm:minute from tm
            } (exec distinct sym from trade)
            """
            minute_df = q(query)
            print('xxxx minute_df:')
            minute_df = minute_df.bfill() # to ensure price available from Open
            minute_df = minute_df.ffill() # to keep each series up to date
            #print(minute_df.head())
            #print(minute_df.tail())
            #minute_rebased = rebase_series(minute_df.dropna())
            minute_rebased = rebase_series(minute_df.ffill())

            minute_json = []
            for sym, row in minute_rebased.items():
                #print(f"i:{i}, r:{list(row.index)}, {list(row)}")
                #print(f"name:{i}, data:{list(zip(list(row.index), list(row)))}")
                #minute_json.append({f"name:{i}, data:{list(zip(list(row.index), list(row)))}"})
                #minute_json.append({f"name:{i}, data:{list(map(list, zip(list(row.index), list(row))))}"})            
                #minute_json.append({f"name:{i}, data:{list(map(list, zip([str(x).split(' ')[-1] for x in row.index], list(row))))}"})
                
                #print(f"i:{sym},  {[datetime.strptime(str(x).split(' ')[-1], '%H:%M:%S').timestamp() for x in row.index]}")            
                #print(f"name:{sym}, {[int(pd.to_datetime(datetime.strptime(str(x).split(' ')[-1], '%H:%M:%S')).value/100000) for x in row.index]}")
                #mdata = list(map(list, zip([datetime.strptime(str(x).split(' ')[-1], '%H:%M:%S').isoformat() for x in row.index], list(row))))
                mdata = list(map(list, zip([int(pd.to_datetime(datetime.strptime(str(x).split(' ')[-1], '%H:%M:%S')).value / 1000000) for x in row.index], list(row))))
                minute_json.append({"name": sym, "data": mdata})


            print('xxxx minute_json:')
            #print(minute_json)

            # publish kdb upd time:
            tm = q('update dft:"t"$"z"$(qtm-"z"$wstm) from select max qtm, max wstm from update wstm:"p"$1970.01.01D+tms from select by sym from trade')
            print(f'count: {count}, qtime: {tm}')

            ### send alert to UI when delay is over 1m - IMPL
            live_positions_df = get_live_positions()
            live_positions_html = live_positions_df.to_html(classes="table table-hover table-bordered table-striped",header=True)


            long_signals_rank = sorted(long_signals_count_dict.items(), key=lambda x: x[1], reverse=True) 
            short_signals_rank = sorted(short_signals_count_dict.items(), key=lambda x: x[1], reverse=True)

            print(f'$$$$$$$$ SSSSSSSSSSSSSSSSSSS sending wss updates {datetime.now()}')

            socketio.emit('my_response',
                            {'count': count,
                            #'time':str(tm).split(" ")[0],
                            'time': str(tm.iloc[-1]['dft']),

                            'signals_rank_long': str(long_signals_rank),
                            'signals_rank_short': str(short_signals_rank),
                            'signals_html': signals_html,
                            'orders_hist_html': orders_hist_html,
                            'live_positions_html': live_positions_html,

                            'signal': signals_json,                       
                            'summary': stats_json,

                            'prices_series': prices_json,
                            'minute_json': json.dumps(minute_json),

                            }, namespace='/test2')

            print(f'XXXXXXXXXXXXXXXXXXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxx DONE. {datetime.now()} xxxxxxxxxxxxxx')
            print('\n')

            # set update period
            socketio.sleep(13)
            count += 1


        # end while

    except Exception as ex:
        print(f"ERROR: background thread exception: {ex}")
        traceback.print_exc(file=sys.stdout)
        sys.exit(-1)


### API info -
load_app_config('app.config')

API_KEY = config['key_id']
API_SECRET = config['secret_key']
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"
api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

get_account_info()
# send test order -


print('xxxx connect to Kdb...')

# create connection object
#q = qconnection.QConnection(host='localhost', port=5001, pandas=True)
q = qconnection.QConnection(host='aq101', port=6001, pandas=True)

print('XXXXXXXX enable_trading?? ', config.get('enable_trading'))
if config.get('enable_trading', False) == 'True':
    print('$$$$ enabled_trading=True')
else:
    print('XXXX enabled_trading=False')


## order_entry_size
init_order_size = int(config.get('init_order_size', 4))


#### main ####
if __name__ == '__main__':
    #socketio.run(app, debug=False)
    socketio.run(app, debug=False, host='0.0.0.0', port=8501)
