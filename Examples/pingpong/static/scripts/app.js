/* jshint bitwise:true, newcap:true, noarg:true, noempty:true, curly:true, eqeqeq:true*/
/* jshint  forin:true, immed:true, latedef:true, nonew:true, undef:true, strict:true*/
/* jshint  indent:4, browser:true, undef: true, unused: true*/
/* global $, _, console,WebSocket */

var app = (function ($) { // run after document load
    "use strict";
    app = this;

    var defaults = {
        ws_url: null,
        channel: "THE_CHANNEL"
    };

    var settings = {};
    var ws = null;

    function send_pXng(ws, X) {
        // PING or PONG
//        console.log(X + "ing");
        var msg = {msg_type: "PUB",
            payload: X,
            channel: settings.channel};
        ws.send(JSON.stringify(msg));

    }


    // callback for succesfuly opening websocket
    function onWSOpen() {
        console.log("websocket Opened.");
        // subscribe to channel named objid
        console.log("Sending Subscribe request to channel: " + settings.channel);
        ws.send(JSON.stringify({msg_type: "SUB", channel: settings.channel}));
    }


    function onWSMessage(msg) { // initial phase
        console.log("Received WS message: " + msg.data);
        var d = JSON.parse(msg.data);
        if (d.msg_type === "ACK") { // subscribe acknowledged
            ws.onmessage = pingLooper; // next message goes to the pingLooper handler
            console.log("Subscribed. PING!");
            send_pXng(ws, "PING"); // send first ping to start the ball rolling
        }
    }

    function pingLooper(msg) {
//        console.log("Received WS message: " + msg.data);
        var d = JSON.parse(msg.data);
        if (d.payload === "PING") {
//            console.log("PINGed!");
            send_pXng(ws, "PONG"); // send first ping to start the ball rolling

        } else if (d.payload === "PONG") {
            console.log("PONGed!");

            setTimeout(function () {
                console.log("PINGing!");
                send_pXng(ws, "PING"); // send first ping to start the ball rolling
            }, 1000); // rest a while, then send the next ping
        }
    }

    function openWS(ws_url) {
        console.log("opening websocket to " + ws_url);

        ws = new WebSocket(ws_url);
        ws.onopen = onWSOpen;
        ws.onmessage = onWSMessage;
    }

    // public API, availabe from global namespace under app
    function start(options) {
        // override defaults with provided options
        settings = $.extend({}, defaults, options);

        openWS(settings.ws_url, settings.objid);


    }

    // return our API
    return {
        start: start,
        settings: settings
    };
})($);

