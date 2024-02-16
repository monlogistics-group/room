odoo.define('ml_trucking.mltruck_dashboard', function (require){
"use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var CustomDashBoard = AbstractAction.extend({
        template: 'MLTruckingDashBoard',
        events: {
            'click .tot_projects': 'direct_shipment',
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
                this.set("title", 'DashboardASD');
                return this._super().then(function() {
                    self.render_dashboards();
                });
            },
        
        render_dashboards: function(){
            var self = this;
            _.each(this.dashboards_templates, function(template) {
                    self.$('.o_pj_dashboard').append(QWeb.render(template, {widget: self}));
                });

            // Calender
            $('#calender').datetimepicker({
                inline: true,
                format: 'L'
            });

            // Chart Global Color
            Chart.defaults.color = "#6C7293";
            Chart.defaults.borderColor = "#000000";

            // Worldwide Sales Chart
            //var ctx1 = $("#worldwide-sales").get(0).getContext("2d");
            console.log(self,'******************')
            var ctx1 = self.$("#worldwide-sales")[0];
            var myChart1 = new Chart(ctx1, {
                type: "bar",
                data: {
                    labels: ["2016", "2017", "2018", "2019", "2020", "2021", "2022"],
                    datasets: [{
                            label: "USA",
                            data: [15, 30, 55, 65, 60, 80, 95],
                            backgroundColor: "rgba(235, 22, 22, .7)"
                        },
                        {
                            label: "UK",
                            data: [8, 35, 40, 60, 70, 55, 75],
                            backgroundColor: "rgba(235, 22, 22, .5)"
                        },
                        {
                            label: "AU",
                            data: [12, 25, 45, 55, 65, 70, 60],
                            backgroundColor: "rgba(235, 22, 22, .3)"
                        }
                    ]
                    },
                options: {
                    responsive: true
                }
            });


            // Salse & Revenue Chart
            //var ctx2 = $("#salse-revenue").get(0).getContext("2d");
            var ctx2 = self.$("#salse-revenue")[0];
            var myChart2 = new Chart(ctx2, {
                type: "line",
                data: {
                    labels: self.graph_months,
                    datasets: [{
                            label: "Cost",
                            data: self.planned_cost,
                            backgroundColor: "rgba(235, 22, 22, .7)",
                            fill: true
                        },
                        {
                            label: "Rate",
                            data: self.budget,
                            backgroundColor: "rgba(235, 22, 22, .5)",
                            fill: true
                        }
                    ]
                    },
                options: {
                    responsive: true
                }
            });
        },

        fetch_data: function() {
            var self = this;
            var def1 =  this._rpc({
                    model: 'mltrucking.base',
                    method: 'get_tiles_data'
            }).then(function(result)
                {
                    self.total_confirmed_transportation=result['total_confirmed_transportation']
                    self.between_countries=result["between_countries"]
                    self.between_cities=result['between_cities']
                    self.within_the_city=result["within_the_city"]
                    self.other_total=result['other_total']
                    self.other_total_within_city=result['other_total_within_city']
                    self.other_total_between_cities=result['other_total_between_cities']
                    self.other_total_between_countries=result['other_total_between_countries']
                    self.planned_cost=result['planned_cost']
                    self.budget=result['budget']
                    self.graph_months=result['graph_months']

            });
            return $.when(def1);
        },
        reload: function () {
            window.location.href = this.href;
        },
        direct_shipment: function(event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            return self.do_action({
                name: "Direct",
                type: 'ir.actions.act_window',
                res_model: 'mltrucking.base',
                view_mode: 'list,form',
                view_type: 'list',
                views: [[false, 'list'],[false, 'form']],
                // context: {'search_default_operation': 'direct'},
                // domain: [['operation','=','direct']],
                // search_view_id: self.employee_data.operation_search_view_id,
                target: 'current'
            },{on_reverse_breadcrumb: function(){ return self.reload();}})
        },
    })
    core.action_registry.add('mltrucking_dashboard_tags', CustomDashBoard);
    return CustomDashBoard;
})