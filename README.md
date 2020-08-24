"# alpaca data" 


8/20/2020:

/ 
 opt thursday short model:
   - on Thursday, sell ATM call, put for next week's Friday Exp.
   - check daily return till next Thursday's close and hold to expiration returns.
\

opt_thursday_short:{[d;s]
 / s:`AAPL;d:2020.08.13
 expdate:d+8;
 dclose:select from ohlc2 where sym=s, Date=d;
 pxclose:max exec Close from dclose;
 pxcsk:first exec strikePrice from (select from opt where symbol=s, side=`call, lastUpdated=d, expirationDate=expdate, strikePrice>=pxclose );
 shortcall:(update D:m[d] from update d:lastUpdated mod 7, sym:symbol, Date:lastUpdated from (select from opt where symbol=s, lastUpdated>=d, expirationDate=expdate, strikePrice=pxcsk, side=`call  ) );
 shortcallandclose:shortcall lj `sym`Date xkey (`sym`Date`Open`High`Low`Close`Volume`sigma#select from ohlc2 where sym=s, Date>=d);
 callret:update ret:log(closingPrice%prev closingPrice) from shortcallandclose;
 callret
 }


wow:raze {opt_thursday_short[2020.07.16;x] } each exec distinct symbol from  select by symbol from opt

wow

select count i, avg ret, closingPrice wavg ret by Date, D from wow



Go to %systemroot%\System32\drivers\etc
Backup the hosts file
Then open notepad with administrator rights.
Navigate to the same folder and open the hosts file
Make sure the first line after the # lines (comments) is 127.0.0.1 localhost and the second is ::1 localhost
Then open cmd and run the command ipconfig /flushdns
Restart the browser or whatever program you are using.


8/19/2020:

$(function () {
    $('#container').highcharts({

        chart: {
            type: 'boxplot'
        },

        title: {
            text: 'Highcharts Box Plot Example'
        },

        legend: {
            enabled: false
        },

        xAxis: {
            categories: ['1', '2', '3', '4', '5'],
            title: {
                text: 'Experiment No.'
            }
        },

        yAxis: {
            title: {
                text: 'Observations'
            },
            plotLines: [{
                value: 932,
                color: 'red',
                width: 1,
                label: {
                    text: 'Theoretical mean: 932',
                    align: 'center',
                    style: {
                        color: 'gray'
                    }
                }
            }]
        },

        series: [{
            name: 'Observations',
            data: [
                [760, 801, 848, 895, 965],
                [733, 853, 939, 980, 1080],
                [714, 762, 817, 870, 918],
                [724, 802, 806, 871, 950],
                [834, 836, 864, 882, 910]
            ],
            tooltip: {
                headerFormat: '<em>Experiment No {point.key}</em><br/>'
            }
        }]

    });

    $('#btn').click(function () {
        var chart = $('#container').highcharts();

        chart.yAxis[0].plotLinesAndBands[0].options.value = 950;
        chart.yAxis[0].plotLinesAndBands[0].options.width = 10;
        chart.yAxis[0].plotLinesAndBands[0].label.attr({
            text: 'Test'
        });

        chart.yAxis[0].redraw();
    });
});


var chart = Highcharts.chart('container', {

    xAxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    },

    series: [{
        data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4]
    }]
});


// the button action
var hasPlotBand = false,
    $button = $('#button');

$button.click(function () {
    if (!hasPlotBand) {
        chart.xAxis[0].addPlotBand({
            from: 5.5,
            to: 7.5,
            color: '#FCFFC5',
            id: 'plot-band-1'
        });

        chart.yAxis[0].addPlotBand({
            from: -100,
            to: -200,
            color: '#FCFFC5',
            id: 'plot-band-1'
        });
                
        $button.html('Remove plot band');
    } else {
        chart.xAxis[0].removePlotBand('plot-band-1');
        $button.html('Add plot band');
    }
    hasPlotBand = !hasPlotBand;
});


// add multiple series at once -

    seriesOptions[i] = {
        name: name,
        data: data  // list of [[t1, 101], ...[tn, 101*n]]
    };

function createChart() {

    Highcharts.stockChart('container', {

        rangeSelector: {
            selected: 4
        },

        yAxis: {
            labels: {
                formatter: function () {
                    return (this.value > 0 ? ' + ' : '') + this.value + '%';
                }
            },
            plotLines: [{
                value: 0,
                width: 2,
                color: 'silver'
            }]
        },

        plotOptions: {
            series: {
                compare: 'percent',
                showInNavigator: true
            }
        },

        tooltip: {
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
            valueDecimals: 2,
            split: true
        },

        series: seriesOptions
    });
}


            chart.addSeries({
                linkedTo: 'aapl-ohlc',
                type: type,
                params: {
                    period: parseInt(period, 10)
                }
            });


            var chartDiv = document.createElement('div');
            chartDiv.className = 'chart';
            document.getElementById('container').appendChild(chartDiv);

            // create a new chart in chartDiv -
            Highcharts.chart(chartDiv, {});


8/16/2020:

Train a model, build a front-end application around it with Streamlit, get the application working locally (on your computer), once it’s working wrap the application with Docker, then deploy the Docker container to Heroku or another cloud provider.


8/12/2020:

$(document).ready(function() {
   $('#cars').change(function() {
     var parentForm = $(this).closest("form");
     if (parentForm && parentForm.length > 0)
       parentForm.submit();
   });
});


var defaultData = 'https://demo-live-data.highcharts.com/time-data.csv';
var urlInput = document.getElementById('fetchURL');
var pollingCheckbox = document.getElementById('enablePolling');
var pollingInput = document.getElementById('pollingTime');

function createChart() {
    Highcharts.chart('container', {
        chart: {
            type: 'spline'
        },
        title: {
            text: 'Live Data'
        },
        accessibility: {
            announceNewData: {
                enabled: true,
                minAnnounceInterval: 15000,
                announcementFormatter: function (allSeries, newSeries, newPoint) {
                    if (newPoint) {
                        return 'New point added. Value: ' + newPoint.y;
                    }
                    return false;
                }
            }
        },
        data: {
            csvURL: urlInput.value,
            enablePolling: pollingCheckbox.checked === true,
            dataRefreshRate: parseInt(pollingInput.value, 10)
        }
    });

    if (pollingInput.value < 1 || !pollingInput.value) {
        pollingInput.value = 1;
    }
}

urlInput.value = defaultData;

// We recreate instead of using chart update to make sure the loaded CSV
// and such is completely gone.
pollingCheckbox.onchange = urlInput.onchange = pollingInput.onchange = createChart;

// Create the chart
createChart();


var seriesOptions = [],
    seriesCounter = 0,
    names = ['MSFT', 'AAPL', 'GOOG'];

/**
 * Create the chart when all data is loaded
 * @returns {undefined}
 */
function createChart() {

    Highcharts.stockChart('container', {

        rangeSelector: {
            selected: 4
        },

        yAxis: {
            labels: {
                formatter: function () {
                    return (this.value > 0 ? ' + ' : '') + this.value + '%';
                }
            },
            plotLines: [{
                value: 0,
                width: 2,
                color: 'silver'
            }]
        },

        plotOptions: {
            series: {
                compare: 'percent',
                showInNavigator: true
            }
        },

        tooltip: {
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
            valueDecimals: 2,
            split: true
        },

        series: seriesOptions
    });
}

function success(data) {
    var name = this.url.match(/(msft|aapl|goog)/)[0].toUpperCase();
    var i = names.indexOf(name);
    seriesOptions[i] = {
        name: name,
        data: data
    };

    // As we're loading the data asynchronously, we don't know what order it
    // will arrive. So we keep a counter and create the chart when all the data is loaded.
    seriesCounter += 1;

    if (seriesCounter === names.length) {
        createChart();
    }
}

Highcharts.getJSON(
    'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/msft-c.json',
    success
);
Highcharts.getJSON(
    'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/aapl-c.json',
    success
);
Highcharts.getJSON(
    'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/goog-c.json',
    success
);

08/10/2020: 

var chart = Highcharts.chart('container', {
       title: {
              text: 'My chart'
       },
       series: [{
           data: [1, 3, 2, 4]
       }]
})

<form class="form-inline" method="POST" action="{{ url_for('test') }}">
  <div class="form-group">
    <div class="input-group">
        <span class="input-group-addon">Please select</span>
            <select name="comp_select" class="selectpicker form-control">
              {% for o in data %}
              <option value="{{ o.name }}">{{ o.name }}</option>
              {% endfor %}
            </select>
    </div>
    <button type="submit" class="btn btn-default">Go</button>
  </div>
</form>


https://bost.ocks.org/mike/bubble-map/


def wavg(val_col_name,wt_col_name):
    def inner(group):
        return (group[val_col_name] * group[wt_col_name]).sum() / group[wt_col_name].sum()
    inner.__name__ = 'wgt_avg'
    return inner



d = {"P": pd.Series(['A','B','A','C','D','D','E'])
     ,"Q": pd.Series([1,2,3,4,5,6,7])
    ,"R": pd.Series([0.1,0.2,0.3,0.4,0.5,0.6,0.7])
     }

df = pd.DataFrame(d)
print df.groupby('P').apply(wavg('Q','R'))

P
A    2.500000
B    2.000000
C    4.000000
D    5.545455
E    7.000000
dtype: float64


https://medium.com/@gfeng22/asset-price-volatility-methods-to-compute-it-8bf395babc1


(Growth expectations were measured using the company’s market-to-book ratio. High market-to-book companies were considered growth companies, and low market-to-book companies were considered value companies.)


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
