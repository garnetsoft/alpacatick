"# alpaca data" 

import logging
import platform
import requests

logger = logging.getLogger(__name__)
SESSION = requests.Session()

2020-07-06 09:23:45,398 INFO     [97%] 230/237 fragments fetched
XXXX remote_file_url: https://zk.sd-dykj.com/2020/06/19/RYlhrKFHPctJ2fcN/out234.ts
XXXX remote_file_url: https://zk.sd-dykj.com/2020/06/19/RYlhrKFHPctJ2fcN/out235.ts
XXXX remote_file_url: https://zk.sd-dykj.com/2020/06/19/RYlhrKFHPctJ2fcN/out236.ts

subprocess call -

    target_mp4 = self.output_filename
    if not target_mp4.endswith(".mp4"):
        target_mp4 += ".mp4"
    cmd = ["ffmpeg",
            "-loglevel", "warning",
            "-allowed_extensions", "ALL",
            "-i", self.media_playlist_localfile,
            "-acodec", "copy",
            "-vcodec", "copy",
            # "-bsf:a", "aac_adtstoasc",
            target_mp4]
    logger.info("Running: %s", cmd)
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        logger.error("run ffmpeg command failed: exitcode=%s",
                        proc.returncode)
        sys.exit(proc.returncode)
    logger.info("mp4 file created, size=%.1fMiB, filename=%s",
                filesizeMiB(target_mp4), target_mp4)
    logger.info("Removing temp files in dir: \"%s\"", self.tempdir)
    if os.path.exists("/bin/rm"):
        subprocess.run(["/bin/rm", "-rf", self.tempdir])
    elif os.path.exists("C:/Windows/SysWOW64/cmd.exe"):
        subprocess.run(["rd", "/s", "/q", self.tempdir], shell=True)
    logger.info("temp files removed")
    


http://www.timestored.com/kdb-guides/python-api

q).z.ws:{neg[.z.w] .Q.s @[value;x;{`$"'",x}]}

let nodeq = require("node-q");

nodeq.connect({host: "codycent", port: 8080}, (err, con) => {
if (err) throw err;
console.log("connected");
// interact with con like demonstrated below

con.k("returnTable 3", (err, res) => {
if (err) throw err;
console.log("result:", res); // 6
});
});

and by running it we see result similar to below:


$node test.js
connected
result: [ { x: 0, y: 'a' }, { x: 1, y: 'b' }, { x: 2, y: 'c' } ]


Listen to a handle
con.k(function(err, res) {
	if (err) throw err;
	console.log("result", res);
});

Subscribe to kdb+tick
con.on("upd", function(table, data) {
	console.log(table, data);
});

con.ks(".u.sub[`;`]", function(err) { // subscribe to all tables and all symbols
	if (err) throw err;
});

Close connection
con.close(function() {
	console.log("con closed");
});


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
