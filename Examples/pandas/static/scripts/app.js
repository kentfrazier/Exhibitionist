/* jshint bitwise:true, newcap:true, noarg:true, noempty:true, curly:true, eqeqeq:true*/
/* jshint  forin:true, immed:true, latedef:true, nonew:true, undef:true, strict:true*/
/* jshint  indent:4, browser:true, undef: true*/
/* global $, _, console, WebSocket */

var app = (function ($) { // run after document load
    "use strict";
    app = this;

    var defaults = {
        objid: null,
        api_url: null
    };

    var settings = {};

    var req = null;

    function reportError(err) {
        console.log("Error fetching columns");
    }

    function BuildColumnsDescriptor(resp) {
        // resp contains the columns data from the server
        // construct jqGrid-specific data structure

        // default values
        var defaultCol = {
            is_index: false,
            cssClass: "",
            formatter: null,
            width: 80,
            aligh: "left"
        };

        // column headings, list of strings
        var colNames = resp.columns.map(function (item) {
            // item.name is a (possibly singleton) list of strings, one per
            // level of the column index.
            // HACK: Use <br/> to display multlevel columns as several rows of
            // header text.
            return item.name.join("<br/>") + "<br/>";
        });

        // list of col_descriptor(name,index,width,align,frozen,classes),
        // others supported by jqGrid
        var colModel = [];
        for (var i in resp.columns) {
            if (resp.columns.hasOwnProperty(i)) {
                var item = $.extend({}, defaultCol, resp.columns[i]);
                item.id = item.id || String(i);
                item.name = String(i);

                var d = {name: item.name, index: String(i),
                    width: item.width, align: item.align};

                if (item.is_index) {
                    // manually set the classes used by the header, to visually
                    // identify this as an index column.
                    d = $.extend(d, {frozen: true, classes: "ui-state-default jqgrid-rownum"});
                }
                colModel.push(d);
            }
        }

        return {colNames: colNames, colModel: colModel};

    }

    function instantiateGrid(columns) {
        // columns is an object containing keys 'colNames','colModel'

        var $grid = $("#myGrid");

        $grid.jqGrid({
            url: settings.rows_api_url,
            datatype: "json",
            colNames: columns.colNames,
            colModel: columns.colModel,
            rowNum: 10,
            width: 690,
            rowList: [10, 20, 50, 100],
            pager: '#pager',
            sortname: '0',
            viewrecords: true,
            sortorder: "desc",
            jsonReader: {
//                    root:function (obj) {
//                        // console.log(obj)
//                        // manipulate request data HERE
//                        return obj.rows
//                    },
                repeatitems: false
            },
            shrinkToFit: false, // needed for frozen columns
            rownumbers: true,
            // 0-based row numbers: https://github.com/tonytomov/jqGrid/pull/426
            rownumbersBase: 0,
            caption: "Pandas DataFrame",
            loadComplete: function () {
                fixPositionsOfFrozenDivs.call(this);
            },
            height: "250px" //'auto'

        });

        $grid.jqGrid('navGrid', '#pager', {refresh: true, add: false,
            del: false, search: false,
            edit: false});

        $grid.jqGrid('setFrozenColumns');


        // HACKS for various issues


        // http://stackoverflow.com/questions/7246506
        // http://stackoverflow.com/questions/8564198

        // front-end development. just shoot me.
        fixPositionsOfFrozenDivs.call($grid[0]);

        // fix resizing of frozen columns
        var headerRow, rowHeight, resizeSpanHeight;

        // get the header row which contains
        headerRow = $grid.closest("div.ui-jqgrid-view")
            .find("table.ui-jqgrid-htable>thead>tr.ui-jqgrid-labels");

        // increase the height of the resizing span
        resizeSpanHeight = 'height: ' + headerRow.height() +
            'px !important; cursor: col-resize;';
        headerRow.find("span.ui-jqgrid-resize").each(function () {
            this.style.cssText = resizeSpanHeight;
        });

        // set position of the div with the column header text to the middle
        rowHeight = headerRow.height();
        headerRow.find("div.ui-jqgrid-sortable").each(function () {
            var ts = $(this);
            ts.css('top', (rowHeight - ts.outerHeight()) / 2 + 'px');
        });

        // https://github.com/tonytomov/jqGrid/issues/42
        // when using 'gridResize', the hide/show folding
        // of the grid doesn't work properly, but leaves
        // a frame outline behind
        $('.HeaderButton').click(function () {
            var el = $('#gbox_myGrid');
            if (el.attr('data-status') !== 'hidden' || el.attr('data-status') === undefined) {
                el.attr('data-status', 'hidden');
                el.css({ 'height': 'auto' });
            } else {
                el.attr('data-status', 'active');
                el.css({ 'height': 'auto' });
            }
        });
        $grid.jqGrid('gridResize');

        // when frozen columns + gridResize are in use
        // using the resize handle to reduce the height of the
        // grid doesn't resize the frozen columns
        //
        // HACK: hook the resize event and trigger a reload
        // on the nextmouseUp event
        var reloadOnMouseUp = false;

        $("#gbox_myGrid").bind("resize", function (event, ui) {
            reloadOnMouseUp = true;
        });

        $(document).mouseup(function () {
            if (reloadOnMouseUp) {
                $grid.trigger("reloadGrid");
                reloadOnMouseUp = false;
            }
        });


        // Included $.jqGrid.js was modified with
        //  https://github.com/tonytomov/jqGrid/pull/426
        //  https://github.com/tonytomov/jqGrid/pull/427
    }

    var fixPositionsOfFrozenDivs = function () {
        if (typeof this.grid.fbDiv !== "undefined") {
            $(this.grid.fbDiv).css($(this.grid.bDiv).position());
        }
        if (typeof this.grid.fhDiv !== "undefined") {
            $(this.grid.fhDiv).css($(this.grid.hDiv).position());
        }
    };


    // public API, availabe from global namespace under app
    function start(options) {
        // override defaults with provided options
        settings = $.extend({}, defaults, options);
        // api url is the endpoint sans trailing slash
        settings.cols_api_url = (settings.api_url + "/columns/" + settings.objid);
        settings.rows_api_url = (settings.api_url + "/rows/" + settings.objid);

        // success: AJAX(cols_api_url) -> BuildColumnsDescriptor(resp) -> instantiateGrid(columns)
        // fail:    AJAX(cols_api_url) -> reportError
        req = $.ajax(settings.cols_api_url)
            .then(BuildColumnsDescriptor, reportError)
            .done(instantiateGrid);

    }

    // return our API
    return {
        start: start,
        settings: settings
    };
})($);
