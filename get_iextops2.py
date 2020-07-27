import pandas as pd
import numpy as np
import json
import sys
import os
import traceback
import datetime
import configparser


from datetime import datetime
from urllib.request import Request, urlopen
from pandas.io.json import json_normalize

# kdb lib
from qpython import qconnection
from qpython.qtype import QException


def get_iex_tops(url):

    print(f'{datetime.now()} iex_tops data url: {url}')

    request = Request(url)
    response = urlopen(request)
    elevations = response.read()
    data = json.loads(elevations)
    #print(f'xxxx TOPS: {data}')

    return data



# convert a list of json object to kdb obj
def create_kdb_obj(data, seq=-1):
    kobj = {}

    for idx, d in enumerate(data):
        # print(f'xxxx {idx}, d: {d}')

        for j, (k, v) in enumerate(d.items()):
            if isinstance(v, str):
                v = np.string_(v)
            else:
                v = float(v)

            kv = kobj.get(k)
            if kv:
                kv.append(v)
            else:
                kobj[k] = [v]

    #print(f'xxxx DEBUG idx={idx}, j={j}')
    kobj['seq'] = [float(seq) for x in range(idx+1)]

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


### load app config
load_app_config(sys.argv[1])


print('xxxx connect to Kdb...')

# create connection object
#q = qconnection.QConnection(host='localhost', port=5001, pandas=True)
q = qconnection.QConnection(host='localhost', port=6000, pandas=True)

q.open()
print('IPC version:%s %s. Is connected: %s' % (q, q.protocol_version, q.is_connected()))

# data table -
cols = ['symbol','sector','securityType','bidPrice','bidSize','askPrice','askSize','lastUpdated','lastSalePrice','lastSaleSize','lastSaleTime','volume']

table = 'iextops2'
iex_token = config['iex_token']


#### main ####
if __name__ == "__main__":

    tickerfile = config['ticker_file']
    tickers = list(pd.read_csv(tickerfile).ticker.unique())
    #etf = list(pd.read_csv('data/test2.csv').ticker.unique())

    symbols = ",".join(tickers)
    print(f'xxxx symbol: {symbols}')

    url=f"https://cloud.iexapis.com/stable/tops?symbols={symbols}&token={iex_token}"
    tops_data = get_iex_tops(url)
    print(tops_data)

    # to kdb
    #publish_to_rdb(tops_data, cols, table)
    #publish_to_tp(quote_data)

    try:
        seq = float(datetime.now().strftime('%H%M'))
        kobj = create_kdb_obj(tops_data, seq)
        print(kobj)

        q.sendAsync("upd", np.string_(table), kobj)

    except Exception as e:
        print('xxx processing to Kdb error: ', e)
        traceback.print_exc(file=sys.stdout)

