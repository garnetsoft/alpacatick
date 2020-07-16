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

import uuid
UUID = uuid.uuid1()
print(UUID)


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


def gen_order_id():
    return uuid.uuid1().hex[:8]


### position management ###

acct_balance = []

def get_today_pnl():
    account = api.get_account()
    print(f'HAHA: {type(account)}, {account.last_equity}, {account.equity}')

    pnl = float(account.equity) - float(account.last_equity)
    pct = 100* pnl / float(account.last_equity)
    
    return [pnl, pct]


def get_account_info():
    account = api.get_account()
    print(f'0000: {account}')

    # open orders
    orders = api.list_orders(status="open")
    for i, order in enumerate(orders):
        print(f'xxxx {i} ord: {order}')

    positions = api.list_positions()
    notional = 0.0
    for i, position in enumerate(positions):
        # print(f'$$$$ {i} pos: {position}')
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

            pos_list.append([pos.symbol, pos.qty, pos.market_value, float(pos.unrealized_pl), pos.side, pos.avg_entry_price, pos.current_price])
            notional += float(pos.market_value)

        print(f'$$$$ total USD: {notional}')

    pos_df = pd.DataFrame(pos_list, columns=['symbol', 'qty', 'market_value', 'unrealized_pl', 'side', 'avg_entry_price', 'current_price'])

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



def send_entry_order2(sym, size, side, signal, entry_type):
    if isinstance(sym, bytes):
        sym = sym.decode('utf-8')

    print(f'EEEE sending {entry_type} order for signal: {sym}')

    status = None
    if trading_enabled:
        status = send_basic_order(api, sym, size, side)
        print(f'EEEE entry order: {sym}, {side}, {size} executed. status: {status}')
    else:
        print(f'EEEE trading_enabled is {trading_enabled}, entry order: {sym}, {side}, {size} NOT sent.')
    
    ## - add to order_hist
    order_id = gen_order_id()
    order_id_dict[sym] = order_id
    orders_hist.append([datetime.now(), sym, size, side, entry_type, signal['close'], signal['qtm'], order_id])

    pos[sym] = signal

    #print(f"EEEE sent order for {entry_type} signal: {sym}, status: {status}")
    if status:
        print(f"EEEE sent order for {entry_type} signal: {sym}, status: {status}")
    else:
        ## raise alert !!
        alert_msg = f"EEEE ERROR in sent order for {entry_type} signal: {sym}, status: {status}"
        global alerts
        print(alert_msg)
        alerts[sym] = alert_msg


    return status


def send_exit_order2(sym, size, side, signal, exit_type):
    if isinstance(sym, bytes):
        sym = sym.decode('utf-8')

    print(f'EEEE sending {exit_type} order for signal: {sym}')

    status = None
    if trading_enabled:
        status = send_basic_order(api, sym, size, side)
        print(f'EEEE exit order: {sym}, {side}, {size} executed. status: {status}')
    else:
        print(f'EEEE trading_enabled is {trading_enabled}, entry order: {sym}, {side}, {size} NOT sent.')
    
    ## - add to order_hist
    org_order_id = order_id_dict.get(sym, None)
    orders_hist.append([datetime.now(), sym, size, side, exit_type, signal['close'], signal['qtm'], org_order_id])
    #pos[sym] = signal

    print(f"EEEE sent order for {exit_type} signal: {sym}, status: {status}")

    return status



def close_sym_position(sym):
    positions = api.list_positions()

    for position in positions:
        if position.symbol == sym:
            if(position.side == 'long'):
                orderSide = 'sell'
            else:
                orderSide = 'buy'

            qty = abs(int(float(position.qty)))

            return send_basic_order(api, sym, qty, orderSide)


def get_position_info(sym):
    positions = api.list_positions()

    for position in positions:
        if position.symbol == sym:
            return position

    return None


def clear_residual_positions():
    positions = api.list_positions()
    
    for position in positions:
        qty = abs(int(float(position.qty)))

        if qty == int(init_order_size / 4):
            if(position.side == 'long'):
                orderSide = 'sell'
            else:
                orderSide = 'buy'

        respSO = []
        tSubmitOrder = threading.Thread(target=submitOrder(qty, position.symbol, orderSide, respSO))
        tSubmitOrder.start()
        tSubmitOrder.join()

        ## also need to clear positions from pos, add to order_hist as well

    return respSO


def close_all_positions():
    try:
        api.close_all_positions()
        print("All postions closed.")
    except Exception as e:
        print(f"Error: {str(e)}")


#### stats module 
def rebase_series(series):
    if len(series) > 0:
        return (series / series.iloc[0]) * 100

    return series


### app routes -
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode, trading_enabled=trading_enabled, )


### update global config - insert key/value pair
@socketio.on('my_info', namespace='/test2')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    print(f'xxxx CONFIG UPDATE: {message}')
    #clear_residual_positions()
    
    cmdstr = str(message['data'])
    if cmdstr.index('=') > 0:
        kv = cmdstr.split("=")
        k, v = kv[0], kv[1]
        print(f'xxxx CONFIG COMMAND: {k}={v}')
        update_configs(**{k: v})

    info_data = len(pos)

    if cmdstr.startswith('pos'):
        print(f'xxxx printPos()')
        
        if info_data > 0:
            info_data = pos[list(pos)[-1]]
    elif cmdstr.startswith('cache'):
        print(f'xxxx printCache()')


    print(f'XXXX SETTINGS : {info_data}')


    ## wss update -
    emit('my_info',
         {'data': message['data'], 'count': session['receive_count'], 
         'config': json.dumps(config), 
         'info_data': info_data,
         })


### CLOSE ALL POSITIONS $$$
@socketio.on('my_broadcast_event', namespace='/test2')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1

    print(f'xxxx HALT TRADING: {message}')
    # keyword from UI -
    #close_all_positions()

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

    # initQ
    initQ()

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

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
        df = df.replace(0, np.nan).bfill().ffill()
        df = rebase_series(df)
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
        df = df.replace(0, np.nan).bfill().ffill()
        df = rebase_series(df)
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
        query = '0!select tm:qtm, price:lastSalePrice by sym:symbol from  update qtm:"j"$(lastSaleTimez-1970.01.01D)%1000000, qtmz:"z"$lastSaleTimez from  select from iextops where symbol in `SPY`AAPL, lastSaleTimez.minute>=13:30'
        df = q(query)
        print(f'xxxx tickupdate2: {query}, df:')
    
        tops_data = [{'name':row.sym.decode('utf-8'), 'data':list(map(list, zip(row['tm'], row['price'])))} for i, row in df.iterrows()]
        #print(f'xxxx tickupdate2: {query}, tops_data: {tops_data} ')


        query2 = 'update sym:`AAPL2`SPY2 from  0!select tm:tms%1000000, price by sym from update wtm:"p"$1970.01.01D+tms from  select by qtm.minute, sym from trade where sym in `SPY`AAPL, qtm.minute>=13:30'
        df2 = q(query2)
        ticks_data = [{'name':row.sym.decode('utf-8'), 'data':list(map(list, zip(row['tm'], row['price'])))} for i, row in df2.iterrows()]
        #print(f'xxxx tickupdate2: {query2}, ticks_data: {ticks_data} ')        
        # test data
        tops_json = '[{"name": "AAPL", "data": [[1592323719865, 349.72], [1592323778164, 349.75], [1592323856421, 349.365], [1592323917619, 349.5], [1592323975537, 350.0]]}, {"name": "SPY", "data": [[1592323735266, 311.54], [1592323797892, 311.59], [1592323853178, 311.44], [1592323919910, 311.65], [1592323978168, 311.92]]}]'


        return {'msg_type': 'tick_update2', 'ticks_data': tops_json, 'tops_data': json.dumps(tops_data+ticks_data) }
        #return {'msg_type': 'tick_update2', 'ticks_data': tops_json, 'tops_data': json.dumps(ticks_data) }

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
        pnl_data = [{'sym': 'pnl', 'pnl': [int(datetime.now().timestamp()*1000), float(acct.portfolio_value)] }] 
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
order_id_dict = {}

def update_signals_count(signals_count_map, signals_count_dict, signals_df, long_or_short):
    #### update signals_rank -- $$$ IMPL
    
    for _, row in signals_df.iterrows():
        sym = row['sym']
        if isinstance(sym, bytes):
            sym = sym.decode('utf-8')

        if signals_count_dict[sym] == 0:
            signals_count_dict[sym] += 1
            signals_count_map[sym] = row
        else:
            prev = signals_count_map[sym]
            
            #if (prev['qtm'] != row['qtm']) and (prev['close'] != row['close']):
            if prev['qtm'] != row['qtm']:
                signals_count_dict[sym] += 1
                signals_count_map[sym] = row  # update to the latest signal details -


                if signals_count_dict[sym] == 5:  # only sent entry order once

                    #if len(orders_hist) > int(config['orders_threshold']):
                    if len(pos) >= int(config['orders_threshold']):
                        print(f'KKKK daily orders_threshold reached, not sending order for {long_or_short} signal: {sym}')

                        ### maybe we should clear out the positions with 1/4 pct of size left to give rooms to new opportunities ??
                        # clear_residual_positions()

                    elif pos.get(sym, None) is not None:
                        print(f'FFFF already has position for signal: {sym}')

                    elif long_or_short > 0:
                        send_entry_order2(sym, init_order_size, 'buy', row, 'ENTRY_LONG')
                        #pos[sym] = row
                        #orders_hist.append(row.to_dict('records'))
                        #orders_hist.append([datetime.now(), sym, init_order_size, 'buy', 'ENTRY_LONG', row['close'], row['qtm']])

                    elif long_or_short < 0:
                        send_entry_order2(sym, init_order_size, 'sell', row, 'ENTRY_SHORT')
                        #pos[sym] = row
                        #orders_hist.append([datetime.now(), sym, init_order_size, 'sell', 'ENTRY_SHORT', row['close'], row['qtm']])

                    else:
                        print(f'XXXX Unkown state, skip {long_or_short} signal: {row}')


                # exit for profit
                elif signals_count_dict[sym] > 9:
                    #if not config.get('enable_trading', False) == 'True':
                    #    print('XXXX trading is NOT enabled, ignoring {long_or_short} signal for {sym}')
                    #    pass
                    #elif pos.get(sym, None) is None:
                    if pos.get(sym, None) is None:
                        pass
                    else:
                        side = 'buy' if long_or_short < 0 else 'sell'

                        if signals_count_dict[sym] == 10:
                            # taking profit on existing order - do 1/2, 1/4, 1/4 method?
                            # get position size from entry order AND broker to ensure double confirmation
                            send_exit_order2(sym, init_order_size/2, side, row, 'TAKE_PROFIT_1')
                            print('$$$$ exiting 1/2 profitable position0: sell {init_order_size/2} {sym}')
                            #orders_hist.append([datetime.now(), sym, init_order_size/2, side, 'TAKE_PROFIT1', row['close'], row['qtm']])

                        elif signals_count_dict[sym] == 15:
                            # taking profit on existing order - do 1/2, 1/4, 1/4 method?
                            send_exit_order2(sym, init_order_size/4, side, row, 'TAKE_PROFIT_2')
                            print('$$$$ exiting 1/4 profitable position1: sell {init_order_size/4} {sym}')
                            #orders_hist.append([datetime.now(), sym, init_order_size/4, side, 'TAKE_PROFIT2', row['close'], row['qtm']])

                        elif signals_count_dict[sym] == 20:
                            # taking profit on existing order - do 1/2, 1/4, 1/4 method?
                            send_exit_order2(sym, init_order_size/4, side, row, 'TAKE_PROFIT_EXIT')
                            print('$$$$ exiting 1/4 profitable position2: sell {init_order_size/4} {sym}')
                            #orders_hist.append([datetime.now(), sym, init_order_size/4, side, 'TAKE_PROFIT3', row['close'], row['qtm']])

                            del order_id_dict[sym]
                            del pos[sym]

                            ## start over - reset cache so we can trade this again if momentum builds up
                            removed = signals_count_map.pop(sym, None)
                            if removed is not None:
                                signals_count_dict.pop(sym)
                                print(f'AAAA removed signal {sym} from cache so it can be traded again $$$.')


    print(f'$$$$: {long_or_short} signals_count_dict: {signals_count_dict}')


def remove_signals_count(signals_count_map, signals_count_dict, signals_df):
    #### remove signal from opposite map if trend reverse -- $$$$ IMPL
    # exit_at_loss  - for long positions, going down to low of the day
    #               - for short positions, going up to high of the day

    for _, row in signals_df.iterrows():
        sym = row['sym']
        if isinstance(sym, bytes):
            sym = sym.decode('utf-8')

        removed = signals_count_map.pop(sym, None)
        if removed is not None:
            signals_count_dict.pop(sym)
            print(f'XXXX removed sig {sym} from opposite signals map.')

            ### NEED TO EXIT ACTIVE POSTION COMPLETELY so it can trade on opposite trend $$$
            if pos.pop(sym, None) is not None:
                print(f'$$$$ sending STOP_LOSS (exit) order for signal: {sym}')

                #close_sym_position(sym)
                pos_info = get_position_info(sym)

                if pos_info is not None:
                    if(pos_info.side == 'long'):
                        orderSide = 'sell'
                    else:
                        orderSide = 'buy'

                    qty = abs(int(float(pos_info.qty)))
                    send_exit_order2(sym, qty, orderSide, row, 'STOP_LOSS_EXIT')
                    #orders_hist.append([datetime.now(), sym, qty, orderSide, 'STOP_LOSS', row['close'], row['qtm']])
                    #del pos[sym]

    return None


def create_long_short_signals(stats):
    # ONLY DOW 30 NAMES -


    # APPLY signals and send orders to Alpaca, update real-time postions
    signal_long = stats.loc[(stats.n>=stats_threshold) & (stats.close>=stats.mx) & (stats.close>stats.open)].copy()
    signal_long['signal'] = 'Mom_Long'

    # send to order event queue -
    if len(signal_long) > 0:
        print('$$$$ got mom LONG signals: (send to Alexa) ')
        #print(signal_long)
        # check if any active positions -
        update_signals_count(long_signals_count_map, long_signals_count_dict, signal_long, 1)
        remove_signals_count(short_signals_count_map, short_signals_count_dict, signal_long)


    signals_short = stats.loc[(stats.n>=stats_threshold) & (stats.close<=stats.mn) & (stats.close<stats.open)].copy()
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


def calc_pnl(g, long_or_short):
    entry_price = g.iloc[0]['ref_price']
    total_pnl = 0.0

    for i, (index, r) in enumerate(g.iterrows()):
        # print(f'xxxx: {i}, {r}')
        # if not r['ord_type'].startswith('ENTRY'): # calc each pnl
        if i > 0:
            exit_price = r['ref_price']
            size = r['size']
            total_pnl += (exit_price - entry_price) * size * long_or_short

    # print(f'$$$$ total_pnl: {total_pnl}, {size}')
    # float("{:.2f}".format(total_pnl)) 
    return float("{:.2f}".format(total_pnl)) 


def get_agg_pnl(df):
    #orders_hist_df = pd.DataFrame(orders_hist, columns=['order_time', 'symbol', 'size', 'side', 'ord_type', 'ref_price', 'signal_time', 'order_id'])

    long_pnl, short_pnl = 0.0, 0.0
    pnl_map = defaultdict(float)
    
    #for name, g in df.loc[df.symbol=='TWTR'].groupby('order_id'):
    for name, g in df.groupby('order_id'):
        #print(f'xxxx order_id {name}, DDDD: {len(g)}, {g}')
        sym = g.iloc[0]['symbol']

        if g.iloc[0]['ord_type'] == 'ENTRY_LONG':
            pnl = calc_pnl(g, 1)
            long_pnl += pnl
            pnl_map[sym] += pnl
            #print(f"xxxx LONG order_id: {name}, {g.iloc[0]['symbol']} pnl {pnl}")
        elif g.iloc[0]['ord_type'] == 'ENTRY_SHORT':
            pnl = calc_pnl(g, -1)
            short_pnl += pnl
            pnl_map[sym] += pnl
            #print(f"xxxx SHORT order_id: {name}, {g.iloc[0]['symbol']} pnl {pnl}")
        else:
            print(f'ERROR: Unknown entry order: {name}, {g}')

    print(f'$$$$ total_pnl: {long_pnl+short_pnl}, long_pnl: {long_pnl}, short_pnl: {short_pnl}, shared_traded: {np.sum(df.size)}')
    #print(sorted(pnl_map.items(), key=lambda x: x[1], reverse=True))
    
    # float("{:.2f}".format(orig_float)) 
    return sorted(pnl_map.items(), key=lambda x: x[1], reverse=True)


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    signals_hist = []
    signals_hist_df = pd.DataFrame()
    # track order hist change
    orders_hist_len = 0
    sorted_pnl = defaultdict(float)


    try:
        while True:
            print(f'{datetime.now()}################################# background thread running {count} ###############')

            # set update period
            socketio.sleep(13)
            count += 1

            stats = q("get_summary2[]")
            stats['count'] = count

            #print('xxxx: stats -')
            #print(stats.tail())
            stats_json = stats.to_json(orient='records')
            #print(stats.dtypes)
            #stats_html = stats.to_html(classes="table table-hover table-bordered table-striped",header=True)
            #print(stats_json)
            #print(stats_html)

            # check ACTIVE trading period -
            bday = datetime.today().date().strftime('%m%d%Y')
            utc_time = datetime.utcnow()
            cur_hr, cur_mm = utc_time.hour, utc_time.minute
            print(f'XXXX DEBUG: UTC_TIME: {utc_time}, {cur_hr}, {cur_mm}')

            signals_df = pd.DataFrame()
            if ((cur_hr <=13 ) and (cur_mm < 35)) or (cur_hr < 13):
                print(f'HAHA: {datetime.now()} - market is not open yet.  trading starts 5 minutes after open.')
            elif ((cur_hr == 19) and (cur_mm >= 55)):
                if trading_enabled:
                    close_all_positions()
                
                get_account_info()
                pnl_info = get_today_pnl()
                print(f'$$$$: {datetime.now()} - closing out today positions. today_pnl: {pnl_info}')
            elif cur_hr >= 20:
                pnl_info = get_today_pnl()
                print(f'HEHE: {datetime.now()} - done for the day. today_pnl: {pnl_info}')
            else:
                print('XXXX updating long/short signals...')
                signals_df = create_long_short_signals(stats)


            # merged Long/Short signals -
            if len(signals_df) > 0:
                signals_ui = signals_df[['count', 'sym', 'qtm', 'n', 'open', 'mn', 'mu', 'md', 'mx', 'vwap', 'close', 'dv', 'atr', 'signal']]
                print('xxxx signals_ui: ')
                print(signals_ui)

                ### write to signal_ui_yyyyMMDD.csv file -
                with open(f'/data/signals_ui_{bday}.csv', 'a') as f:
                    f.to_csv(signals_ui, header=False)


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
                orders_hist_df = pd.DataFrame(orders_hist, columns=['order_time', 'symbol', 'size', 'side', 'ord_type', 'ref_price', 'signal_time', 'order_id'])
                #print(orders_hist_df)
                
                ## save to file
                if orders_hist_len < len(orders_hist_df):
                    orders_hist_df.to_csv(f'/data/alpaca_paperlive_trades_{bday}.csv')
                    orders_hist_len = len(orders_hist_df)
                    print(orders_hist_df)

                # send to html
                orders_hist_html += orders_hist_df.sort_index(ascending=False).to_html(classes="table table-hover table-bordered table-striped",header=True)
                #print(orders_hist_html)
                
                # sorted pnl -
                sorted_pnl = get_agg_pnl(orders_hist_df)


            # minute price series -
            #query = '0!select data:100*price % first price by name:sym  from select last price by sym, qtm.minute from trade where sym like "XL*"'
            #prices_df = q(query)
            #prices_json = prices_df.to_json(orient='records')
            #print('xxxx prices_json:')
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
            live_positions_html = live_positions_df.sort_values('unrealized_pl').to_html(classes="table table-hover table-bordered table-striped",header=True)


            long_signals_rank = sorted(long_signals_count_dict.items(), key=lambda x: x[1], reverse=True) 
            short_signals_rank = sorted(short_signals_count_dict.items(), key=lambda x: x[1], reverse=True)
            print(f'XXXX LONG: {long_signals_rank}, SHORT: {short_signals_rank}')

            print(f'$$$$$$$$ SSSSSSSSSSSSSSSSSSS sending wss updates {datetime.now()}')
            positions_allowed = config.get('orders_threshold', 11)



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

                            # 'prices_series': prices_json,
                            'minute_json': json.dumps(minute_json),

                            'positions_allowed': positions_allowed,
                            'alerts': str(alerts),

                            'sorted_pnl': str(sorted_pnl),

                            }, namespace='/test2')

            print(f'{datetime.now()}XXXXXXXXXXXXXXXXXXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxx DONE. {count} xxxxxxxxxxxxxx')
            print('\n')

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


## model settings:
init_order_size = 4
stats_threshold = 30
trading_enabled = False

def update_configs(**kwargs):
    #print(kwargs)
    #print(kwargs.keys())
    for k, v in kwargs.items():
        print(f'{k}->{v}')
        config[k] = v

    ## update global vars
    global init_order_size, stats_threshold, trading_enabled
    init_order_size = int(config.get('init_order_size', 4))
    stats_threshold = int(config.get('stats_threshold', 30))
    trading_enabled = True if config.get('enable_trading') == 'True' else False
    
    print(f'XXXX trading_enabled={trading_enabled}')

    return None

#update_configs(**{'key':'value', 'haha':'hehe'})    
update_configs(**{})
alerts = {'SPY': 'THIS IS A TEST ALERT.'}

print('-- Display full Dataframe without truncation')
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)


# write all signals_ui df to file for backtest -


#### main ####
if __name__ == '__main__':
    #socketio.run(app, debug=True)
    socketio.run(app, debug=False, host='0.0.0.0', port=8501)
