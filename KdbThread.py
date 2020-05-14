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


from qpython import qconnection
from qpython.qcollection import qlist
from qpython.qtype import QException, QTIME_LIST, QSYMBOL_LIST, QFLOAT_LIST


# utils
def get_table_columns(q, table_name):
    try:
        return [x.decode('utf-8') for x in q('cols {}'.format(table_name))]
    except Exception as e:
        print('load_kdb_tables error: ', e)

    return None


# kdb+ data thread 
class KdbThread(Thread):

    def __init__(self, config, queue):
        super(KdbThread, self).__init__()
        self.config = config
        self.queue = queue

        # init q conn
        self._initq()
        self._stopper = threading.Event()

        self.count = 0

    # init q service - start if not running
    def _initq(self):
        try:
            h = self.config.get('kdb_host', 'localhost')
            p=int(self.config.get('kdb_port', '5001'))

            print(f'xxxx connecting to q: {h}:{p}')            
            self.q = qconnection.QConnection(host=h, port=p)
            self.q.open()

            print('IPC version:%s %s. Is connected: %s' % (self.q, self.q.protocol_version, self.q.is_connected()))
            # send a handshake message
            print('xxxx kdb time: ', self.q('.z.Z'))

        except Exception as e:
            print('init Q error: ', e)


    def stop(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def process(self, message):
        try:
            #print(f'xxxx got wss msg: {type(message)} {message}')

            # send to kdb, raw and specific tables, T/Q/AM
            #cols = get_table_columns(self.q, self.config['table'])

            # note: np.string_("haha") makes string a symbol type
            # save raw json msg, let q process it
            #self.q.sendAsync("{y insert x}", np.string_(message), np.string_("raw"))
            #self.q.sendAsync("{data:.j.k x; y insert enlist data}", message, np.string_("evt"))
            self.q.sendAsync("upd", np.string_("raw"), np.string_(message))

            if 1 < 2:
                return
                
            # now update trade and quote -
            msg_json = json.loads(message)
            #print('xxxx json obj: {}, {}'.format(type(msg_json), msg_json))

            stream = msg_json['stream']
            data = msg_json['data']
            kobj = [np.string_(stream), np.string_(str(data))]        
            #print(f'xxxx $$$$ {kobj}')
            self.q.sendAsync("upd", np.string_("evt"), kobj)

            # trade:flip `ev`T`i`x`p`s`t`c`z!"**fffff*f"$\:()
            # quote:flip `ev`T`x`p`s`X`P`S`c`t!"**ffffff*f"$\:()

            msg_type = stream[:2]
            msg_type = "XX"
            #print('xxxx DEBUG msg_type: ', msg_type)
            if msg_type == "T.":
                #self.q.sendAsync("{data:.j.k x; y insert enlist data[`data]}", message, np.string_("trade"))
                trade = [np.string_(str(data[x])) if isinstance(data[x], str) or isinstance(data[x], list) else data[x] for x in ['ev', 'T', 'i', 'x', 'p', 's', 't', 'c', 'z'] ]
                #print(trade)
                self.q.sendAsync("upd", np.string_("trade"), trade)

            elif msg_type == "Q.":
                #self.q.sendAsync("{data:.j.k x; y insert enlist data[`data]}", message, np.string_("quote"))
                quote = [np.string_(str(data[x])) if isinstance(data[x], str) or isinstance(data[x], list) else data[x] for x in ['ev', 'T', 'x', 'p', 's', 'X', 'P', 'S', 'c', 't'] ]
                #print(quote)
                self.q.sendAsync("upd", np.string_("quote"), quote)


        except Exception as e:
            print('xxx processing to Kdb error: ', e)


    def update_count(self, n):
        self.count += n

        if self.count % int(self.config['count']) == 0:
            print(f'XXXX processed {self.count} kdb records')        


    def process_trades(self, messages):
        try:
            self.q.sendAsync("upd", np.string_("raw"), np.string_("|".join([m for m in messages])))

            # trades 
            evt_list = []
            symbol_list = []
            id_list = []
            ex_list = []
            price_list = []
            size_list = []
            tms_list = []
            cond_list = []
            tape_list = []
            
            for message in messages:
                msg_json = json.loads(message)
                data = msg_json['data']

                # get trade field from data
                # ['ev', 'T', 'i', 'x', 'p', 's', 't', 'c', 'z']                
                evt_list.append(data['ev'])
                symbol_list.append(data['T'])
                id_list.append(float(data['i']))
                ex_list.append(float(data['x']))
                price_list.append(float(data['p']))
                size_list.append(float(data['s']))
                tms_list.append(float(data['t']))
                cond_list.append(str(data['c']))
                tape_list.append(float(data['z']))

            kobj = [np.string_(evt_list), np.string_(symbol_list), id_list, ex_list, price_list, size_list, tms_list, cond_list, tape_list]        
            #print(f'xxxx $$$$ {kobj}')
            self.q.sendAsync("upd", np.string_("trade"), kobj)

            self.update_count(len(messages))

        except Exception as e:
            print('xxx processing to Kdb error: ', e)


    def process_quotes(self, messages):
        try:
            self.q.sendAsync("upd", np.string_("raw"), np.string_("|".join([m for m in messages])))
            
            # trades 
            evt_list = []
            symbol_list = []
            exbid_list = []
            bid_list = []
            bsize_list = []
            exask_list = []
            ask_list = []            
            asize_list = []
            cond_list = []
            tms_list = []
            
            for message in messages:
                msg_json = json.loads(message)
                data = msg_json['data']

                # get quote field from data
                # ['ev', 'T', 'x', 'p', 's', 'X', 'P', 'S', 'c', 't'] 
                evt_list.append(data['ev'])
                symbol_list.append(data['T'])
                exbid_list.append(float(data['x']))
                bid_list.append(float(data['p']))
                bsize_list.append(float(data['s']))
                exask_list.append(float(data['X']))
                ask_list.append(float(data['P']))
                asize_list.append(float(data['S']))
                cond_list.append(str(data['c']))
                tms_list.append(float(data['t']))

            kobj = [np.string_(evt_list), np.string_(symbol_list), exbid_list, bid_list, bsize_list, exask_list, ask_list, asize_list, cond_list, tms_list]        
            #print(f'xxxx $$$$ {kobj}')
            self.q.sendAsync("upd", np.string_("quote"), kobj)

            self.update_count(len(messages))

        except Exception as e:
            print('xxx processing to Kdb error: ', e)


    def run(self):
        print('xxxx kdb data thread starting...',self.stopped())
        
        #while not self.stopped():
        while True:
            try:
                # items = [q.get() for _ in range(q.qsize())]
                if self.queue.empty():
                    continue

                ticks = [ self.queue.get() for _ in range(self.queue.qsize()) ]
                # tick = self.queue.get()
                #print('xxxx Kdb thread got ticks: ', len(ticks))

                # batching -
                if self.config['stream'] == 'trade':
                    self.process_trades(ticks)
                elif self.config['stream'] == 'quote':
                    self.process_quotes(ticks)

                if self.stopped():
                    break

            except Exception as e:
                print(e)
                time.sleep(0.2)
            except:
                self.stop()

        print('xxxx closing kdb connection...')
        self.q.close()

        print('xxxx kdb data thread exiting...')