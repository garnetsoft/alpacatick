import sys
import os

import pandas as pd
import numpy as np
import traceback
import datetime
import configparser

from datetime import datetime
from pandas.io.json import json_normalize

# kdb lib
from qpython import qconnection
from qpython.qtype import QException


import json
import pprint
import sseclient


"""
function connect() {
    stream = request({
        //url: 'https://cloud-sse.iexapis.com/stable/stocksUSNoUTP?token=YOUR_TOKEN&symbols=spy,ibm,twtr',
        url: "https://cloud-sse.iexapis.com/stable/tops?token=YOUR_TOKEN&symbols=spy,aapl,twtr,ge,dkng",
        headers: {
            'Content-Type': 'text/event-stream'
        }
    })
}
"""

def with_urllib3(url):
    """Get a streaming response for the given event feed using urllib3."""
    import urllib3
    http = urllib3.PoolManager()
    return http.request('GET', url, preload_content=False)

def with_requests(url):
    """Get a streaming response for the given event feed using requests."""
    import requests
    return requests.get(url, stream=True)


def publish_to_rdb(df, table, cols):
    # load json into dataframe
    df = df.reset_index(drop=True)

    try:
        # kdb data obj
        kdf = df[cols]
        q.sendAsync('{y insert x}', kdf, np.string_(table))
        print('$$$$ KKKK debug insert data in kdb: ', df)

    except Exception as e:
        print('xxx processing to Kdb error: ', e)
        traceback.print_exc(file=sys.stdout)


def publish_to_tp(df, table):
    # load json into dataframe
    df = df.reset_index(drop=True)

    try:
        kobj = []
        for c in df.columns:
            kobj.append(list(df[c]))

        print('$$$$ KKKK debug upd data in kdb: ', kobj)
        q.sendAsync("upd", np.string_(table), df)

    except Exception as e:
        print('xxx processing to Kdb error: ', e)
        traceback.print_exc(file=sys.stdout)


# convert a list of json object to kdb obj
def create_kdb_obj(data):
    kobj = {}

    for idx, d in enumerate(data):
        print(f'xxxx {idx}, d: {d}')

        for k, v in d.items():
            if isinstance(v, str):
                v = np.string_(v)
            else:
                v = float(v)

            kv = kobj.get(k)
            if kv:
                kv.append(v)
            else:
                kobj[k] = [v]

    return list(kobj.values())


##################################

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



print('xxxx connect to Kdb...')

# create connection object
#q = qconnection.QConnection(host='localhost', port=5001, pandas=True)
q = qconnection.QConnection(host='aqanalytics.com', port=6000, pandas=True)

q.open()
print('IPC version:%s %s. Is connected: %s' % (q, q.protocol_version, q.is_connected()))

# data table -
cols = ['symbol','sector','securityType','bidPrice','bidSize','askPrice','askSize','lastUpdated','lastSalePrice','lastSaleSize','lastSaleTime','volume', 'seq', 'lastSaleTimez','lastUpdatedz', 'seq2']
table = 'iextops2'


### API info -
load_app_config(sys.argv[1])

tickerfile = config['ticker_file']
tickers = pd.read_csv(tickerfile).ticker.unique()
symbols = ",".join(tickers)
TOKEN = config['iex_token']

#url ="https://cloud-sse.iexapis.com/stable/tops?token={TOKEN}&symbols=spy,aapl,twtr,ge,dkng"
url = f"https://cloud-sse.iexapis.com/stable/tops?token={TOKEN}&symbols={symbols}"
#response = with_urllib3(url)  # or with_requests(url)
response = with_requests(url)


client = sseclient.SSEClient(response)
for i, event in enumerate(client.events()):
    data = json.loads(event.data)
    print(f'xxxx {i}, len: {len(data)}, data: {data}')

    kobj = create_kdb_obj(data)

    try:
        print('$$$$ KKKK debug upd data in kdb: ', kobj)
        q.sendAsync("upd", np.string_(table), kobj)

    except Exception as e:
        print('xxx processing to Kdb error: ', e)
        traceback.print_exc(file=sys.stdout)


    #df = pd.DataFrame(data)
    #df['lastSaleTimez'] = pd.to_datetime(df['lastSaleTime'], unit='ms')
    #df['lastUpdatedz'] = pd.to_datetime(df['lastUpdated'], unit='ms')
    #print(df)

