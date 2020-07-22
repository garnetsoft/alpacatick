$(document).ready(function() {


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
                      xhttp.open("GET", "/pricestats/dow30", true);
                      xhttp.send();
                      /* Exit the function: */
                      return;
    
                  }, 11*1000);
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
                //console.log(series)
  
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
                          //console.log(rdata)
                          //console.log('xxxx minute_data:')
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
                    xhttp.open("GET", "/pricebar/dow30", true);
                    xhttp.send();
                    /* Exit the function: */
                    return;
  
                }, 13*1000);
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
  

  // sp500 sectors -
  var sectorBubble =  Highcharts.chart('sectorBubble', {

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
                          //console.log(stats_obj)

                          bubble_series[0].setData(stats_obj[0].data)
                          bubble_series[1].setData(stats_obj[1].data)
                        }
                        if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
                        /* Remove the attribute, and call this function once more: */
                      }
                    }
                    xhttp.open("GET", "/pricestats/sector", true);
                    xhttp.send();
                    /* Exit the function: */
                    return;
  
                }, 17*1000);
            }
          } // end events  
      },

      legend: {
          enabled: true
      },

      title: {
          text: 'Intraday stats: SPY & Sectors'
      },

      accessibility: {
          point: {
              // valueDescriptionFormat: '{index}. {point.name}, fat: {point.x}g, sugar: {point.y}g, obesity: {point.z}%.'
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
              // rangeDescription: 'Range: 60 to 100 grams.'
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
        name: 'Actual',
        data: [],
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
        name: 'Relative',
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


  var sectorChart = Highcharts.chart('sectorChart', {
    chart: {        
        type: 'spline',
    
        events: {
          load: function () {
              // set up the updating of the chart periodically
              var series = this.series;
              // console.log(series)

              setInterval(function () {
                  xhttp = new XMLHttpRequest();
                  xhttp.onreadystatechange = function() {
                    if (this.readyState == 4) {
                      if (this.status == 200) {

                        // parse the last tick:
                        var rdata = JSON.parse(this.response)
                        console.log('sectorbar ajax response x:')
                        var minute_obj = JSON.parse(rdata.minute_data)
                        //console.log(minute_obj)

                        sectorChart.update({series: minute_obj}, true, true);                        

                      }
                      if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
                      
                    }
                  }
                  xhttp.open("GET", "/pricebar/sector", true);
                  xhttp.send();
                  
                  return;

              }, 19*1000);
          }
        }, // end events
    },

    title: {
        text: 'Intraday Minute Chart - SPY Sectors'
    },

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

});
