/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 110, indent: 4 */
/*jslint sub: true */
/*globals window navigator document */
/*globals setTimeout clearTimeout setInterval */
/*globals Slick alert */


(function ($) {

    // Proxy a minimal but necessary part of jquery-ui
    // XX TODO, move this to somewhere on its own at some point?
    $.ui = $.ui || {};
    if (!$.ui.version) {
        $.extend($.ui, {
            keyCode:{
                BACKSPACE:8,
                COMMA:188,
                DELETE:46,
                DOWN:40,
                END:35,
                ENTER:13,
                ESCAPE:27,
                HOME:36,
                LEFT:37,
                NUMPAD_ADD:107,
                NUMPAD_DECIMAL:110,
                NUMPAD_DIVIDE:111,
                NUMPAD_ENTER:108,
                NUMPAD_MULTIPLY:106,
                NUMPAD_SUBTRACT:109,
                PAGE_DOWN:34,
                PAGE_UP:33,
                PERIOD:190,
                RIGHT:39,
                SPACE:32,
                TAB:9,
                UP:38
            }
        });
    }


    function _safeConvert(obj) {
        var type = $.type(obj);
        if (type == 'object' && $(obj).parent().length > 0) {
            obj = "DOM #" + $(obj).attr('id');
        } else if (type == 'array' || type == 'object') {
            var res;
            if (type == 'array') {
                res = [];
            } else {
                res = {};
            }
            $.each(obj, function (key, value) {
                res[key] = _safeConvert(value);
            });
            obj = res;
        }
        return obj;
    }

    function log() {
        var args = [new Date()];
        var i;
        for (i = 0; i < arguments.length; i++) {
            args.push(arguments[i]);
        }
        args = _safeConvert(args);
        var repr = JSON.stringify(args);
        $('#logger').prepend('<code>' + repr + '</code><br>');
    }

    window.log = log;

    function requiredFieldValidator(value) {
        if (value === null || value === undefined || !value.length) {
            return {valid:false, msg:"This is a required field"};
        }
        else {
            return {valid:true, msg:null};
        }
    }


    function locateCell(grid, evt) {
        // There is something strange going on with the event targets here. We would like
        // to get the target (typically a <div class="slick-cell" />), but that does not seem
        // to be correct. Using originalEvent is good though.
        var realEvt = evt.originalEvent || evt;
        var target = $(realEvt.target);
        var res;
        if (target.parent().is('.slick-header-columns')) {
            var column = target.index();
            res = {
                target:target,
                type:'header',
                column:column
            };
        } else {
            // Find out the row and column of the cell
            var cell = grid.getCellFromEvent(realEvt);
            if (cell !== null) {
                // We are in the canvas.
                res = {
                    target:target,
                    type:'cell',
                    row:cell.row,
                    column:cell.cell
                };
            } else {
                // We are not in the canvas.
                res = {
                    type:'outside'
                };
            }
        }
        return res;
    }

    var dataView;
    var grid;
    var data = [];
    var columns = [
/*
        {id:"sel", name:"#", field:"num", behavior:"select",
            cssClass:"cell-selection", width:40, cannotTriggerInsert:true,
            resizable:false, selectable:false},
*/
        {id:"last_name", name:"Last Name", field:"last_name",
            behavior: "select",
            cssClass:"cell-last-name", editor:Slick.Editors.Text,
            validator:requiredFieldValidator, sortable:true},
        {id:"first_name", name:"First Name", field:"first_name",
            cssClass:"cell-first-name", editor:Slick.Editors.Text,
            validator:requiredFieldValidator, sortable:true},
        {id:"emails", name:"Emails", field:"emails",
            width:90, minWidth:60,
            cssClass:"cell-emails", editor:Slick.Editors.Text,
            validator:requiredFieldValidator, sortable:true},
        {id:"pinnie_size", name:"Pinnie Size", field:"pinnie_size",
            width:40, minWidth:40,
            cssClass:"cell-emails", editor:Slick.Editors.Text,
            validator:requiredFieldValidator, sortable:true},
        {id:"shorts_size", name:"Shorts Size", field:"shorts_size",
            width:40, minWidth:40,
            cssClass:"cell-emails", editor:Slick.Editors.Text,
            validator:requiredFieldValidator, sortable:true},
        {id:"jersey_number", name:"Jersey #", field:"jersey_number",
            width:30, minWidth:30,
            cssClass:"cell-emails", editor:Slick.Editors.Text,
            validator:requiredFieldValidator, sortable:true}
    ];

    var i;
    for (i = 0; i < columns.length; i++) {
        // it seems that sortable=false must be used. Otherwise the
        // traditional sorting kicks in and shadows the menu headers.
        // We remove sortable for this reason and add the menu items if needed.
        var sortable = columns[i].sortable;
        columns[i].sortable = false;
        columns[i].optionsbar = [
            {
                cssClass:'btn btn-inverse',
                label:'<i class="caret upsidedown"></i>',
                command:"sort-asc",
                disabled:!sortable
            },
            {
                cssClass:'btn btn-inverse',
                label:'<i class="caret"></i>',
                command:"sort-desc",
                disabled:!sortable
            }
        ];
    }


    var origColumns = columns.slice();

    var options = {
        editable:true,
        enableAddRow:true,
        enableCellNavigation:true,
        asyncEditorLoading:true,
        forceFitColumns:false,
        enableColumnReorder:false
    };

    var sortcol = "title";
    var sortdir = 1;
    var searchString = "";

    function myFilter(item, args) {
        if (args.searchString !== "" &&
            item["title"].indexOf(args.searchString) == -1) {
            return false;
        }

        return true;
    }


    function comparer(a, b) {
        var x = a[sortcol], y = b[sortcol];
        return (x == y ? 0 : (x > y ? 1 : -1));
    }

    function toggleFilterRow() {
        if ($(grid.getTopPanel()).is(":visible")) {
            grid.hideTopPanel();
        } else {
            grid.showTopPanel();
        }
    }

    $(function () {

        dataView = new Slick.Data.DataView({inlineFilters:true});
        grid = new Slick.Grid("#myGrid", dataView, columns, options);
        grid.setSelectionModel(new Slick.RowSelectionModel());

        //var columnpicker = new Slick.Controls.ColumnPicker(
        //        columns, grid, options);


        // move the filter panel defined in a hidden div into grid top panel
        $("#inlineFilterPanel")
            .appendTo(grid.getTopPanel())
            .show();

        grid.onCellChange.subscribe(function (e, args) {
            dataView.updateItem(args.item.id, args.item);
        });

        grid.onAddNewRow.subscribe(function (e, args) {
            var item = {
                "num":data.length,
                "id":"new_" + (Math.round(Math.random() * 10000)),
                "title":"New task"
            };
            $.extend(item, args.item);
            dataView.addItem(item);
        });

        grid.onKeyDown.subscribe(function (e) {
            // select all rows on ctrl-a
            if (e.which != 65 || !e.ctrlKey) {
                return false;
            }

            var rows = [];
            var i;
            for (i = 0; i < dataView.getLength(); i++) {
                rows.push(i);
            }

            grid.setSelectedRows(rows);
            e.preventDefault();
        });

        grid.onSort.subscribe(function (e, args) {
            sortdir = args.sortAsc ? 1 : -1;
            sortcol = args.sortCol.field;
            log('onSort', sortdir, sortcol);

            dataView.sort(comparer, args.sortAsc);
        });

        // wire up model events to drive the grid
        dataView.onRowCountChanged.subscribe(function (e, args) {
            grid.updateRowCount();
            grid.render();
        });

        dataView.onRowsChanged.subscribe(function (e, args) {
            grid.invalidateRows(args.rows);
            grid.render();
        });

        var h_runfilters = null;

        function updateFilter() {
            dataView.setFilterArgs({
                                       searchString:searchString
                                   });
            dataView.refresh();
        }


        // wire up the search textbox to apply the filter to the model
        $("#txtSearch,#txtSearch2").keyup(function (e) {
            Slick.GlobalEditorLock.cancelCurrentEdit();

            // clear on Esc
            if (e.which == 27) {
                this.value = "";
            }

            searchString = this.value;
            updateFilter();
        });

        $("#btnSelectRows").click(function () {
            if (!Slick.GlobalEditorLock.commitCurrentEdit()) {
                return;
            }

            var rows = [];
            var i;
            for (i = 0; i < 10 && i < dataView.getLength(); i++) {
                rows.push(i);
            }

            grid.setSelectedRows(rows);
        });


        // initialize the model after all the events have been hooked up
        var data = [];

        // Get the data from ajax
        var json_url = $('#myGrid').data('json-url');
        $.ajax({
                   url:json_url
               })
            .error(function () {
                   var s = 'Cannot load data at: ' + json_url;
                   console.log(s);
                           })
            .done(function (new_data) {
                      data = new_data;
                      dataView.beginUpdate();
                      dataView.setItems(data);
                      dataView.setFilterArgs({
                                                 searchString:searchString
                                             });
                      dataView.setFilter(myFilter);
                      dataView.endUpdate();

                      // autosize ...
                      // XXX Not sure if we want this here to happen. But since
                      // we have an ajax, the scrollbar / no scrollbar question
                      // will only be decided when we have the first result set.
                      // This line helps to avoid a horizontal scrollbar.
                      // Perhaps, a better way would be to revisit the usage of forceFitColumns=true,
                      // which however caused a problem in an earlier state of development.
                      grid.autosizeColumns();
                  });


        // autosize first
        grid.autosizeColumns();


        // header menus
        var headerOptionsPlugin = new Slick.Plugins.HeaderOptionsBar({
                                                                         buttonImage:null
                                                                     });
        // hook up the sorting menu commands into the grid's sorting mechanism.
        headerOptionsPlugin.onCommand.subscribe(function (e, args) {
            if (args.command.substr(0, 5) == 'sort-') {
                var sortAsc = args.command.substr(5) == 'asc';
                args.grid.onSort.notify({
                                            grid:args.grid,
                                            multiColumnSort:false,
                                            sortCol:args.column,
                                            sortAsc:sortAsc
                                        }, e, args.grid);
                // Visually mark the sorted column header with the up / down chevron.
                args.grid.setSortColumns([
                                             {columnId:args.column.id, sortAsc:sortAsc}
                                         ]);
            }
        });
        headerOptionsPlugin.onMenuShow.subscribe(function (e, args) {
            // save the edited cells
            if (!Slick.GlobalEditorLock.commitCurrentEdit()) {
                // ???
                Slick.GlobalEditorLock.cancelCurrentEdit();
            }
        });
        grid.registerPlugin(headerOptionsPlugin);


        var $grid = $('#myGrid');
        // Enable event translation for both the canvas (cells), and the headers.
        // It seems the only way to run this is prevent_default = true.
        // But this means that we need to wire all touch events we want.
        $grid.hammer({
                         prevent_default:true
                     });

        // Help debugging by logging all the possible events with the cell information.
        $grid.on('hold tap doubletap transformstart transform transformend' +
                     'dragstart drag dragend swipe release', function (evt) {
            var locate = locateCell(grid, evt);
            if (locate.type == 'header') {
                //log('Touch event (header):', evt.type, locate.column);
            } else if (locate.type == 'cell') {
                //log('Touch event (cell):', evt.type, locate.row, locate.column);
            } else {
                //log('Touch event (outside):', evt.type);
            }
        });

        // Cell button bar

        var $canvas = $grid.find('.grid-canvas');
        var $viewport = $grid.find('.slick-viewport');

        $canvas.optionsbar({
                               content:[
                                   {
                                       cssClass:'btn btn-inverse',
                                       label:"Edit",
                                       command:"edit"
                                   },
                                   {
                                       cssClass:'btn btn-inverse',
                                       label:"Delete Row",
                                       command:"delete-row"
                                   }
                               ]
                           });
        var cellOptionsBar = $canvas.data('optionsbar');
        var finishEditBar;
        $canvas.on('command.demo76', function (evt, options) {
            // Find out the row and column of the cell
            var realEvt = evt.originalEvent || evt;
            var cell = grid.getCellFromEvent(realEvt);
            log('Cell command:', options.command, cell);
            if (options.command == 'edit') {
                // Set this cell to be the active one. And activate the editor for it.
                grid.setActiveCell(cell.row, cell.cell);
                grid.editActiveCell();
                // Pop up a second toolbar that can be used to cancel the editing.
                finishEditBar.setPositionElement(realEvt.target, $grid);
                finishEditBar.show(evt);

            } else if (options.command == 'delete-row') {
                var item = dataView.getItem(cell.row);
                var RowID = item.id;
                dataView.deleteItem(RowID);
                grid.invalidate();
                grid.render();
            }


        });


        var instance = {};    // hold the state of our event workflow.
        $grid.on({

                     // This part is handling the pinch-to-resize on the canvas
                     // (pinching in top of the cell, resizes the column.
                     // An ambivalent experiment.)

                     transformstart:function (evt) {
                         // Find out the row and column of the cell
                         var target = evt.originalEvent.target;
                         var cell = grid.getCellFromEvent(evt.originalEvent);
                         // Let's lock the column for the duration of the entire transform.
                         instance.columnIndex = cell.cell;
                         var cHeaders = $('#myGrid .slick-header .slick-header-column');
                         instance.columnHeader = cHeaders.eq(instance.columnIndex);
                         // Start the transform.
                         var column = instance.columnHeader;
                         instance.oldColor = column.css('color');
                         instance.oldWidth = column.width();
                         column.css('color', 'red');
                         return false;
                     },
                     transform:function (evt) {
                         var scale = evt.scale;
                         if (scale === 0) {
                             // why?
                             return false;
                         }
                         var column = instance.columnHeader;
                         column.width(instance.oldWidth * scale);
                         return false;
                     },
                     transformend:function (evt) {
                         var scale = evt.scale;
                         if (scale === 0) {
                             // why?
                             return false;
                         }
                         var column = instance.columnHeader;
                         var newWidth = instance.oldWidth * scale;
                         column.width(newWidth);
                         column.css('color', instance.oldColor);
                         columns[instance.columnIndex].width = newWidth;
                         grid.setColumns(columns);
                         grid.autosizeColumns();
                         return false;
                     },


                     // Tapping selects the tapped row, and unselects any other row.
                     // Tapping a selected row pops the cell options menu buttons,
                     // doubletapping has the same effect as selecting and tapping again.

                     tap:function (evt) {
                         var locate = locateCell(grid, evt);
                         if (locate.type == 'cell') {
                             // What is the current selection now?
                             var selectedRows = grid.getSelectedRows();
                             var isSameSelection = selectedRows.length == 1 && selectedRows[0] == locate.row;
                             if (isSameSelection) {
                                 // If the same row is already selected, then a single tap acts like
                                 // a double tap: that is, this is a second tap and doubletap will be in effect.
                                 cellOptionsBar.setPositionElement(locate.target, $grid);
                                 cellOptionsBar.show(evt);
                             } else {
                                 // If we had no selection, or a different selection from this single row in the set:
                                 // Then, the current selection is cleared, and a single
                                 // row will be selected.
                                 selectedRows = [locate.row];
                                 grid.setSelectedRows(selectedRows);
                                 //
                                 // This must cancel the editing too.
                                 // save the edited cells
                                 if (!Slick.GlobalEditorLock.commitCurrentEdit()) {
                                     // ???
                                     Slick.GlobalEditorLock.cancelCurrentEdit();
                                 }
                             }
                         }
                     },

                     doubletap:function (evt) {
                         var locate = locateCell(grid, evt);
                         if (locate.type == 'cell') {
                             cellOptionsBar.setPositionElement(locate.target, $grid);
                             cellOptionsBar.show();
                         }
                     }

                 });


        // The edit buttons are bound to a separate node then the first (hmmm...)
        $viewport.optionsbar({
                                 content:[
                                     {
                                         cssClass:'btn btn-inverse',
                                         label:"Cancel",
                                         command:"cancel-editing"
                                     }
                                 ]
                             });
        finishEditBar = $viewport.data('optionsbar');
        $viewport.on('command.demo76', function (evt, options) {
            // Find out the row and column of the cell
            var realEvt = evt.originalEvent || evt;
            var cell = grid.getCellFromEvent(realEvt);
            if (options.command == 'cancel-editing') {
                Slick.GlobalEditorLock.cancelCurrentEdit();
            }
        });

        grid.onClick.subscribe(function (e, args) {
            // Prevent clicking a cell. This would go to edit which we
            // do not want now.
            e.stopImmediatePropagation();
            e.preventDefault();
        });
        grid.onDblClick.subscribe(function (e, args) {
            // Prevent double clicking a cell. This would go to edit which we
            // do not want now.
            e.stopImmediatePropagation();
            e.preventDefault();
        });


        // autoresize columns
        var timer;
        $(window).resize(function (evt) {
            if (timer !== null) {
                clearTimeout(timer);
            }
            timer = setTimeout(function () {
                var width = $(window).width();
                var wide = (width > 768); // ipad orientation narrow / wide
                // Hide or show the last two columns, based on the layout.
                // XXX this is a little rough... we'd need to be smarter here
                // to conserve our current columns sizes and order.
                if (wide) {
                    if (columns.length < 5) {
                        columns.push(origColumns[3]);
                        columns.push(origColumns[4]);
                    }
                } else {
                    if (columns.length > 3) {
                        columns = origColumns.slice(0, 3);
                    }
                }

                // and resize.
                grid.setColumns(columns);
                grid.autosizeColumns();
                timer = null;
            }, 400);
        });

    });

    $('#fb-download').on('click', function () {
        var csv_url = $('#myGrid').data('csv-url');
        console.log('csv_url', csv_url);
        location.url = csv_url;
        //return false;
    })

})(window.jQuery);
