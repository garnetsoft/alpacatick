$(document).ready(function() {

    // tick chart to monitor ticks data
    var tickTopsChart = Highcharts.chart('topsChart', {
      chart: {
          //type: 'spline',
          zoomType: 'xy',
          animation: Highcharts.svg,
          //marginRight: 10,
          
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
  
                            var data = JSON.parse(rdata.tops_data)
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
  
                  }, 11*1000);  // update everython 10 seconds
              }
          }
      },
  
      time: {
          useUTC: false
      },
  
      title: {
          text: 'Real-time ticks'
      },
  
      xAxis: {
          type: 'datetime',
          tickPixelInterval: 150
      },

      yAxis: [{
          // Primary yAxis
          labels: {
            format: '{value:.2f} °F',
            style: {
                color: Highcharts.getOptions().colors[0]
            }
          },
          title: {
            text: 'AAPL',
            style: {
                color: Highcharts.getOptions().colors[0]
            }
          }        
        },
        { // Secondary yAxis
          title: {
            text: 'SPY',
            style: {
                color: Highcharts.getOptions().colors[1]
            }
          },
          labels: {
            format: '{value:.2f} °C',
            style: {
                color: Highcharts.getOptions().colors[1]
            }
          },
          opposite: true
        },
      ],

      tooltip: {
        shared: true,
        headerFormat: '<b>{series.name}</b><br/>',
        pointFormat: '{point.x:%Y-%m-%d %H:%M:%S}<br/>{point.y:.2f}'
      },
  
      legend: {
        layout: 'vertical',
        align: 'left',
        x: 120,
        verticalAlign: 'top',
        y: 100,
        floating: true,
        backgroundColor:
            Highcharts.defaultOptions.legend.backgroundColor || // theme
            'rgba(255,255,255,0.25)'
      },

      exporting: {
          enabled: true
      },
  
      // try multiple series -
      series: [
      {
        name: 'SPY',
        data: [[(new Date()).getTime(), 310.01]]
      },    
      {
        name: 'AAPL',
        yAxis: 1,
        data: [[(new Date()).getTime(), 380.01]]
      },
      {
        name: 'SPY2',
        data: [[(new Date()).getTime(), 310.09]]
      },    
      {
        name: 'AAPL2',
        yAxis: 1,
        data: [[(new Date()).getTime(), 380.09]]
      },

    ]
  
  }); // tops
    
  
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
                var data_series = {'pnl': [], 'OpeningBalance': []}

                setInterval(function () {
                    console.log('xxxx mychart series')
                    //console.log(series)

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
                          //console.log('rdata pnl x:')
                          //console.log(rdata)

                          var data = JSON.parse(rdata.data)
                          console.log('rdata pnl: ' + data.length)

                          for (var i = 0; i < data.length; i++) {
                            var pnlseries = data_series[data[i].sym]
                            //console.log('xxx pnlupdate')
                            //console.log(data[i].pnl)

                            pnlseries.push(data[i].pnl)

                            //console.log('xxx pnl')
                            //console.log(pnlseries)

                            series[i].setData(pnlseries)

                            // save init pnl -
                            if (mdata.length == 0) {
                              mdata.push(data[i].pnl)
                            }
                          }

                          // update opening balance with the same init value
                          if (mdata.length > 0) {
                            console.log('xxxx: mdata: ' + mdata)
                            init_series = data_series['OpeningBalance']
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
        text: 'Live pnl'
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

    legend: {
      layout: 'vertical',
      align: 'right',
      verticalAlign: 'middle'
    },

    exporting: {
        enabled: true
    },

    // try multiple series -
    series: [
      {
        name: 'pnl',
        data: [[(new Date()).getTime(), 50000.09]]
      },
      {
        name: 'OpeningBalance',
        data: [[(new Date()).getTime(), 50000.01]]
      },    
    ]

  });    


}); // eod-of-documary.ready()
