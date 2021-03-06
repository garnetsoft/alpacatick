$(document).ready(function() {
    // Use a "/test" namespace.

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
                //o.value = (o.value).toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
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
        selModel: 'row',
        resizable: true,
        cellHeight: 50,

        data: {
          items: signal_init
        },
        defaults: {
          type: 'string',
          width: 100,
          editable: true,

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
        }, {
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

/*
  var priceChart = Highcharts.chart('priceChart', {

      title: {
          text: 'Solar Employment Growth by Sector, 2010-2016'
      },
  
      subtitle: {
          text: 'Source: thesolarfoundation.com'
      },
  
      yAxis: {
          title: {
              text: 'Number of Employees'
          }
      },
  
      xAxis: {
          accessibility: {
              rangeDescription: 'Range: 2010 to 2017'
          }
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
              pointStart: 2010
          }
      },
  
      series: [{
          name: 'Installation',
          data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
      }, {
          name: 'Other',
          data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
      }],
  
      responsive: {
          rules: [{
              condition: {
                  maxWidth: 500
              },
              chartOptions: {
                  legend: {
                      layout: 'horizontal',
                      align: 'center',
                      verticalAlign: 'bottom'
                  }
              }
          }]
      }

  });

  
var bubbleChart =  Highcharts.chart('bubbleChart', {

      chart: {
          type: 'bubble',
          plotBorderWidth: 1,
          zoomType: 'xy'
      },

      legend: {
          enabled: false
      },

      title: {
          text: 'Sugar and fat intake per country'
      },

      subtitle: {
          text: 'Source: <a href="http://www.euromonitor.com/">Euromonitor</a> and <a href="https://data.oecd.org/">OECD</a>'
      },

      accessibility: {
          point: {
              valueDescriptionFormat: '{index}. {point.name}, fat: {point.x}g, sugar: {point.y}g, obesity: {point.z}%.'
          }
      },

      xAxis: {
          gridLineWidth: 1,
          title: {
              text: 'Daily fat intake'
          },
          labels: {
              format: '{value} gr'
          },
          plotLines: [{
              color: 'black',
              dashStyle: 'dot',
              width: 2,
              value: 65,
              label: {
                  rotation: 0,
                  y: 15,
                  style: {
                      fontStyle: 'italic'
                  },
                  text: 'Safe fat intake 65g/day'
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
              text: 'Daily sugar intake'
          },
          labels: {
              format: '{value} gr'
          },
          maxPadding: 0.2,
          plotLines: [{
              color: 'black',
              dashStyle: 'dot',
              width: 2,
              value: 50,
              label: {
                  align: 'right',
                  style: {
                      fontStyle: 'italic'
                  },
                  text: 'Safe sugar intake 50g/day',
                  x: -10
              },
              zIndex: 3
          }],
          accessibility: {
              rangeDescription: 'Range: 0 to 160 grams.'
          }
      },

      tooltip: {
          useHTML: true,
          headerFormat: '<table>',
          pointFormat: '<tr><th colspan="2"><h3>{point.country}</h3></th></tr>' +
              '<tr><th>Fat intake:</th><td>{point.x}g</td></tr>' +
              '<tr><th>Sugar intake:</th><td>{point.y}g</td></tr>' +
              '<tr><th>Obesity (adults):</th><td>{point.z}%</td></tr>',
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
          data: [
              { x: 95, y: 95, z: 13.8, name: 'BE', country: 'US' },
              { x: 86.5, y: 102.9, z: 14.7, name: 'DE', country: 'UK' },
              { x: 64, y: 82.9, z: 31.3, name: 'CN', country: 'China' }
          ]
      }]

  });
*/
  

    // An application can open a connection on multiple namespaces, and
    // Socket.IO will multiplex all those connections on a single
    // physical channel. If you don't care about multiple channels, you
    // can set the namespace to an empty string.
    namespace = '/test';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
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
        /*
        if (typeof msg.prices_series !== 'undefined') {
          console.log('priceChart:')

          var priceSeries = JSON.parse(msg.prices_series)
          priceChart.update({series: priceSeries}, true, true);
          console.log(priceChart.series[0].data)

          // update bubbleChart -
          bubbleChart.update({series: bubble}, true, true);
          console.log(bubbleChart.series[0].data)

        }
        $('#debug').text(priceChart.series);
        */


        // $('#log').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
        $('#log').html(msg.signals_html);
        $('#signals_rank_long').html(msg.signals_rank_long);
        $('#signals_rank_short').html(msg.signals_rank_short);

        // update grid
        signalGrid.setTitle(msg.time)

        if (typeof msg.signal !== 'undefined') {
          var dobj = JSON.parse(msg.signal)

          if (dobj.length > 0) {  
            // var grid = FancyGrid.get('test');
            signalGrid.setData(dobj)
            signalGrid.update()
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


var signal_init = [
  {"id":476,  "qtm": "2020-05-21 19:26:13.758", "sym":"AAPL", "price":[125.78,125.85,125.92,125.91,125.92],"src":"http://ny529s.com/logo/AAPL.png","volume":86180.0, "ps":[2, 1, 5, 4], "tick": 7.7, "signal": "Long"},
  {"id":1001, "qtm": "2020-05-21 19:26:13.758", "sym":"XOM",  "price":[85.05,85.075,85.075,85.135,85.135], "src":"http://ny529s.com/logo/XOM.png"," volume":79866.0, "ps":[2, 5, 1, 4], "tick": 8.8, "signal": "Short"}
]


// sym	qtm	n	open	mn	mu	md	mx	dv	vwap	close	chg	volume	l2dv	r2dv, ps
var summary_init = [
  {"id": 0, "sym":"xxx", "qtm": "2020-05-21 19:26:13.758", "n":0, "open":0.99, "mn":0.99, "mu":0.99, "md":0.99, "mx":0.99, "dv":0.99, "vwap":0.99, "close":0.99, "chg":0.99, "volume":7, "l2dv": 95.5, "r2dv": 105.0, "atr": 0, "price":[5, 4, 3, 2, 1] , "pbox":[5, 4, 3, 2, 1], "ps":[2, 1, 5, 4] }, 
  {"id": 7, "sym":"yyy", "qtm": "2020-05-21 19:26:13.758", "n":0, "open":0.99, "mn":0.99, "mu":0.99, "md":0.99, "mx":0.99, "dv":0.99, "vwap":0.99, "close":0.99, "chg":0.99, "volume":7, "l2dv": 95.5, "r2dv": 105.0, "atr": 0, "price":[1, 2, 3, 4, 5] , "pbox":[1, 2, 3, 4, 5], "ps":[2, 1, 5, 4] }, 
];


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


var series2 = [{
  name: 'XXXXXXXXx',
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
