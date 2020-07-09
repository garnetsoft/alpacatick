import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


import ffn
import qpython 
from qpython import qconnection


# import options model class
from opt_model import *
from notify import *


#### stats module 
def wavg(group, val_col, wt_col='dollarValue'):
    d = group[val_col]
    w = group[wt_col]
    return (d * w).sum() / w.sum()


def rebase_series(series):
    return (series/series.iloc[0]) * 100

def get_kdbdata2(host, port, query):
    #rdb = qconnection.QConnection(host='www.aqanalytics.com', port=9001, pandas=True)
    #rdb = qconnection.QConnection(host='www.ny529s.com', port=9001, pandas=True)
    rdb = qconnection.QConnection(host=host, port=port, pandas=True)

    rdb.open()
    print('connected to Kdb service: ')
    print(rdb)
    print('xxxx query: ', query)
    df = rdb.sendSync(query)
    rdb.close()

    #df['sym'] = df['Sym'].str.decode('utf-8')
    # df = df.set_index('symbol')

    return df

def get_kdbdata(query):
    #rdb = qconnection.QConnection(host='www.aqanalytics.com', port=9001, pandas=True)
    rdb = qconnection.QConnection(host='www.ny529s.com', port=9001, pandas=True)
    #rdb = qconnection.QConnection(host=host, port=port, pandas=True)

    rdb.open()
    print('connected to Kdb service: ')
    print(rdb)
    print('xxxx query: ', query)
    df = rdb.sendSync(query)
    rdb.close()

    #df['sym'] = df['Sym'].str.decode('utf-8')
    # df = df.set_index('symbol')

    return df


def test():
    print('hahah...pyfin2')

    # $1.47
    p = Option(opt_type=OptionType.PUT, spot0=41.13, strike=40, mat=38 / 360, vol=0.38, riskless_rate=0.01)
    #print(dir(p))
    print('xxxx: p=',p)
    print('xxxx: p=',p.binomial_tree())

    # $2.66
    c = Option(opt_type=OptionType.CALL, spot0=41.13, strike=40, mat=38 / 360, vol=0.38, riskless_rate=0.02, yield_=0.0, exer_type=OptionExerciseType.AMERICAN)
    print('xxxx: c=',c.binomial_tree())

    # imp_vol
    # 38.34%
    pvol = Option.imply_volatility(1.47, opt_type=OptionType.PUT, spot0=41.13, strike=40, mat=38 / 360, riskless_rate=0.01)
    print('xxxx pvol: ', pvol)

    # 38.68%
    cvol = Option.imply_volatility(2.66, opt_type=OptionType.CALL, spot0=41.13, strike=40, mat=38/360, riskless_rate=0.01)
    print('xxxx cvol: ', cvol)

    # or 
    premium = 1.47
    opt_kwargs = {
            'opt_type': OptionType.PUT,
            'spot0': 41.13,
            'strike': 40,
            'mat': 38 / 360,
            'riskless_rate': 0.01,
        }
    #self.assertAlmostEquals(0.30, 
    c2vol = Option.imply_volatility(premium, **opt_kwargs)
    print('xxxx c2vol: ', c2vol)

### run test
# test()

#### app main ####

# load option files -
#tickers = '`spy`AAPL`ADS`TSLA`TWTR`AMZN`GE`DKNG`CVX'
tickers = list(pd.read_csv('C:/Users/gfeng/OneDrive/git/data/dow30.csv').ticker)
min_size = 100

print(f'xxxx main...tickers: {tickers}')

# myopt2:raze load_opt_hist each `spy`AAPL`ADS`TSLA`TWTR`AMZN`GE`DKNG
symbols = "`"+"`".join(tickers)
query = f'myopt2:raze load_opt_hist each {symbols}'
get_kdbdata(query)

### get latest options data
df = get_kdbdata('select from myopt2 where symbol in `{}, volume>={}, lastUpdated=max lastUpdated'.format(symbols, min_size))
df['sym'] = df['symbol'].str.decode('utf-8')

print(df.tail())

# get historical daily prices - 
print(f'xxxx get historical prices for {tickers}')
sdate = datetime.today().date() - timedelta(days=61)
#sdate.strftime('%Y-%m-%d')
prices = ffn.get(tickers, start=sdate)
print(prices.tail())

# compute historical volatility -
hist_vol = prices.pct_change().dropna().rolling(20).std()*np.sqrt(252)
hist_vol = hist_vol.dropna()
print(hist_vol.tail())


# compute imp_vol for each contract -
print(f'xxxx computing implied volatility for {len(df)} option contracts...')

imp_vol_list = []
j = 0
for i, row in df.iterrows():
    opt_type = OptionType.CALL if row['side'].decode('utf-8') == 'call' else OptionType.PUT
    
    spot0 = prices.iloc[prices.index==row['lastUpdated']][row['symbol'].decode('utf-8').lower()][-1]
    
    strike = row['strikePrice']
    mat = (row['expirationDate'] - row['lastUpdated']).days / 360
    riskless_rate = 0.01
    
    #premium = 0.5*(row['bid'] + row['ask'])
    premium = row['closingPrice']    
    #print('spot:{}, {}, {}, {}, {}, {}, {}, {}'.format(spot, i, row['symbol'].decode('utf-8'), row['side'].decode('utf-8'), row['lastUpdated'], row['expirationDate'], row['strikePrice'], row['closingPrice']))
    
    opt_kwargs = {
        'opt_type': opt_type,
        'spot0': spot0,
        'strike': strike,
        'mat': mat,
        'riskless_rate': riskless_rate,
    }

    imp_vol = Option.imply_volatility(premium, **opt_kwargs)
    imp_vol_list.append(imp_vol)
    
    if (i > 0) & (i % round(len(df)//10) == 0):
        j += 1
        print(f'$$$$ ...{j*10}% processed {i} imp_vol: {imp_vol}, inputs: {premium}, {opt_type}, {spot0}, {strike}, {mat}, {riskless_rate}')


### got all implied vol - HOW TO USE THIS?
#print('xxxx imp_vol_list: ', imp_vol_list)

impvol_file = f"/tmp/df_options_impvol_{sdate.strftime('%Y-%m-%d')}.csv"
df['imp_vol'] = imp_vol_list
df.to_csv(impvol_file)
print(df.tail())


### aggregate by symbol, side -
opt_agg = []

for expr_date, g in df.groupby(['symbol', 'side']):
    sym = expr_date[0].decode('utf-8').lower()
    hv = hist_vol.iloc[hist_vol.index == g['lastUpdated'].min()][sym].mean()
    spot = prices.iloc[prices.index == g['lastUpdated'].min()][sym][-1]
    #print(f"xxxx hv {hv}, spot: {spot}")    
    #print(f"xxxx ex: {g['lastUpdated'].min()} {expr_date}, {expr_date[1].decode('utf-8')}, {g.volume.sum()}, {g['dollarValue'].sum()}, {g['imp_vol'].mean()}, {(g['imp_vol']*g['dollarValue']).sum()/g['dollarValue'].sum()}, {wavg(g, 'strikePrice', 'dollarValue')}")

    opt_agg.append([expr_date[0].decode('utf-8'), g['lastUpdated'].min(),  expr_date[1].decode('utf-8'), spot, round(wavg(g, 'strikePrice')), g.volume.sum(), g['dollarValue'].sum(), g['imp_vol'].mean(), wavg(g, 'imp_vol'), hv])

opt_df = pd.DataFrame(opt_agg, columns=['symbol','trade_date', 'opt_type', 'spot', 'strike_level', 'volume', 'dollar_value', 'imp_vol_avg', 'imp_vol_wavg', 'hist_vol'])
opt_df['iv_hv'] = opt_df['imp_vol_wavg'] / opt_df['hist_vol']
opt_sorted = opt_df.sort_values(['symbol', 'opt_type'])
#opt_sorted = opt_df.sort_values('iv_hv')

print(opt_sorted.head())
print(opt_sorted.tail())

opt_sorted_html = opt_sorted.to_html(classes="table table-hover table-bordered table-striped",header=True)

# build a message object
msg = message(subject="", text=opt_sorted_html, img='/tmp/GS.png', attachment=impvol_file)
send(msg)  # send the email (defaults to Outlook)
