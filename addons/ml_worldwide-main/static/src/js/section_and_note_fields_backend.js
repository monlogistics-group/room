
odoo.define('ml_worldwide-main.section_and_note_backend', function (require) {
"use strict";

var FieldMany2Many = require('web.relational_fields').FieldMany2Many;
var fieldRegistry = require('web.field_registry');
var ListRenderer = require('web.ListRenderer');

var core = require('web.core');
var qweb = core.qweb;
var _t = core._t;

var SectionAndNoteListRenderer = ListRenderer.extend({
    
    _renderView: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.$el.find('table').removeClass('o_list_table_ungrouped');
            self.$el.find('table').addClass('o_list_table_grouped');
            self.$('.o_list_table').toggleClass('', true);
        });
    },

    addLineButtonTemplate: 'group_by_add_item',
 
    _renderGroupRow: function (group, display_name, group_by) {
        var cells = [];
        const groupBy = group_by; //this.state.groupedBy[groupLevel];
        const name = display_name
        var $th = $('<th>')
            .addClass('o_group_name')
            .attr('tabindex', -1)
            .text(name + ' (' + group.count + ')');
        var $arrow = $('<span>')
            .css('padding-left', 22 + 'px')
            .css('padding-right', '5px')
            .addClass('fa');
        
        if (group.count > 0) {
            $arrow.toggleClass('fa-caret-right', !group.isOpen)
                .toggleClass('fa-caret-down', group.isOpen);
        }
        $th.prepend($arrow);
        cells.push($th);

        var aggregateKeys = Object.keys(group.aggregateValues);
        var aggregateValues = _.mapObject(group.aggregateValues, function (value) {
            return { value: value };
        });
        var aggregateCells = this._renderAggregateCells(aggregateValues);
        var firstAggregateIndex = _.findIndex(this.columns, function (column) {
            return column.tag === 'field' && _.contains(aggregateKeys, column.attrs.name);
        });
        var colspanBeforeAggregate;
        if (firstAggregateIndex !== -1) {
            colspanBeforeAggregate = firstAggregateIndex;
            var lastAggregateIndex = _.findLastIndex(this.columns, function (column) {
                return column.tag === 'field' && _.contains(aggregateKeys, column.attrs.name);
            });
            cells = cells.concat(aggregateCells.slice(firstAggregateIndex, lastAggregateIndex + 1));
            var colSpan = this.columns.length - 1 - lastAggregateIndex;
            if (colSpan > 0) {
                cells.push($('<th>').attr('colspan', colSpan));
            }
        } else {
            var colN = this.columns.length;
            colspanBeforeAggregate = colN > 1 ? colN - 1 : 1;
            if (colN > 1) {
                cells.push($('<th>'));
            }
        }
        if (this.hasSelectors) {
            colspanBeforeAggregate += 1;
        }
        $th.attr('colspan', colspanBeforeAggregate);

        if (group.isOpen && !group.groupedBy.length && (group.count > group.data.length)) {
            const lastCell = cells[cells.length - 1][0];
            this._renderGroupPager(group, lastCell);
        }
        if (group.isOpen && this.groupbys[groupBy]) {
            var $buttons = this._renderGroupButtons(group, this.groupbys[groupBy]);
            if ($buttons.length) {
                var $buttonSection = $('<div>', {
                    class: 'o_group_buttons',
                }).append($buttons);
                $th.append($buttonSection);
            }
        }

        cells.push($('<th>'));
    
        return $('<tr>')
            .addClass('o_group_header')
            .toggleClass('o_group_open', group.isOpen)
            .toggleClass('o_group_has_content', group.count > 0)
            .data('group', group)
            .append(cells);
    },

    _renderRow: function (record, isLast) {
        var $row = this._super.apply(this, arguments);
        if (record.data.display_type) {
            $row.addClass('o_is_' + record.data.display_type);
        }
        return $row;
    },

    _renderTrashIcon: function() {
        return qweb.render('hr_trash_button');
    },

    arrToObject: function(arr){
        var formatted = [];
        for (var i=0; i<arr.length; i++) {
            var o = {};
            o[arr[i][0]] = arr[i][1];
            formatted.push(o);
        }
        return formatted;
    },

    _getCreateLineContext: function (group) {
        return {};
    },

    _renderAddItemButton: function (group) {
        return qweb.render(this.addLineButtonTemplate, {
            context: JSON.stringify(this._getCreateLineContext(group)),
        });
    },

    _renderBody: function () {
        var self = this;
        var result = [];
        var aggArray = [];

        var groupBy = '';
        if (self.state.orderedBy.length>0) groupBy = self.state.orderedBy[0].name;
        var grouped_by = _.groupBy(this.state.data, function (record) {
            if (aggArray.length === 0) {
                _.each(record.fields, function (field) {
                    var type = field.type;
                    if (type === 'integer' || type === 'float' || type === 'monetary') {
                        if (field.name) aggArray.push([field.name, 0]);
                    }
                })
            }

            if (!record.data[groupBy].data) return record.data[groupBy];
            else if (record.data[groupBy].data.length == 0) return record.data[groupBy].res_id;
            else if (record.data[groupBy].data.display_name) return record.data[groupBy].data.display_name;
            else return record.data[groupBy].data[0].data.display_name;
        });

        var groupTitle;
        for (var key in grouped_by) {
            var $body = $('<tbody>');
            var group = grouped_by[key];
            if (key === 'undefined') {
                groupTitle = _t("Other");
            } else {
                if (!group[0].data[groupBy].data)  groupTitle = group[0].data[groupBy];
                    else if (group[0].data[groupBy].data.length == 0)  groupTitle = group[0].data[groupBy].res_id;
                    else if (group[0].data[groupBy].data.display_name)  groupTitle = group[0].data[groupBy].data.display_name;
                    else  groupTitle = group[0].data[groupBy].data[0].data.display_name;
                // if (group[0].data[groupBy].data.display_name) groupTitle = group[0].data[groupBy].data.display_name;
                // else if (group[0].data[groupBy].data[0].data) groupTitle = group[0].data[groupBy].data[0].data.display_name;
                // else groupTitle = group[0].data[groupBy];
            }
            group.forEach(function (record, index) {
                aggArray.forEach(function (agg, i) {
                    var value = (record.type === 'record') ? record.data[agg[0]] : record.aggregateValues[agg[0]];
                    if (Number(value) === value) {
                        agg[1] += value;
                    }
                });
            });
            var arrr = JSON.stringify(self.arrToObject(aggArray)).replaceAll("},{", ",").replaceAll("[{", "{").replaceAll("}]", "}");
            this.groupbys = [groupBy];
            var $title_row = $(self._renderGroupRow({
                'aggregateValues':JSON.parse(arrr),
                'count':group.length,
                'groupedBy': [groupBy],
                'isOpen':true,
                'context':this.state.context,
                'data': group.data,
                'domain':this.state.domain,
                'fields':this.state.fields,
                'fieldsInfo':this.state.fieldsInfo,
                'groupsCount': group.length,
                'groupsLimit': 20,
                'groupsOffset': 0,
                'id': this.state.id,
                'isM2MGrouped': this.state.isM2MGrouped,
                'isSample': this.state.isSample,
                'limit': this.state.limit,
                'model': this.state.model,
                'offset': this.state.offset,
                'orderedBy': this.state.orderedBy,
                'range': this.state.range,
                'res_id': this.state.res_id,
                'res_ids': this.state.res_ids,
                'type': "list",
                'value': groupTitle, //this.state.value,
                'viewType': "list"
            }, groupTitle, groupBy));
            
            aggArray.forEach(function (agg, i) {
                agg[1] = 0;
            })
            // Render each rows
            $body.append($title_row);
            result.push($body);
            var $tbl = $('<tbody id="'+groupTitle+'">');
            group.forEach(function (record, index) {
                var isLast = (index + 1 === group.length);
                var $row = self._renderRow(record, isLast);
                // if (self.addTrashIcon) $row.append(self._renderTrashIcon());
                $tbl.append($row);
            });
            result.push($tbl);
        }

        if (result.length>0 && self.addCreateLine) {
            result.push(this._renderAddItemButton());
        }
        return result;
    },

    _onToggleGroup: function (ev) {
        ev.preventDefault();
        var group = $(ev.currentTarget).closest('tr').data('group');
        if (group.count) {
            var lTable = document.getElementById(group.value);
            lTable.style.display = (lTable.style.display == "") ? "none" : "";
        }
    },

});

var SectionAndNoteFieldOne2Many = FieldMany2Many.extend({
    /**
     * We want to use our custom renderer for the list.
     *
     * @override
     */
    _getRenderer: function () {
        if (this.view.arch.tag === 'tree') {
            return SectionAndNoteListRenderer;
        }
        return this._super.apply(this, arguments);
    },
});

fieldRegistry.add('ml_worldwide_widget', SectionAndNoteFieldOne2Many);

return SectionAndNoteListRenderer;
});
