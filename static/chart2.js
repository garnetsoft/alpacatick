
$(document).ready(function() {

    // handle submit button
    $('#ticker_select').on('change', function() {
        //$('#submit').click();    
    });

    var update_interval = 31  // in seconds

    var ticker = $("#ticker_select option:selected").text();

    console.log($("#ticker_select").val())
    console.log('xxxx creating chart for ' + ticker)


    // get stats ranking
    setInterval(function () {    
        xhttp = new XMLHttpRequest();

        xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {

                if (this.status == 200) {

                    // parse stats data
                    //var stats = JSON.parse(this.response)
                    console.log('xxxx statsdata: ')
                    //console.log(this.response)

                    $('#stats').html(this.response);

                } // end if this.status == 200

                if (this.status == 404) {elmnt.innerHTML = "ERROR: stats data not available.";}
            }
        }

        xhttp.open("GET", "/statsdata", true);
        xhttp.send();
        
        return;  // Exit the function:

    }, 33 * 1000);



    // add all real-time charts
    $( "option" ).each(function( index, elements ) {
        console.log( index + ": " + $( this ).text() );
        //console.log( elements + ": xxxx " );

        var ticker = $(this).text()
        console.log('xxxx add NEW Chart...' + ticker)

        var txt = document.createElement("p");  // Create with DOM
        txt.innerHTML = "<hr><b>" + ticker + " Chart - created @ " + new Date() + "<b>";

        $("body").append(txt);      // Append the new elements

        // createa a div class="chart"
        $("<div/>").attr('id', ticker).attr('class', 'chart').appendTo('body');

        // backend call to get all pivot points: P0, R1/S1, R2/S2, R3/S3
        createTickerChart(ticker)        
    });


    function randint(min, max) {
        return Math.round((Math.random() * Math.abs(max - min)) + min);
    }


    function createTickerChart(ticker) {

        var namespace = '/chartdata/'+ticker
        var local_url = location.protocol + '//' + document.domain + ':' + location.port + namespace
        
        console.log('xxxx 0000 local url:')
        console.log(local_url)


        Highcharts.getJSON(local_url, function (data) {

            // console.log('xxxx OHLCV data: ')
            // console.log(data[0])

            var ohlc = [], volume = [], pivot = [];
            var P0, R1, S1;
            var minRate = 9999, maxRate = 0;
            var vwap = [], u2sd = [], d2sd = [];
            var spk_updown_ratio = []

            var predclose = -1;

            // split the data set into ohlc and volume
            var dataLength = data.length, i = 0;
            
            for (i; i < dataLength; i += 1) {
                ohlc.push([
                    data[i][0], // the date
                    data[i][1], // open
                    data[i][2], // high
                    data[i][3], // low
                    data[i][4] // close
                ]);

                
                volume.push([
                    data[i][0], // the date
                    //data[i][5] // the volume
                    data[i][13] // px move in sd
                    //data[i][5] * randint(-1, 1)
                ]);

                pivot.push([
                    data[i][0], // the date
                    data[i][6], // pivot                    
                    // data[i][13], // wopen
                    // data[i][14], // whigh
                    // data[i][15], // wlow
                    // data[i][16]  // wclose
                ])

                P0 = data[i][6]
                R1 = data[i][18]
                S1 = data[i][19]

                if (data[i][2] > maxRate) {
                    maxRate = data[i][2];
                }
                if (data[i][3] < minRate) {
                    minRate = data[i][3];
                }

                vwap.push([data[i][0], data[i][6]])
                u2sd.push([data[i][0], data[i][9]])
                d2sd.push([data[i][0], data[i][10]])

                //predclose = data[i][34]
            }

            console.log('xxxxx pivots: ')
            console.log('P0='+P0+", R1="+R1+", S1="+S1 + " xxxx predclose=="+ predclose)
            console.log('xxxxx vwap: ')
            console.log(vwap[i-1])


            // init chart -
            var rtchart = Highcharts.stockChart(ticker, {
                
                title: {
                    text: ticker + ' Intraday: ' + ohlc[ohlc.length-1][4]
                },
                        
                // subtitle: {
                //     text: 'With MACD and Pivot Points technical indicators'
                // },
                chart: {
                    marginLeft: 50,
                    //marginRight: 20
                },

                stockTools: {
                    gui: {
                        enabled: false
                    }
                },    

                rangeSelector : {
                    inputEnabled : false,
                    //allButtonsEnabled: false,
                    enabled: false
                },
                scrollbar : {
                    enabled: false
                },
                navigator: {
                    enabled: false
                },
                plotOptions: {
                    series: {
                        // general options for all series
                    },
                    bar: {
                        // shared options for all line series
                    },
                    ohlc: {
                        // shared options for all ohlc series
                    }
                },
                
                yAxis: [{
                    title: {
                        text: '<b>'+ticker+'</b>'
                    },
                    height: '65%',
                    resize: {
                        enabled: true
                    },
                    offset: 15,
                    labels: {
                        align: 'right',
                        x: -5
                    },
    
                    // add pivot lines
                    plotLines: [{
                         value: minRate,
                        //value: predclose,
                        color: 'red',
                        dashStyle: 'shortdash',
                        width: 2,
                        label: {
                            //text: 'predclose $$$$: ' + predclose
                            text: 'predclose $$$$: ' + minRate
                        }
                    }, {
                        value: maxRate,
                        color: 'green',
                        dashStyle: 'shortdash',
                        width: 2,
                        label: {
                            text: 'Intraday maximum: ' + maxRate
                        }
                    }, 
                    // {
                    //     value: vwap,
                    //     color: 'black',
                    //     dashStyle: 'shortdash',
                    //     width: 2,
                    //     label: {
                    //         text: 'Pivot'                            
                    //     }
                    // }                    
                    ]

                }, {
                    top: '65%',
                    height: '35%',
                    labels: {
                        align: 'right',
                        x: -3
                    },
                    offset: 0,
                    title: {
                        text: 'Px Vol.'
                    },

                    plotBands: [{ // Light air
                        from: 0,
                        to: 5,
                        color: 'rgba(68, 170, 213, 0.1)',
                        label: {
                            text: 'Spk up',
                            style: {
                                color: '#606060'
                            }
                        }
                    }, { // Light breeze
                        from: 0,
                        to: -5,
                        color: 'rgba(68, 170, 213, 0.1)',
                        label: {
                            text: 'Spk Down',
                            style: {
                                color: '#606060'
                            }
                        }
                    }],                    
                    
                }],
        
                tooltip: {
                    valueDecimals: 2
                },

                series: [{
                        type: 'candlestick',
                        id: 'aapl',
                        name: ticker + ' Price',
                        data: ohlc,
                        //zIndex: 1
                        tooltip: {
                            valueDecimals: 2
                        }
                    }, 
                    {
                        type: 'spline',
                        id: 'aapl-pivot',
                        name: 'vwap',
                        data: vwap,
                    }, 
                    {
                        id: 'aapl-volume',
                        name: ticker + ' Px Move in Std',
                        type: 'column',
                        data: volume,
                        yAxis: 1,
                        color: 'black',
                    },

                    {
                        type: 'spline',
                        id: 'aapl-u2sd',
                        name: 'u2sd',
                        data: u2sd,
                    }, 
                    {
                        type: 'spline',
                        id: 'aapl-d2sd',
                        name: 'd2sd',
                        data: d2sd,
                    }, 
                ],
    
            });
    
    
            console.log('xxxx init rtchart.series: ')
            console.log(rtchart.series.length)

            // rtchart.series[0].setData(ohlc)
            // rtchart.series[1].setData(pivot)
            // rtchart.series[2].setData(volume)
            
            // console.log('xxxx ohlc: ')
            // console.log(ohlc[0])        
            // console.log('xxxx volume: ')
            // console.log(volume[i-1])
            //console.log(new Date(volume[i-1][0]))


            console.log('xxxx waiting for ajax updates...')
            console.log('xxxx update_interval:')
            console.log(update_interval)
            

            // make a periodic ajax call - THIS CAN GO INTO THE CHART EVENT PROPERTY 
            setInterval(function () {
    
                elmnt =  document.getElementById('debug');
                // clear current content
                elmnt.innerHTML = "";
            
                xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4) {
    
                        if (this.status == 200) {

                            // parse OHLCV data
                            var data2 = JSON.parse(this.response)

                            console.log("COOOOOOOOOOOOOOOOOOOOOOOOOOOL")
                            
                            console.log('data2:')
                            console.log(data2[data2.length-1])    
                            // console.log(new Date(data[data.length-1][0]))
    
                            var ohlc2 = [], volatility2 = [], pivot2 = [], vwap2 = [];
                            var dataLength2 = data2.length, j = 0;
                            var ivwap = [], u2sd = [], d2sd = [];

                            var spk_updown_ratio = [];  // momentum indicator -
                            //var P0, R1, S1;
    
                            for (j; j < dataLength2; j += 1) {
                                ohlc2.push([
                                    data2[j][0], // the date
                                    data2[j][1], // open
                                    data2[j][2], // high
                                    data2[j][3], // low
                                    data2[j][4] // close
                                ]);
    
                                
                                volatility2.push([
                                    data2[j][0], // the date
                                    //data[i][5], // volume
                                    data2[j][13] // px move in sd
                                ]);

                                spk_updown_ratio.push(data2[j][0], data2[j][14])

    
                                pivot2.push([
                                    data2[j][0], // the date                                
                                    data2[j][6], // vwap       
                                ])

                                vwap2.push([
                                    data2[j][0], // the date                                
                                    data2[j][6] + 1.1, // vwap     
                                    data2[j][6] - 1.1, // vwap  
                                ])


                                ivwap.push([data2[j][0], data2[j][6]])
                                u2sd.push([data2[j][0], data2[j][9]])
                                d2sd.push([data2[j][0], data2[j][10]])

                                // update max, min intraday
                                if (data2[j][2] > maxRate) {
                                    maxRate = data2[j][2];
                                }
                                if (data2[j][3] < minRate) {
                                    minRate = data2[j][3];
                                }


                            }
    
                            console.log('xxxx 0000 ohlc2: ')
                            console.log(ohlc2[0])
                            
                            console.log('xxxx 0000 volatility2: ')
                            console.log(volatility2[j-1])
                            //console.log(new Date(volatility2[j-1][0]))
    
                            // display last update time -
                            //elmnt.innerHTML = new Date(volatility[i-1][0]);
    
    
                            // update chart, or create a Highchart panel -
                            console.log('xxxxxxxxxx ajax rtchart.series.length:')
                            console.log(rtchart.series.length)
                            console.log(rtchart.series)
    
                            // console.log(rtchart.series[0])
                            // console.log(rtchart.series[3])
                            
                            rtchart.series[1].setData(ivwap)
                            rtchart.series[3].setData(u2sd)
                            rtchart.series[4].setData(d2sd)

                            // ohlc chart on the front -
                            rtchart.series[0].setData(ohlc2)
                            rtchart.series[2].setData(volatility2)
                            //rtchart.series[1].setData(pivot2) // pivot lines -

                            // rtchart.addSeries({
                            //     title: 'vwap bband',
                            //     type: 'spline',
                            //     data: vwap2
                            // });

    
                            var lastbar = ohlc2[ohlc2.length-1]
                            var last_spk_updown_ratio = spk_updown_ratio[spk_updown_ratio.length-1]
                            console.log('xxxx spk_updown_ratio: ')
                            console.log(last_spk_updown_ratio)


                            rtchart.setTitle({ text: ticker + ' - Last: ' 
                                + lastbar[4] + ' @' 
                                + new Date(lastbar[0]).toLocaleTimeString() 
                                + ', last_spk_updown_ratio: ' + last_spk_updown_ratio });

                            console.log(ticker + ' - Last: ' 
                            + lastbar[4] + ' @' 
                            + new Date(lastbar[0]).toLocaleTimeString() 
                            + ', last_spk_updown_ratio: ' + last_spk_updown_ratio)

                            // update new maxHigh, minLow
                            var minLow = rtchart.yAxis[0].options.plotLines[0].value 
                            var maxHigh = rtchart.yAxis[0].options.plotLines[1].value 
                            //console.log('xxxxxxxxx maxHigh: ' + maxHigh)

                            if ((maxHigh != maxRate) || (minLow != minRate)) {
                                rtchart.yAxis[0].options.plotLines[0].value = minRate
                                rtchart.yAxis[0].options.plotLines[1].value = maxRate
                        
                                // rtchart.yAxis[0].options.plotLines[0].label.text = 'Intraday minimum: ' + minRate;
                                // rtchart.yAxis[0].options.plotLines[1].label.text = 'Intraday maximum: ' + maxRate;

                                rtchart.yAxis[0].plotLinesAndBands[0].label.attr({ text: 'Intraday minimum: ' + minRate });
                                rtchart.yAxis[0].plotLinesAndBands[1].label.attr({ text: 'Intraday maximum: ' + maxRate });
                                // rtchart.yAxis[0].redraw();
                            }

                        } // end if this.status == 200
    
                        if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
                    }
                }
    
                xhttp.open("GET", "/chartdata/" + ticker, true);
                xhttp.send();
                
                return;  // Exit the function:
    
            }, update_interval * 1000);  // update everython 31 seconds
    

        }); // end Highcharts.getJSON()


        console.log('XXXX tick chart created.')

    } // end createTickerChart()



    // NEW chart - test
    $('#small').click(function () {

        console.log('xxxx add NEW Chart...')

        // add a new chart panel - <div>
        var ticker = $("#ticker_select option:selected").text();
        console.log('xxxx new select ticker: '+ticker)

        var txt = document.createElement("p");  // Create with DOM
        txt.innerHTML = ticker + " Chart - created @ " + new Date();

        $("body").append(txt);      // Append the new elements

        // createa a div class="chart"
        $("<div/>").attr('id', ticker).attr('class', 'chart').appendTo('body');
        // var chartDiv = document.createElement('div');
        // chartDiv.className = 'chart';
        // document.getElementById('container').appendChild(chartDiv);

        //createTickerChart(ticker)

        var chart = $('#SPY').highcharts();

        //chart.yAxis[0].options.plotLines[1].label.text = new Date()
        // chart.yAxis[0].options.plotLines[0].label.attr({
        //     text: 'Test ' + new Date()
        // });
        chart.yAxis[0].plotLinesAndBands[1].label.attr({
            text: 'Test ' + new Date()
        });
        console.log('xxxxxxxxx Intraday maximum:: xxxx')
        console.log(chart.yAxis[0].options.plotLines[1])

    });
    
});