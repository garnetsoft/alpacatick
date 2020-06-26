$(document).ready(function() {
    // Use a "/test" namespace.

    var tickTopsChart = Highcharts.chart('topsChart', {
      chart: {
          type: 'spline',
          animation: Highcharts.svg, // don't animate in old IE
          marginRight: 10,
          events: {
              load: function () {
                  console.log('xxxx topsChart events:')
                  console.log(this.series)
  
                  // set up the updating of the chart each second
                  //var series = this.series[0];
                  var series = this.series;
                  var series_len = series.length
                  
                  elmnt =  document.getElementById('debug');
                  // clear current content
                  elmnt.innerHTML = "";

                  setInterval(function () {

                      xhttp = new XMLHttpRequest();
                      xhttp.onreadystatechange = function() {
                        if (this.readyState == 4) {
                          if (this.status == 200) {
                            //console.log('xxxx ajax res:')
                            //console.log(this)
                            console.log('xxxx topsChart ajax responseText:')
                            //console.log(this.responseText)
    
                            // parse the last tick:
                            var rdata = JSON.parse(this.response)
                            console.log('topsChart rdata x:')
                            //console.log(rdata)
  
                            var data = JSON.parse(rdata.tops_data20)
                            console.log('topsChart data:')
                            //console.log(data)

                            // for (var i = 0, len = data.length; i < len; i++) {
                            //   series[i].setData(data[i])
                            // }
                            
                            tickTopsChart.update({series: data}, true, true);
                          }

                          if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
                        }
                      }
                      xhttp.open("GET", "/tickupdate2", true);
                      xhttp.send();
                      /* Exit the function: */
                      return;
  
                  }, 61*1000);  // update everython 10 seconds
              }
          }
      },
  
      time: {
          useUTC: false
      },
  
      title: {
          text: 'SPY real-time'
      },
  
      xAxis: {
          type: 'datetime',
          tickPixelInterval: 150
      },
  
      yAxis: {
          title: {
              text: 'Value'
          },
          plotLines: [{
              value: 0,
              width: 1,
              color: '#808080'
          }]
      },
  
      tooltip: {
          headerFormat: '<b>{series.name}</b><br/>',
          pointFormat: '{point.x:%Y-%m-%d %H:%M:%S}<br/>{point.y:.2f}'
      },
  
      legend: {
        layout: 'vertical',
        align: 'right',
        verticalAlign: 'middle'
      },
  
      exporting: {
          enabled: false
      },
  
      // try multiple series -
      series: [
      {
        name: 'AAPL',
        data: [[(new Date()).getTime(), 300.09]]
      },
      {
        name: 'SPY',
        data: [[(new Date()).getTime(), 300.01]]
      },    
      ]
  
  }); // tickTops
    
  
  // pnl chart
  var tickChart = Highcharts.chart('mychart', {
    chart: {
        type: 'spline',
        animation: Highcharts.svg, // don't animate in old IE
        marginRight: 10,
        events: {
            load: function () {
                console.log('xxxx mychart events:')
                console.log(this.series)

                // set up the updating of the chart each second
                //var series = this.series[0];
                var series = this.series;
                var mdata = []
                var data_series = {'XXX': [], 'AAPL': []}

                setInterval(function () {
                    console.log('xxxx mychart series')
                    console.log(series)

                    // Make an HTTP request
                    // document.getElementById('dynamic_content').innerText = new Date().toUTCString();
                    elmnt =  document.getElementById('debug');
                    // clear current content
                    elmnt.innerHTML = "";

                    xhttp = new XMLHttpRequest();
                    xhttp.onreadystatechange = function() {
                      if (this.readyState == 4) {
                        if (this.status == 200) {
                          //console.log('xxxx ajax res:')
                          //console.log(this)
                          console.log('xxxx ajax responseText:')
                          console.log(this.responseText)

                          elmnt.innerHTML = this.responseText;

                          // parse the last tick:
                          var rdata = JSON.parse(this.response)
                          console.log('rdata pnl x:')
                          console.log(rdata)

                          var data = JSON.parse(rdata.data)
                          console.log('rdata pnl: ' + data.length)

                          for (var i = 0; i < data.length; i++) {
                            var pnlseries = data_series[data[i].sym]
                            console.log('xxx pnlupdate')
                            console.log(data[i].pnl)

                            pnlseries.push(data[i].pnl)

                            //console.log('xxx pnl')
                            //console.log(pnlseries)

                            series[i].setData(pnlseries)

                            // save init pnl -
                            if (mdata.length == 0) {
                              mdata.push(data[i].pnl)
                            }
                          }

                          if (mdata.length > 0) {
                            console.log('xxxx: mdata: ' + mdata)
                            init_series = data_series['AAPL']
                            init_series.push([(new Date()).getTime(), mdata[0][1] ])
                            //console.log(init_series)

                            series[1].setData(init_series)
                          }

                          // data.forEach(function(o) {
                          //   tickdata = data_series.get(o.sym)
                          //   tickdata.push([o.qtm, o.price])
                          // });
                          // for (var i = 0; i < data.length; i++) {
                          //   var tickdata = data[i]
                          //   var mdata = data_series[tickdata.sym]

                          //   var qtm = tickdata['qtm']
                          //   var kdbtime = tickdata['kdbtime']
                          //   var wstime = tickdata['wstz']

                          //   console.log('xxxx time check: ')

                          //   if (i > 0) {
                          //     mdata.push([qtm, tickdata['price']])
                          //   }
                          //   else {
                          //     // use wstime to know if any market data delay
                          //     mdata.push([wstime, tickdata['price']])
                          //   }
                            
                          //   series[i].setData(mdata)
                          // }

                        }
                        if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
                        /* Remove the attribute, and call this function once more: */
                      }
                    }
                    xhttp.open("GET", "/pnlupdate", true);
                    xhttp.send();
                    /* Exit the function: */
                    return;

                }, 31*1000);  // update everython 10 seconds
            }
        }
    },

    time: {
        useUTC: false
    },

    title: {
        text: 'PnL'
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

    xAxis: {
        type: 'datetime',
        tickPixelInterval: 150
    },

    yAxis: {
        title: {
            text: 'Value'
        },
        plotLines: [{
            value: 0,
            width: 1,
            color: '#808080'
        }]
    },

    tooltip: {
        headerFormat: '<b>{series.name}</b><br/>',
        pointFormat: '{point.x:%Y-%m-%d %H:%M:%S}<br/>{point.y:.2f}'
    },

    // legend: {
    //     enabled: false
    // },
    legend: {
      layout: 'vertical',
      align: 'right',
      verticalAlign: 'middle'
    },

    exporting: {
        enabled: false
    },

    // try multiple series -
    series: [
      {
        name: 'XXX',
        data: [[(new Date()).getTime(), 50000.09]]
      },
      {
        name: 'AAPL',
        data: [[(new Date()).getTime(), 50000.01]]
      },    
    ]

  });    


  var summaryGrid = new FancyGrid({
      title: 'Summary',
      renderTo: 'summary',
      width: 'fit',
      height: 'fit',
      resizable: true,
      trackOver: true,
      selModel: 'row',

      footer: {
        status: '<span style="position: relative;top: 3px;">*</span> - Stock intraday stats:',
        source: {
          text: 'AQ Analytics',
          link: 'ny529s.com'
        }
      },        
      data: {
          items: summary_init,
          // fields:['sym', 'qtm', 'n', 'open', 'mn', 'mu', 'md', 'mx', 'dv', 'vwap', 'close', 'price', 'atr', 'chg', 'volume', 'l2dv', 'r2dv']
      },
      defaults: {
          type: 'string',
          width: 100,
          editable: false,
          sortable: true,
      },

      columns: [
        {
          type: 'number',
          title: 'id',
          index: 'id',
        },
        //2020-05-21 19:26:13.758
        {
          type: 'text',
          title: 'qtm',
          index: 'qtm',
          width: 150,
        },
        {
          type: 'number',
          title: 'n',
          index: 'n',
        },

        {
          type: 'number',
          title: 'open',
          index: 'open',
        },
        {
          type: 'number',
          title: 'mn',
          index: 'mn',
        },
        {
          type: 'number',
          title: 'mu',
          index: 'mu',
          render: renderPriceFn,
        },
        {
          type: 'number',
          title: 'md',
          index: 'md',
        },
        {
          type: 'number',
          title: 'mx',
          index: 'mx',
        },
        {
          type: 'number',
          title: 'vwap',
          index: 'vwap',
          //render: renderPriceFn,
          render: function(o) {
              o.value = (o.value).toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
              //o.value = '$$' + (o.value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
              return o;
          }
        },
        {
          type: 'number',
          title: 'dv',
          index: 'dv',
          render: renderPriceFn,
        },
        {
          type: 'number',
          title: 'close',
          index: 'close',
          render: renderCloseFn,
        },
        {
          type: 'text',
          title: 'sym',
          index: 'sym',
        },
        {
          title: 'price',
          type: 'sparklineline',
          index: 'price',
          width: 200,
          sparkConfig: {
            barColor: '#60B3E2'
          }
        },
        {
          title: 'pbox',
          type: 'sparklinebox',
          index: 'price',
          width: 150,
          sparkConfig: {
            barColor: '#60B3E2'
          }
        },
        {
          title: 'P-OH/LC',
          type: 'sparklineline',
          index: 'ps',
          width: 100,
          sparkConfig: {
            barColor: '#60B3E2'
          }
        },
        {
          type: 'number',
          title: 'chg',
          index: 'chg',
          cellAlign: 'right',
          render: renderChangesFn,
        },
        {
          type: 'number',
          title: 'atr',
          index: 'atr',
          sortable: true,            
          render: renderAtrFn,
        },          
        {
          type: 'number',
          title: 'volume',
          index: 'volume',
          cellAlign: 'right',
          format: 'number',            
        },
        {
          type: 'number',
          title: 'l2dv',
          index: 'l2dv',
          render: renderPriceFn,
        },
        {
          type: 'number',
          title: 'r2dv',
          index: 'r2dv',
          render: renderPriceFn,
        },

      ]

  });

    
  // create a fancygrid var
  var signalGrid = new FancyGrid({
      title: 'Trading Stats',
      renderTo: 'signal',
      width: 'fit',
      height: 'fit',
      trackOver: true,
      //resizable: true,
      selModel: 'row',
      cellHeight: 50,
      
      footer: {
        status: '<span style="position: relative;top: 3px;">*</span> - Live Trading Sinagls (last 5)',
        source: {
          text: 'AQ Analytics',
          link: 'ny529s.com'
        }
      },
      data: {
        items: signal_init
      },
      defaults: {
        type: 'string',
        width: 100,
        editable: false,
        sortable: true,
      },
      //clicksToEdit: 1,
      columnLines: false,

      columns: [{
        type: 'number',
        title: 'ID',
        index: 'id',
        width: 100,
        sortable: true,
        locked: true,
        //cls: 'id-column-cls'
      },
      {
        type: 'number',
        title: 'Count',
        index: 'count',
        width: 80,
        sortable: true,
        locked: true,
      },        
      {
        type: 'text',
        title: 'qtm',
        index: 'qtm',
        width: 150,
      }, {
        type: 'image',
        title: 'Company',
        index: 'src',
        width: 80,
        resizable: true,
        autoHeight: true,
        cls: 'photo'
      }, {
        title: 'Ticker',
        index: 'sym',
        resizable: true,
        width: 140,
        type: 'text',
        render: function(o) {
  
          o.style = {
            'font-size': '14px'
          };
  
          return o;
        }
      }, 
      {
        title: 'Prices',
        type: 'sparklineline',
        index: 'price',
        width: 350,
        sparkConfig: {
          barColor: '#60B3E2'
        }
      },
      {
          title: 'Box',
          type: 'sparklinebox',
          index: 'price',
          width: 150,
          sparkConfig: {
            barColor: '#60B3E2'
          }
      },
      {
        title: 'Volume',
        index: 'volume',
        type: 'number',
        sortable: true,
        cellAlign: 'right',
        format: 'number',
      },
      {
          title: 'O(H/L)C',
          type: 'sparklineline',
          index: 'ps',
          width: 150,
          sparkConfig: {
            barColor: '#60B3E2'
          }
      },
      {
          title: 'Last tick',
          index: 'tick',
          type: 'number',
          //sortable: true,
          //cellAlign: 'right',
          format: 'number',
          render: function(o) {
            if (o.data.signal == 'Mom_Long') {
              o.style = {
                color: '#65AE6E',
                'font-size': '14px'
              };
            } else {
              o.style = {
                color: '#E46B67',
                'font-size': '14px'
              };
            }

            return o;
          }
        },
        {
          title: 'Signal',
          index: 'signal',
          resizable: true,
          width: 200,
          type: 'text',
          render: function(o) {
    
            if (o.value == 'Mom_Long') {
              o.style = {
                color: '#65AE6E',
                'font-size': '14px'
              };
            } else {
              o.style = {
                color: '#E46B67',
                'font-size': '14px'
              };
            }

            return o;
          }
        },
      ]
  });


  var bubbleChart =  Highcharts.chart('bubbleChart', {

      chart: {
          type: 'bubble',
          plotBorderWidth: 1,
          zoomType: 'xy',

          events: {
            load: function () {
                var bubble_series = this.series;
  
                setInterval(function () {
                    // ajax request -
                    xhttp = new XMLHttpRequest();
                    xhttp.onreadystatechange = function() {
                      if (this.readyState == 4) {
                        if (this.status == 200) {
  
                          // parse the last tick:
                          var rdata = JSON.parse(this.response)
                          console.log('stats ajax response x:')
                          //console.log(rdata)
  
                          // override the chart with entire new series
                          console.log('xxxx stats_data:')
                          var stats_obj = JSON.parse(rdata.stats_data)
                          console.log(stats_obj)

                          bubble_series[0].setData(stats_obj[0].data)
                          bubble_series[1].setData(stats_obj[1].data)
                        }
                        if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
                        /* Remove the attribute, and call this function once more: */
                      }
                    }
                    xhttp.open("GET", "/statsbar2", true);
                    xhttp.send();
                    /* Exit the function: */
                    return;
  
                }, 63*1000);
            }
          } // end events  
      },

      legend: {
          enabled: true
      },

      title: {
          text: 'Intraday stats: DOW 30'
      },

      // subtitle: {
      //     text: 'Source: <a href="http://www.euromonitor.com/">Euromonitor</a> and <a href="https://data.oecd.org/">OECD</a>'
      // },

      accessibility: {
          point: {
              valueDescriptionFormat: '{index}. {point.name}, fat: {point.x}g, sugar: {point.y}g, obesity: {point.z}%.'
          }
      },

      xAxis: {
          gridLineWidth: 1,
          title: {
              text: 'Sharpe'
          },
          labels: {
              format: '{value} '
          },
          plotLines: [{
              color: 'black',
              dashStyle: 'dot',
              width: 2,
              value: 0,
              label: {
                  rotation: 0,
                  y: 15,
                  style: {
                      fontStyle: 'italic'
                  },
                  text: 'avg. sharpe'
              },
              zIndex: 3
          }],
          accessibility: {
              rangeDescription: 'Range: 60 to 100 grams.'
          }
      },

      yAxis: {
          startOnTick: false,
          endOnTick: false,
          title: {
              text: 'Total return'
          },
          labels: {
              format: '{value} '
          },
          maxPadding: 0.2,
          plotLines: [{
              color: 'black',
              dashStyle: 'dot',
              width: 2,
              value: 0,
              label: {
                  align: 'right',
                  style: {
                      fontStyle: 'italic'
                  },
                  text: 'avg. return',
                  x: -10
              },
              zIndex: 3
          }],
          accessibility: {
              //rangeDescription: 'Range: 0 to 160 grams.'
          }
      },

      tooltip: {
          useHTML: true,
          headerFormat: '<table>',
          pointFormat: '<tr><th colspan="2"><h3>{point.name}</h3></th></tr>' +
              '<tr><th>Sharpe:</th><td>{point.x:,.2f} </td></tr>' +
              '<tr><th>Return:</th><td>{point.y:,.2f} </td></tr>' +
              '<tr><th>Volatility:</th><td>{point.z:,.2f}%</td></tr>',
          footerFormat: '</table>',
          followPointer: true
      },

      plotOptions: {
          series: {
              dataLabels: {
                  enabled: true,
                  format: '{point.name}'
              }
          }
      },

      series: [{
        name: 'SeriesA',
        data: [
            { x: 95, y: 95, z: 13.8, name: 'US', country: 'US' },
            { x: 86.5, y: 102.9, z: 14.7, name: 'UK', country: 'UK' },
            { x: 64, y: 82.9, z: 31.3, name: 'CN', country: 'China' }
        ],
        marker: {
          fillColor: {
              radialGradient: { cx: 0.4, cy: 0.3, r: 0.7 },
              stops: [
                  [0, 'rgba(255,255,255,0.5)'],
                  [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0.5).get('rgba')]
              ]
          }
        }        
      }, {
        name: 'Watchlist',
        data: [
        ],
        marker: {
          fillColor: {
              radialGradient: { cx: 0.4, cy: 0.3, r: 0.7 },
              stops: [
                  [0, 'rgba(255,255,255,0.5)'],
                  [1, Highcharts.color(Highcharts.getOptions().colors[1]).setOpacity(0.5).get('rgba')]
              ]
          }
        }        
      }]

  });


  var minuteChart = Highcharts.chart('minuteChart', {
    chart: {
        type: 'spline',

        events: {
          load: function () {
              // set up the updating of the chart each second
              var series = this.series;
              console.log(series)

              setInterval(function () {
                  // Make an HTTP request
                  // document.getElementById('dynamic_content').innerText = new Date().toUTCString();

                  xhttp = new XMLHttpRequest();
                  xhttp.onreadystatechange = function() {
                    if (this.readyState == 4) {
                      if (this.status == 200) {

                        // parse the last tick:
                        var rdata = JSON.parse(this.response)
                        console.log('minutebar ajax response x:')
                        console.log(rdata)
                        console.log('xxxx minute_data:')
                        //console.log(rdata.minute_data)

                        var minute_obj = JSON.parse(rdata.minute_data)
                        //console.log(minute_obj)

                        minuteChart.update({series: minute_obj}, true, true);                        
                        //series[0].update({series: minute_obj}[0], true, true);
                        //series[1].update({series: minute_obj}[1], true, true);                          
                        //series[0].setData(minute_obj[0])
                        //series[1].setData(minute_obj[1])
                        // minuteChart.redraw()

                      }
                      if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
                      /* Remove the attribute, and call this function once more: */
                    }
                  }
                  xhttp.open("GET", "/minutebar", true);
                  xhttp.send();
                  /* Exit the function: */
                  return;

              }, 67*1000);
          }
        },

      // end events        

    },
    title: {
        text: 'Intraday Minute Chart - Dow30'
    },
    // subtitle: {
    //     text: 'Irregular time data in Highcharts JS'
    // },
    xAxis: {
        type: 'datetime',
        tickPixelInterval: 150,
        dateTimeLabelFormats: {
            //month: '%e. %b',
            year: '%b',
            hour: '%H:%M',
        },
        title: {
            text: 'Time'
        }
    },
    yAxis: {
        title: {
            text: 'Prices (normalized)'
        },
        //min: 0
    },
    tooltip: {
        headerFormat: '<b>{series.name}</b><br/>',
        pointFormat: '{point.x:%H:%M:%S}<br/>{point.y:.2f}'        
    },

    legend: {
      layout: 'vertical',
      align: 'right',
      verticalAlign: 'middle'
    },

    plotOptions: {
      series: {
          label: {
              connectorAllowed: false
          },
          marker: {
              enabled: false
          }          
      }
    },

    // create minute bar series -
    // exec (`SPY`AAPL)#sym!price by minute from 0!select last price by sym, 5 xbar qtm.minute from trade where sym in `SPY`AAPL
    // [{"name": s, "data": list(map(list, zip([datetime.strptime(str(x)[-8:], '%H:%M:%S') for x in mdata.index], mdata))) } for s, mdata in df.items()]

    series: [
      {
        name: 'SPY',
        data: [[(new Date()).getTime(), 300.09]]
      },
      {
        name: 'AAPL',
        data: [[(new Date()).getTime(), 300.01]]
      },    
    ],

    responsive: {
        rules: [{
            condition: {
                maxWidth: 500
            },
            chartOptions: {
                plotOptions: {
                    series: {
                        marker: {
                            radius: 2.5
                        }
                    }
                }
            }
        }]
    }
  });
  

  // An application can open a connection on multiple namespaces, and
  // Socket.IO will multiplex all those connections on a single
  // physical channel. If you don't care about multiple channels, you
  // can set the namespace to an empty string.
  namespace = '/test2';

  // Connect to the Socket.IO server.
  // The connection URL has the following format:
  //     http[s]://<domain>:<port>[/<namespace>]
  console.log('xxxx 0000:')
  console.log(location.protocol + '//' + document.domain + ':' + location.port + namespace)

  // KICK OF THE BACKGROUND THREAD IN SOCKETIO
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

  // Event handler for new connections.
  // The callback function is invoked when a connection with the
  // server is established.
  socket.on('connect', function() {
    socket.emit('my_event', {data: 'I\'m connected!'});
  });

  // Interval function that tests message latency by sending a "ping"
  // message. The server then responds with a "pong" message and the
  // round trip time is measured.
  var ping_pong_times = [];
  var start_time;
  var s = '[';
  window.setInterval(function() {
    start_time = (new Date).getTime();
    socket.emit('my_ping');
    
    // DO SOMETHING HERE -
  }, 30000);

  // Handler for the "pong" message. When the pong is received, the
  // time from the ping is stored, and the average of the last 30
  // samples is average and displayed.
  socket.on('my_pong', function() {
    var latency = (new Date).getTime() - start_time;
    ping_pong_times.push(latency);
      ping_pong_times = ping_pong_times.slice(-10); // keep last 30 samples
      var sum = 0;
      for (var i = 0; i < ping_pong_times.length; i++)
        sum += ping_pong_times[i];

      $('#ping-pong').text(Math.round(10 * sum / ping_pong_times.length) / 10);
      $('#latency').text(ping_pong_times.join(", "));
  });


  // Event handler for server sent data.
  // The callback function is invoked whenever the server emits data
  // to the client. The data is then displayed in the "Received"
  // section of the page.
  // var signal_hist = [];
  socket.on('my_response', function(msg) {
      // show a flashing banner -

      // console.log(priceChart)
      // console.log(priceChart.series)

      //priceChart.setSeriesData(series2)
      //priceChart.update({})

      if (typeof msg.prices_series !== 'undefined') {

        //console.log('priceChart:')
        //var priceSeries = JSON.parse(msg.prices_series)
        //priceChart.update({series: priceSeries}, true, true);
        //console.log(priceChart.series[0].data)

        // update bubbleChart -
        //bubbleChart.update({series: bubble}, true, true);
        //console.log(bubbleChart.series[0].data)

        //console.log('xxxx minute_json:')
        //console.log(msg.minute_json)
        //var minute_obj = JSON.parse(msg.minute_json)
        //console.log(minute_obj)
        //minuteChart.update({series: minute_obj}, true, true);
      }


      $('#debug').text(priceChart.series);

      // $('#log').html(msg.signals_html);
      $('#log').append('<br>' + $('<div/>').text('positions allowed #' + msg.positions_allowed).html());

      $('#signals_rank_long').html(msg.signals_rank_long);
      $('#signals_rank_short').html(msg.signals_rank_short);

      $('#orders_hist_html').html(msg.orders_hist_html);      
      $('#live_positions_html').html(msg.live_positions_html);

      // update grid
      signalGrid.setTitle(msg.time)

      if (typeof msg.signal !== 'undefined') {
        var dobj = JSON.parse(msg.signal)

        if (dobj.length > 0) {  
          // var grid = FancyGrid.get('test');
          signalGrid.setData(dobj)
          signalGrid.update()

          //signalGrid.flashRow(1);
        }
        else {
          // update title ONLY -
          // last_update_time = Date.parse(signalGrid.getTitle())
          // time_passed = Date.parse(msg.time) - last_update_time
          // signalGrid.updateSubtitle(str(time_passed))
        }
      }

      // console.log('yyyy')
      // console.log(typeof(grid.getData()))

      if (typeof msg.summary !== 'undefined') {
          //console.log('xxxx: '+msg.time)

          summary_data = JSON.parse(msg.summary)
          // console.log(msg.summary)
          // console.log(summary_data)

          summaryGrid.setData(summary_data)
          //summaryGrid.flashRow(5)
          summaryGrid.update()

          //$('#container').text(JSON.stringify(grid2.getData()))
      }

  });

  // Handlers for the different forms in the page.
  // These accept data from the user and send it to the server in a
  // variety of ways
  $('form#emit').submit(function(event) {
    socket.emit('my_event', {data: $('#emit_data').val()});
    return false;
  });
  $('form#broadcast').submit(function(event) {
    socket.emit('my_broadcast_event', {data: $('#broadcast_data').val()});
    return false;
  });

  $('form#disconnect').submit(function(event) {
    socket.emit('disconnect_request');
    return false;
  });

});


// global functions
var renderChangesFn = function(o) {
    //console.log('yyyy: ')
    //console.log(o)
    //console.log(o.data)

    if (o.value < 0) {
      o.style = {
        color: '#E46B67'
      };
    } else {
      o.style = {
        color: '#65AE6E'
      };
    }
  
    //o.value = o.value + '%';
    o.value = o.value + ' ticks';    
  
    return o;
};


var renderPriceFn = function(o) {
    if (o.value) 
        o.value = (o.value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');

    return o;
};


var renderAtrFn = function(o) {
    if (o.data.dv > 0) {
        dvmv = o.data.atr / o.data.dv
        o.value = dvmv.toFixed(2) + ' sdev'
    }
    else
        o.value = '0 sdev'

    return o;
};


var renderCloseFn = function(o) {
    //console.log('yyyy: ')
    //console.log(o.data)

    if (o.data.close < o.data.l2dv) {
      o.style = {
        color: '#E46B67',
        'font-size': '14px',
      };
    } else if (o.data.close > o.data.r2dv) {
      o.style = {
        color: '#65AE6E',
        'font-size': '14px'
      };
    }
    else {
        o.style = {
            color: 'black',
            'font-size': '12px'
          };    
    }
  
    return o;
};

function formatNumber(num) {
  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}

function currencyFormat(num) {
  return '$' + num.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}



var signal_init = [
  {"id":476, "count": 0, "qtm": "2020-05-21 19:26:13.758", "sym":"AAPL", "price":[125.78,125.85,125.91,125.92,125.92],"src":"http://ny529s.com/logo/AAPL.png","volume":86180.0, "ps":[2, 1, 5, 5], "tick": 7.7, "signal": "Long"},
  {"id":1001, "count": 1,"qtm": "2020-05-21 19:26:13.758", "sym":"XOM",  "price":[85.05,85.135,85.135,85.075,85.075], "src":"http://ny529s.com/logo/XOM.png"," volume":79866.0, "ps":[2, 5, 1, 1], "tick": 8.8, "signal": "Short"}
]


// sym	qtm	n	open	mn	mu	md	mx	dv	vwap	close	chg	volume	l2dv	r2dv, ps
var summary_init = [
  {"id": 0, "sym":"xxx", "qtm": "2020-05-21 19:26:13.758", "n":0, "open":0.99, "mn":0.99, "mu":0.99, "md":0.99, "mx":0.99, "dv":0.99, "vwap":0.99, "close":0.99, "chg":0.99, "volume":7, "l2dv": 95.5, "r2dv": 105.0, "atr": 0, "price":[5, 4, 3, 2, 1] , "pbox":[5, 4, 3, 2, 1], "ps":[2, 1, 5, 4] }, 
  {"id": 7, "sym":"yyy", "qtm": "2020-05-21 19:26:13.758", "n":0, "open":0.99, "mn":0.99, "mu":0.99, "md":0.99, "mx":0.99, "dv":0.99, "vwap":0.99, "close":0.99, "chg":0.99, "volume":7, "l2dv": 95.5, "r2dv": 105.0, "atr": 0, "price":[1, 2, 3, 4, 5] , "pbox":[1, 2, 3, 4, 5], "ps":[2, 1, 5, 4] }, 
];


var series2 = [{
  name: 'XXXXX',
  data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
}, {
  name: 'ZZZZZ',
  data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
}];

var bubble = [{
  data: [
    { x: 71, y: 93.2, z: 24.7, name: 'UK', country: 'United Kingdom' },
    { x: 69.2, y: 57.6, z: 10.4, name: 'IT', country: 'Italy' },
    { x: 68.6, y: 20, z: 16, name: 'RU', country: 'Russia' },
  ]
}]
