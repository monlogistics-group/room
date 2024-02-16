odoo.define('ml_worldwide-main.ListMerge', function (require) {
    "use strict";
    
    var core = require('web.core');
    var FieldMany2Many = require('web.relational_fields').FieldMany2Many;
    var fieldRegistry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');
    var FormController = require('web.FormController');
    var _t = core._t;
    
    FormController.include({

        _onSwitchView: function (event) {
            console.log("_onSwitchView _onSwitchView _onSwitchView");
            event.stopPropagation();
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: event.data.model,
                views: [[event.data.formViewID || false, 'form']],
                res_id: event.data.res_id,
                context: {default_freight_id:1},
            });
        },

     });

    var SectionAndNoteListRenderer = ListRenderer.include({
        // _getNumberOfCols: function () {
        // 	var columns = this._super();
        // 	columns +=1;
        // 	return columns;
        // },
        // _renderFooter: function (isGrouped) {
        // 	var $footer = this._super(isGrouped);
        // 	$footer.find("tr").prepend($('<td>'));
        // 	return $footer;
        // },
        // _renderGroupRow: function (group, groupLevel) {
        //     var $row =  this._super(group, groupLevel);
        //     if (this.mode !== 'edit' || this.hasSelectors){
        //     	$row.find("th.o_group_name").after($('<td>'));
        //     }
        //     return $row;
        // },
        // _renderGroups: function (data, groupLevel) {
        // 	var self = this;
        // 	var _self = this;
        // 	groupLevel = groupLevel || 0;
        //     var result = [];
        // 	var filter = $("div[name*='freights_routes_shipment']")
        //     var $tbody = filter.find('tbody');
        // 	console.log('test');
        // 	if ($tbody) {
        // 		_.each(data, function (group) {
        // 			if (!$tbody) {
        // 				$tbody = $('<tbody>');
        // 				filter
        // 			}
        // 			// $tbody.append(self._renderGroupRow(group, groupLevel));
        // 			if (group.data.length) {
        // 				result.push($tbody);
        // 				// render an opened group
        // 				if (group.groupedBy.length) {
        // 					// the opened group contains subgroups
        // 					result = result.concat(self._renderGroups(group.data, groupLevel + 1));
        // 				} else {
        // 					// the opened group contains records
        // 					var $records = _.map(group.data, function (record,index) {
        // 						//Nilesh
        // 						if (_self.mode !== 'edit' || _self.hasSelectors){
        // 							return self._renderRow(record).prepend($("<th class='o_list_row_count_sheliya'>").html(index+1+2)); //.prepend($('<td>'));
        // 						}
        // 						else{
        // 							return self._renderRow(record);
        // 						}
                                
        // 					});
        // 					result.push($('<tbody>').append($records));
        // 				}
        // 				$tbody = null;
        // 			}
        // 		});
        // 		if ($tbody) {
        // 			result.push($tbody);
        // 		}
        // 	}
    
        //     return result;
        // },
        // _renderHeader: function (isGrouped) {
        // 	var $header = this._super(isGrouped);
        // 	if (this.hasSelectors) {
        // 		$header.find("th.o_list_record_selector").before($('<th class="o_list_row_number_header o_list_row_count_sheliya">').html('#'));
        // 		var advance_search = $header.find("tr.advance_search_row")
        // 		if(advance_search.length && advance_search.find('td.o_list_row_number_header').length==0){    			
        // 			advance_search.prepend($('<td class="o_list_row_number_header">').html('&nbsp;'));
        // 		}
        //     }
        // 	else{
        // 		if (this.mode !== 'edit'){
        // 			$header.find("tr").prepend($("<th class='o_list_row_number_header o_list_row_count_sheliya'>").html('#'));
        // 		}
        // 	}
        // 	//$header.find("tr").prepend($('<th>').html('#'));
        // 	return $header;
        // },
        // _renderRow: function (record) {
        // 	var $row = this._super(record);
        // 	if (this.mode !== 'edit' && this.state.groupedBy.length==0){
        //     	var index = this.state.data.findIndex(function(e){return record.id===e.id})
        // 		console.log(_getNumberOfRows())
        // 		console.log(index,$row);
                // if (index!==-1){
                // 	$row.prepend($("<th class='o_list_row_count_sheliya'>").html("teneg s"));
                // }
                // if (record.data.display_type) {
                //     $row.find(".o_section_and_note_text_cell").attr('colspan', parseInt($row.find(".o_section_and_note_text_cell").attr('colspan')) - 1)
                // }
    
        // 	}
        // 	return $row;
    
        // },

        _onRowClicked: function (ev) {
            if (!ev.target.closest('.o_list_record_selector') && !$(ev.target).prop('special_click') && !this.no_open) {
                var id = $(ev.currentTarget).data('id');
                if (id) {
                    this.trigger_up('open_record', { id: id, target: ev.target, context: {default_freight_id:1} });
                    // fromCtrl.do_action({
                    //     type: 'ir.actions.act_window',
                    //     res_model: 'freights.quotations',
                    //     views: [['form']],
                    //     res_id: id,
                    // });
                }
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
    