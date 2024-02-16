
odoo.define('ml_worldwide-main.mlw_dashboard', function (require){
"use strict";
    
var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var datas;
    var web_client = require('web.web_client');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');


    var CustomDashBoard = AbstractAction.extend({
        template: 'MLWorldwideDashBoard',
        events: {
            'click .mlw_quotes': 'direct_quotes',
            'click .op-number': 'direct_freights',
            'click a': 'dashboard_click',
        },
        init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['DashboardProject'];
            this.today_sale = [];
        },
        
        willStart: function() {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function() {
                return self.fetch_data();
            });
        },

        start: function() {
                var self = this;
                this.set("title", 'A Dashboard');
                return this._super().then(function() {
                    self.render_dashboards();
                });
            },
        
        render_dashboards: function(){
            var self = this;
            console.log("render_dashboards");
            _.each(this.dashboards_templates, function(template) {
                    self.$('.o_pj_dashboard').append(QWeb.render(template, {widget: self}));
                });
            var result = self.dashboards_data;
            for(let i = 0; i < result['freights'].length; i++) {
                let obj = result['freights'][i];
                if (obj.state_id == "cancelled") {
                    self.$("#f_cancelled")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "created") {
                    self.$("#f_created")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "re-inquiry") {
                    self.$("#f_reinquiry")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "quotation") {
                    self.$("#f_quotation")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "confirmed") {
                    self.$("#f_confirmed")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "on-going") {
                    self.$("#f_ongoing")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "arrived") {
                    self.$("#f_arrived")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "released") {
                    self.$("#f_released")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "closed") {
                    self.$("#f_closed")[0].innerHTML = obj.count;
                }
            }
            for(let i = 0; i < result['quotations'].length; i++) {
                let obj = result['quotations'][i];
                if (obj.state_id == "cancelled") {
                    self.$("#q_cancelled")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "sent") {
                    self.$("#q_sent")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "re-cost") {
                    self.$("#q_recost")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "ready") {
                    self.$("#q_ready")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "started") {
                    self.$("#q_started")[0].innerHTML = obj.count;
                } else
                if (obj.state_id == "filled") {
                    self.$("#q_filled")[0].innerHTML = obj.count;
                }
            }
            self.$("#departure_total_ect")[0].innerHTML = result['departure_total_ect'][0].count;
            self.$("#departure_in5_ect")[0].innerHTML = result['departure_in5_ect'][0].count;
            self.$("#departure_late_ect")[0].innerHTML = result['departure_late_ect'][0].count;
            self.$("#departure_ontime_ect")[0].innerHTML = result['departure_ontime_ect'];
            self.$("#departure_total_act")[0].innerHTML = result['departure_total_act'][0].count;
            self.$("#departure_in5_act")[0].innerHTML = result['departure_in5_act'][0].count;
            self.$("#departure_late_act")[0].innerHTML = result['departure_late_act'][0].count;
            self.$("#departure_ontime_act")[0].innerHTML = result['departure_ontime_act'];

            self.$("#ba_total_ect")[0].innerHTML = result['ba_total_ect'][0].count;
            self.$("#ba_in5_ect")[0].innerHTML = result['ba_in5_ect'][0].count;
            self.$("#ba_late_ect")[0].innerHTML = result['ba_late_ect'][0].count;
            self.$("#ba_ontime_ect")[0].innerHTML = result['ba_ontime_ect'];
            self.$("#ba_total_act")[0].innerHTML = result['ba_total_act'][0].count;
            self.$("#ba_in5_act")[0].innerHTML = result['ba_in5_act'][0].count;
            self.$("#ba_late_act")[0].innerHTML = result['ba_late_act'][0].count;
            self.$("#ba_ontime_act")[0].innerHTML = result['ba_ontime_act'];

            self.$("#bd_total_ect")[0].innerHTML = result['bd_total_ect'][0].count;
            self.$("#bd_in5_ect")[0].innerHTML = result['bd_in5_ect'][0].count;
            self.$("#bd_late_ect")[0].innerHTML = result['bd_late_ect'][0].count;
            self.$("#bd_ontime_ect")[0].innerHTML = result['bd_ontime_ect'];
            self.$("#bd_total_act")[0].innerHTML = result['bd_total_act'][0].count;
            self.$("#bd_in5_act")[0].innerHTML = result['bd_in5_act'][0].count;
            self.$("#bd_late_act")[0].innerHTML = result['bd_late_act'][0].count;
            self.$("#bd_ontime_act")[0].innerHTML = result['bd_ontime_act'];

            self.$("#arrival_total_ect")[0].innerHTML = result['arrival_total_ect'][0].count;
            self.$("#arrival_in5_ect")[0].innerHTML = result['arrival_in5_ect'][0].count;
            self.$("#arrival_late_ect")[0].innerHTML = result['arrival_late_ect'][0].count;
            self.$("#arrival_ontime_ect")[0].innerHTML = result['arrival_ontime_ect'];
            self.$("#arrival_total_act")[0].innerHTML = result['arrival_total_act'][0].count;
            self.$("#arrival_in5_act")[0].innerHTML = result['arrival_in5_act'][0].count;
            self.$("#arrival_late_act")[0].innerHTML = result['arrival_late_act'][0].count;
            self.$("#arrival_ontime_act")[0].innerHTML = result['arrival_ontime_act'];
        },

        fetch_data: function() {
            var self = this;
            var prom = this._rpc({
                    model: 'mlworldwide.freights',
                    method: 'get_dashboard_data'
            }).then(function(result_data)
                {
                    self.dashboards_data = result_data;
            });
            console.log(prom,'pr--------------');
            return prom;
        },
        reload: function () {
            window.location.href = this.href;
        },
        direct_quotes: function(event) {
            var self = this;
            var domain=[];
            switch (event.target.id) {
                case 'q_started':
                    domain = ['state_id','=','started'];
                    break;
                case 'q_filled':
                    domain = ['state_id','=','filled'];
                    break;
                case 'q_ready':
                    domain = ['state_id','=','ready'];
                    break;
                case 'q_recost':
                    domain = ['state_id','=','recost'];
                    break;
                case 'q_sent':
                    domain = ['state_id','=','sent'];
                    break;
                case 'q_cancelled':
                    domain = ['state_id','=','cancelled'];
                    break;    
                default:
                    domain = ['state_id','!=','null'];
            }
            event.stopPropagation();
            event.preventDefault();
            return self.do_action({
                name: "Freights quotations",
                type: 'ir.actions.act_window',
                res_model: 'freights.quotations',
                view_mode: 'list,form',
                view_type: 'list',
                views: [[false, 'list'],[false, 'form']],
                domain: [domain],
                priority: 0,
                target: 'current'
            },{ on_reverse_breadcrumb:function(){ self.do_toggle(); } })
        },
        direct_freights: function(event) {
            var self = this;
            var domain=[];
            switch (event.target.id) {
                case 'f_cancelled':
                    domain = ['state_id','=','cancelled'];
                    break;
                case 'f_created':
                    domain = ['state_id','=','created'];
                    break;
                case 'f_reinquiry':
                    domain = ['state_id','=','reinquiry'];
                    break;
                case 'f_quotation':
                    domain = ['state_id','=','quotation'];
                    break;
                case 'f_confirmed':
                    domain = ['state_id','=','confirmed'];
                    break;
                case 'f_ongoing':
                    domain = ['state_id','=','ongoing'];
                    break; 
                case 'f_arrived':
                    domain = ['state_id','=','arrived'];
                    break;  
                case 'f_released':
                    domain = ['state_id','=','released'];
                    break;
                case 'f_closed':
                    domain = ['state_id','=','closed'];
                    break; 
                default:
                    domain = ['state_id','!=','null'];
            }
            event.stopPropagation();
            event.preventDefault();
           
            return self.do_action({
                name: "Freights",
                type: 'ir.actions.act_window',
                res_model: 'mlworldwide.freights',
                view_mode: 'list,form',
                view_type: 'list',
                views: [[false, 'list'],[false, 'form']],
                domain: [domain],
                target: 'current'
            },{on_reverse_breadcrumb: function(){ self.do_toggle(); }})
        },
        dashboard_click:function(event) {
            var self = this;
            console.log(event);
        },
    })
    core.action_registry.add('mlw_dashboard_tags', CustomDashBoard);
    return CustomDashBoard;
})