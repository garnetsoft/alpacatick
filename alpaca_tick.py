import os
import sys
import numpy as np
import pandas as pd

import datetime
import json
import threading
import random
from threading import Thread
from queue import Queue
import configparser
import time


import websocket
try:
    import thread
except ImportError:
    import _thread as thread


from KdbThread import KdbThread


#### wss req messages ####
auth_req = {
    "action": "authenticate",
    "data": {
        "key_id": "",
        "secret_key": ""
    }
}

sub_req = {
    "action": "listen",
    "data": {
        "streams": ["T.AAPL", "T.SPY", "Q.AAPL", "Q.SPY"]
    }
}


def on_message(ws, message):
    #print('xxxx wss on_message:')
    #print(message)
    # send to kdb
    queue.put(message)


def on_error(ws, error):
    print('xxxx wss on_error:')
    print(error)


def on_close(ws):    
    print("### wss closed ###")


def on_open(ws):
    ticker_file = config['ticker_file']

    df = pd.read_csv(ticker_file)
    tickers = tuple(df.ticker)
    print('xxxx subscribe real-time tick for: ', tickers)

    def run(*args):
        time.sleep(1)

        auth_req['data']['key_id'] = config['key_id']
        auth_req['data']['secret_key'] = config['secret_key']

        ws.send(json.dumps(auth_req))
        time.sleep(3)
        #result =  ws.recv()
        #print("Received '%s'" % result)

        print('XXXX tickers: ', args)
        sub_streams = []
        for ticker in args:
            sub_streams.append(f'T.{ticker}')
            sub_streams.append(f'Q.{ticker}')

        sub_req['data']['streams'] = sub_streams
        print('XXXX sub_req: ', sub_req)

        # next send sub_req
        ws.send(json.dumps(sub_req))
        time.sleep(2)

        #result =  ws.recv()
        #print("Received '%s'" % result)
        print('xxxx listening for trades and quotes...')
        time.sleep(60*60)

        print("xxxx wss thread terminating...")
        ws.close()

        print("xxxx wss thread terminated...")

    # start the auth and sub req on a seperate thread 
    # so the main thread can process the incoming data
    thread.start_new_thread(run, tickers)


def usage():
    print("usage: python cbp_data.py <trade> <BTC-USD>")


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


# global properties
config = {}

# define message queue to be shared between WSS and Kdb+ threads 
queue = Queue()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        usage()
        #sys.exit(-1)
        load_app_config('app.config')
    else:
        load_app_config(sys.argv[1])

    try: 
        # start Kdb+ data thread
        kt = KdbThread(config, queue)
        kt.start()

        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(#"ws://echo.websocket.org/",
            #"https://data.alpaca.markets/v1",
            "wss://data.alpaca.markets/stream",
            on_message = on_message,
            on_error = on_error,
            on_close = on_close)

        ticker_file = config['ticker_file']
        ws.on_open = on_open
        ws.run_forever()

        print('xxxx stopping kdb thread: ',kt)
        kt.stop()
        kt.join()

        # wait for sys clean up
        time.sleep(2)

        print('xxxx main exiting...0')
        sys.exit()
        print('xxxx DONE.')

    except Exception as e:
        print('....program exceptions, exiting...', e)
        sys.exit(-1)