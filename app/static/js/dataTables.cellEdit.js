jQuery.fn.dataTable.Api.register('MakeCellsEditable()', function (settings) {
    var table = this.table();

    function getInputHtml(currentColumnIndex, settings, oldValue) {
        var inputSetting, inputType, input, inputCss, confirmCss, cancelCss;

        if (settings.inputTypes) {
            $.each(settings.inputTypes, function (index, setting) {
                if (setting.column == currentColumnIndex) {
                    inputSetting = setting;
                    inputType = inputSetting.type.toLowerCase();
                }
            });
        }

        if (settings.inputCss) {
            inputCss = settings.inputCss;
        }
        if (settings.confirmationButton) {
            confirmCss = settings.confirmationButton.confirmCss;
            cancelCss = settings.confirmationButton.cancelCss;
            inputType = inputType + "-confirm";
        }

        switch (inputType) {
            case "list":
            case "list-confirm": // List w/ confirm
                var html = "<select class='" + inputCss + "'>";
                $.each(inputSetting.options, function (index, option) {
                    if (oldValue == option.value) {
                        html = html + "<option value='" + option.value + "' selected>" + option.display + "</option>"
                    } else {
                        html = html + "<option value='" + option.value + "' >" + option.display + "</option>"
                    }
                });
                html = html + "</select>";
                var $input = $(html);

                if (inputType == 'list') {
                    $input.on('change', function () {
                        updateEditableCell(this);
                    });
                    return [$input];
                } else {
                    return [$input, getConfirmButton(), getCancelButton()];
                }

            case "datepicker": // Both datepicker options work best when confirming the values
            case "datepicker-confirm":
                // Makesure jQuery UI is loaded on the page
                if (typeof jQuery.ui == 'undefined') {
                    alert("jQuery UI is required for the DatePicker control but it is not loaded on the page!");
                    break;
                }
                jQuery(".datepick").datepicker("destroy");
                var $input = $('<input>').attr('id', 'ejbeatycelledit')
                    .attr('name', 'date')
                    .attr('type', 'text')
                    .addClass(inputCss)
                    .addClass('datepick')
                    .attr('value', oldValue);

                setTimeout(function () { // Set timeout to allow the script to write the input.html before triggering the datepicker
                    var icon = "http://jqueryui.com/resources/demos/datepicker/images/calendar.gif";
                    // Allow the user to provide icon
                    if (typeof inputSetting.options !== 'undefined' && typeof inputSetting.options.icon !== 'undefined') {
                        icon = inputSetting.options.icon;
                    }
                    var self = jQuery('.datepick').datepicker(
                        {
                            showOn: "button",
                            buttonImage: icon,
                            buttonImageOnly: true,
                            buttonText: "Select date"
                        });
                }, 100);
                return [$input, getConfirmButton(), getCancelButton()];

            case "text-confirm": // text input w/ confirm            
            case "undefined-confirm": // text input w/ confirm
                var $input = $('<input>').attr('id', 'ejbeatycelledit')
                    .addClass(inputCss)
                    .attr('value', oldValue);
                addKeydownHandler($input);
                return [$input, getConfirmButton(), getCancelButton()];

            case "textarea":
            case "textarea-confirm":
                var $input = $('<textarea>').attr('id', 'ejbeatycelledit')
                    .addClass(inputCss)
                    .val(oldValue);
                addKeydownHandler($input);
                return [$input, getConfirmButton(), getCancelButton()];

            default: // text input
                var $input = $('<input>').attr('id', 'ejbeatycelledit')
                    .addClass(inputCss)
                    .attr('value', oldValue)
                    .on('blur', function () {
                        updateEditableCell(this);
                    });
                addKeydownHandler($input);
                return [$input];
        }
        return;
    }

    function addKeydownHandler($input) {
        $input.on('keydown', function (e) {
            if (e.which == 13) { // Enter key
                e.preventDefault();
                updateEditableCell(this);
            }
        });
    }

    function getConfirmButton() {
        var confirmCss = '';
        if (settings.confirmationButton) {
            confirmCss = settings.confirmationButton.confirmCss;
        }
        var $ok = $('<a>').attr('href', 'javascript:void(0);')
            .addClass(confirmCss)
            .html("<span class='glyphicon glyphicon-ok'>Submit</span>")
            .on('click', function () {
                updateEditableCell(this);
            });
        return $ok;
    }

    function getCancelButton() {
        var cancelCss = '';
        if (settings.confirmationButton) {
            cancelCss = settings.confirmationButton.cancelCss;
        }
        var $cancel = $('<a>').attr('href', 'javascript:void(0);')
            .addClass(cancelCss)
            .html("<span class='glyphicon glyphicon-remove'>Cancel</span>")
            .on('click', function () {
                cancelEditableCell(this);
            });
        return $cancel;
    }

    function getInputField(callingElement) {
        // Update datatables cell value
        var inputField;
        switch ($(callingElement).prop('nodeName').toLowerCase()) {
            case 'a': // This means they're using confirmation buttons
                if ($(callingElement).siblings('input').length > 0) {
                    inputField = $(callingElement).siblings('input');
                }
                if ($(callingElement).siblings('select').length > 0) {
                    inputField = $(callingElement).siblings('select');
                }
                if ($(callingElement).siblings('textarea').length > 0) {
                    inputField = $(callingElement).siblings('textarea');
                }
                break;
            default:
                inputField = $(callingElement);
        }
        return inputField;
    }

    function sanitizeCellValue(cellValue) {
        if (typeof (cellValue) === 'undefined' || cellValue === null || cellValue.length < 1) {
            return "";
        }

        // If not a number
        if (isNaN(cellValue)) {
            // escape single quote
            cellValue = cellValue.replace(/'/g, "&#39;");
        }
        return cellValue;
    }

    function updateEditableCell(callingElement) {
        // Need to redeclare table here for situations where we have more than one datatable on the page. See issue6 on github
        var table = $(callingElement).closest("table").DataTable().table();
        var row = table.row($(callingElement).parents('tr'));
        var cell = table.cell($(callingElement).parent());
        var columnIndex = cell.index().column;
        var inputField = getInputField(callingElement);

        // Update
        var newValue = inputField.val();
        if (!newValue && ((settings.allowNulls) && settings.allowNulls != true)) {
            // If columns specified
            if (settings.allowNulls.columns) {
                // If current column allows nulls
                if (settings.allowNulls.columns.indexOf(columnIndex) > -1) {
                    _update(newValue);
                } else {
                    _addValidationCss();
                }
                // No columns allow null
            } else if (!newValue) {
                _addValidationCss();
            }
            //All columns allow null
        } else {
            _update(newValue);
        }
        function _addValidationCss() {
            // Show validation error
            if (settings.allowNulls.errorClass) {
                $(inputField).addClass(settings.allowNulls.errorClass)
            } else {
                $(inputField).css({ "border": "red solid 1px" });
            }
        }
        function _update(newValue) {
            var oldValue = cell.data();
            cell.data(newValue);
            //Return cell & row.
            settings.onUpdate(cell, row, oldValue);
        }
        // Get current page
        var currentPageIndex = table.page.info().page;

        //Redraw table
        table.page(currentPageIndex).draw(false);
    }

    function cancelEditableCell(callingElement) {
        var table = $(callingElement.closest("table")).DataTable().table();
        var cell = table.cell($(callingElement).parent());
        // Set cell to it's original value
        cell.data(cell.data());

        // Redraw table
        table.draw();
    }

    if (settings === "destroy") {
        $(table.body()).off("click", "td");
        table = null;
    }

    if (table != null) {
        $(table.body()).on('click', 'td', function () {
            var currentColumnIndex = table.cell(this).index().column;
            if ((settings.columns && settings.columns.indexOf(currentColumnIndex) > -1) || (!settings.columns)) {
                var row = table.row($(this).parents('tr'));
                editableCellsRow = row;

                var cell = table.cell(this).node();
                var oldValue = table.cell(this).data();
                oldValue = sanitizeCellValue(oldValue);

                if (!$(cell).find('input').length && !$(cell).find('select').length && !$(cell).find('textarea').length) {
                    var input = getInputHtml(currentColumnIndex, settings, oldValue);
                    $(cell).empty();
                    for (var i = 0; i < input.length; i++) {
                        $(cell).append(input[i]);
                    }
                    $('#ejbeatycelledit').focus();
                }
            }
        });
    }
});
