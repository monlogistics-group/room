odoo.define("tt_odoo_rest_api.tt_form_table_widget", function(require){
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var basic_fields = require('web.basic_fields');
    var core = require('web.core');
    var QWeb = core.qweb;

    var TTRouteWidget = AbstractField.extend({
        init : function(parent, state, params){
            var self = this;
            this._super.apply(this, arguments);
        },

        start: function(){
            var self = this;
            this._super.apply(this, arguments);
            debugger;
            self.tt_route_data = self.recordData.tt_route ? JSON.parse(self.recordData.tt_route) : false
//            self._rpc({
//                'model' : 'tortecs.rest.api',
//                'method' : 'tt_generate_route_data',
//                'args' : [[]]
//            }).then(function(data){
//                self.tt_route_data = data;
//            });
        },

        _render: function() {
            var self = this;
            this._super.apply(this, arguments);
            debugger;
            if(self.tt_route_data){
                var $table_container = $(QWeb.render('table_view_template'));
                var route_data = self.tt_route_data;
                var rows = "";
                var field_name = null;
                for(let item in route_data){
                    const val = `<tr><td class='tt_table_body'>${item}</td><td class="tt_new">${route_data[item]}</td>`;
                    let $body = $table_container.find(".tt_body");
                    $body.append(val);
                }
                self.$el.append($table_container);
            }
        },
    });
    registry.add('tt_table_widget', TTRouteWidget);
});