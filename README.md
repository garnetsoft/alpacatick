"# alpaca data" 

pandas data cleaning:

https://github.com/Kyrand/dataviz-with-python-and-js

https://www.kyrandale.com/static/pyjsdataviz/

Part II: Create your Virtual Environment

python3 -m venv my_environment
source my_environment/bin/activate
pip install flask pandas plotly gunicorn


query = '0!select tm:qtm, price:lastSalePrice by sym:symbol from update qtm:"j"$(lastSaleTimez-1970.01.01D)%1000000 from select from iextops where symbol in `SPY`AAPL, lastSaleTimez.minute>=13:30'
df = get_kdbdata2('aq101', 6001, query)

data_json = [{'name':row.sym.decode('utf-8'), 'data':list(map(list, zip(row['tm'].astype(int), row['price'])))} for i, row in df.iterrows()]
data_json


iexquote:flip`symbol`companyName`primaryExchange`calculationPrice`open`openTime`openSource`close`closeTime`closeSource`high`highTime`highSource`low`lowTime`lowSource`latestPrice`latestSource`latestTime`latestUpdate`latestVolume`iexRealtimePrice`iexRealtimeSize`iexLastUpdated`delayedPrice`delayedPriceTime`oddLotDelayedPrice`oddLotDelayedPriceTime`extendedPrice`extendedChange`extendedChangePercent`extendedPriceTime`previousClose`previousVolume`change`changePercent`volume`iexMarketPercent`iexVolume`avgTotalVolume`iexBidPrice`iexBidSize`iexAskPrice`iexAskSize`iexOpen`iexOpenTime`iexClose`iexCloseTime`marketCap`peRatio`week52High`week52Low`ytdChange`lastTradeTime`isUSMarketOpen!"****ff*ff*ff*ff*f**fffffffffffffffffffffffffffffffffffb"$\:();

iexquote2:flip `symbol`companyName`primaryExchange`calculationPrice`open`openTime`openSource`latestPrice`latestSource`latestTime`latestUpdate`latestVolume`iexRealtimePrice`iexRealtimeSize`iexLastUpdated`iexMarketPercent`iexVolume`avgTotalVolume`iexBidPrice`iexBidSize`iexAskPrice`iexAskSize`iexOpen`iexOpenTime`iexClose`iexCloseTime`marketCap!"****ff*f**fffffffffffffffff"$\();


def publish_to_kdb(self, df):
    # load json into dataframe
    df = df.reset_index(drop=True)

    try:
        # kdb data obj
        kdf = df[self.cols]
        self.q.sendAsync('{y insert x}', kdf, np.string_(self.table))

        if self.debug:
            print('$$$$ KKKK debug insert data in kdb: ', kdf)

    except Exception as e:
        print('xxx processing to Kdb error: ', e)
        traceback.print_exc(file=sys.stdout)


def upd_kdb_dict(self, data):
    if self.debug:
        print('$$$$ KKKK {} debug insert data in kdb: {}'.format(datetime.now(), data))

    try:
        self.q.sendAsync('{t:update sym:`$sym, time:"Z"$time from enlist .j.k x; y insert t}',
                            data, np.string_(self.table))

        if self.debug:
            print('xxxx debug sent json data to kdb: ', data)

    except Exception as e:
        print('xxx processing to Kdb error: ', e)
        traceback.print_exc(file=sys.stdout)
