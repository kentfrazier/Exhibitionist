/* jshint bitwise:true, newcap:true, noarg:true, noempty:true, curly:true, eqeqeq:true*/
/* jshint  forin:true, immed:true, latedef:true, nonew:true, undef:true, strict:true*/
/* jshint  indent:4, browser:true, undef: true, unused: true*/
/* global $, _, console,WebSocket */

var app = (function ($, _) { // run after document load
    "use strict";
    app = this;

    var defaults = {
        ws_url: null,
        objid: null,
        api_url: null
    };

    var settings = {};
    var ws = null;

    // private
    function onError(req, status, errThrown) {
        console.log("alas, 'tis a shame!");
        console.log(req, status, errThrown);
    }

    function onData(data) {
        // when data is recieved , put it in the "#container" div
        console.log("Got JSON data: " + data.payload);
        $("#container").html(data.payload);
    }

     // callback for incoming data on websocket
    function onWSMessage (msg) {
        console.log("websocket Message received: " + msg.data);
        var d = JSON.parse(msg.data);

    }

    // callback for succesfuly opening websocket
    function onWSOpen () {
        console.log("websocket Opened.");
        // subscribe to channel named objid
        console.log("Sending Subscribe request to channel: " + settings.objid);
        ws.send(JSON.stringify({msg_type: "SUB", channel: settings.objid}));
    }

    function openWS (ws_url) {
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

        // fetch json data via AJAX
        $.getJSON(settings.api_url).done(onData).error(onError);
    }

    // return our API
    return {
        start: start,
        settings: settings
    };
})($, _);

