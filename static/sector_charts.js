$(document).ready(function() {

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
                          console.log(stats_obj)

                          //bubble_series[0].setData(stats_obj[0].data)
                          bubble_series[1].setData(stats_obj[1].data)
                        }
                        if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
                        /* Remove the attribute, and call this function once more: */
                      }
                    }
                    xhttp.open("GET", "/sectorstats", true);
                    xhttp.send();
                    /* Exit the function: */
                    return;
  
                }, 14*1000);
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
                  xhttp.open("GET", "/sectorbar", true);
                  xhttp.send();
                  
                  return;

              }, 13*1000);
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
