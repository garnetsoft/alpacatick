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
          {
            type: 'text',
            title: 'sym',
            index: 'sym',
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
          type: 'image',
          title: 'Logo',
          index: 'src',
          width: 80,
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
    var signal_hist = [];
    socket.on('my_response', function(msg) {
        // show a flashing banner -
        // $('#log').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
        if (typeof msg.signal !== 'undefined') {
          var dobj = JSON.parse(msg.signal)

          console.log('tttt: ', typeof(msg.time))
          console.log(msg.time)
          var qtime = Date.parse(msg.time)
          console.log('qqqq: ', typeof(qtime))
          console.log(qtime)

          var last_signal_time = signalGrid.getTitle()
          console.log('xxxx: ', typeof(last_signal_time))
          console.log(last_signal_time)

          if (dobj.length > 0) {
            signal_hist.push(msg.signals_html)
            signal_hist = signal_hist.slice(-5)
            
            // console.log('xxxx')
            // console.log(signal_hist)
            signal_reversed = signal_hist.reverse() 
            $('#log').html(signal_reversed);
  
            // var grid = FancyGrid.get('test');
            signalGrid.setTitle(msg.time);
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
  {"id":476,"sym":"WMT","price":[125.78,125.85,125.92,125.91,125.92],"src":"http://ny529s.com/logo/WMT.png","volume":86180.0, "ps":[2, 1, 5, 4], "tick": 7.7, "signal": "Long"},
  {"id":1002,"sym":"WYNN","price":[85.05,85.075,85.075,85.135,85.135],"src":"http://ny529s.com/logo/GS.png","volume":79866.0, "ps":[2, 5, 1, 4], "tick": 8.8, "signal": "Short"}
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
