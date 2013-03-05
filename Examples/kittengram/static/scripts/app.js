/* jshint bitwise:true, newcap:true, noarg:true, noempty:true, curly:true, eqeqeq:true*/
/* jshint  forin:true, immed:true, latedef:true, nonew:true, undef:true, strict:true*/
/* jshint  indent:4, browser:true, undef: true*/
/* global $, _, console,WebSocket,Howl,d3 */

var app = (function ($) { // run after document load
    "use strict";
    app = this;

    var defaults = {
        sprite_size: 60,
        ws_url: null,
        animal: null,
        objid: null,
        api_url: null
    };

    var settings = {};

// http://www.freesound.org/people/Yoyodaman234/sounds/156643/
// http://www.freesound.org/people/nfrae/sounds/100032/
// Thank you, animal-loving supporters of creative-commons!

    var dog_sound_url = 'http://www.freesound.org/data/previews/100/100032_1540717-lq.mp3';
    var cat_sound_url = 'http://www.freesound.org/data/previews/156/156643_2792951-lq.mp3';

// warning, placedog.com is a little flakey.
    var table = {dog: {img_url: "http://placedog.com/",
        sound: new Howl({urls: [dog_sound_url]})},
        cat: {img_url: "http://placekitten.com/g/",
            sound: new Howl({urls: [cat_sound_url]})}};

    var pet = null;
    var ws = null;
    var dataset = null;

    function onError() {
        console.log("Oh My! an error!");
    }

    function onData(data) {
        dataset = data;
        console.log("opening ws to " + settings.ws_url);
        render();
    }

    // make with the d3
    function render() {
        var s = Math.round(200 + Math.random() * 200); // random size gives us random images
        d3.select("#furryFriends").selectAll("img").remove();
        d3.select("#furryFriends").selectAll("img")
            .data(dataset)
            .enter().append("img")
            .attr("src",function (d, i) {
                return pet.img_url + s + "/" + s;
            }).attr("width", settings.sprite_size).attr("height", settings.sprite_size)
            .attr("style", function (d, i) {
                s = "position:absolute; left:" + d[0] + "px;top:" + d[1] + "px;";
                return s;
            });

    }

    // callback for successfully opening websocket
    var onWSOpen = function () {
        console.log("websocket Opened.");
        // subscribe to channel named objid
        console.log("Sending Subscribe request to channel: " + settings.objid);
        this.send(JSON.stringify({msg_type: "SUB", channel: settings.objid}));
    };

    // callback for rx of data over websocket
    var onWSMessage = function (msg) {
        console.log("Received WS message: " + msg.data);
        var d = JSON.parse(msg.data);
        if (d.payload === "play") {
            console.log("Pet says:");

            // random delay for inevitable chorus experiment
            setTimeout(function () {
                pet.sound.play.call(pet.sound);
            }, Math.random() * 1000);
        }
        else if (d.payload === "dog" || d.payload === "cat") {
            pet = table[d.payload];
            console.log(pet);
            setTimeout(render, 0); // re-render asap
        }
    };

    var openWS = function (ws_url) {
        console.log("opening websocket to " + ws_url);

        ws = new WebSocket(ws_url);
        ws.onopen = onWSOpen;
        ws.onmessage = onWSMessage;
    };


    // public API, availabe from global namespace under app
    function start(options) {
        // override defaults with provided options
        settings = $.extend({}, defaults, options);

        pet = table[settings.animal];

        openWS(settings.ws_url, settings.objid);

        // fetch json data via AJAX
        $.getJSON(settings.api_url).done(onData).error(onError);
    }

    // return our API
    return {
        start: start,
        settings: settings
    };

})($);
