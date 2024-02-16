odoo.define("ml_worldwide-main.export_button", function (require) {
  "use strict";
  var ListController = require("web.ListController");
  var ListView = require("web.ListView");
  var viewRegistry = require("web.view_registry");
  var DataExport = require("web.DataExport");
  var core = require("web.core");
  var QWeb = core.qweb;

  var TreeButton = ListController.extend({
    buttons_template: "ml_worldwide-main.buttons",
    events: _.extend({}, ListController.prototype.events, {
      "click .button_export": "_onDirectExportData",
      //   "click .www": "qwe",
    }),

    init: function (parent, context) {
      this._super.apply(this, arguments);
      this.manager = [];
    },
    qwe: function () {
      console.log("aiosdjoajsd");
      // $(".www").click(function (e) {
      //   console.log("-=asd-=asd");
      // });
      //   this._rpc({
      //     model: "mlworldwide.freights",
      //     method: "get_tiles_data",
      //   }).then(function (result) {
      //     console.log(result);
      //   });
    },

    start: function () {
      this._render();
      this.manager = [{ name: "asd" }, { name: "12" }];
      console.log(this.manager, "=====");
      return this._super.apply(this, arguments);
    },

    _render: function () {
      console.log("----====1");
      $(".some_class").text(this.var_name);
      // this.$el.html(QWeb.render('ml_worldwide-main.buttons', {
      //     manager : ['as']
      // }));
    },

    _onDirectExportData() {
      return this._rpc({
        model: "ir.exports",
        method: "search_read",
        args: [[], ["id"]],
        limit: 1,
      }).then(() => this._getExportDialogWidget().export());
    },

    _getExportDialogWidget() {
      let state = this.model.get(this.handle);
      // console.log(Object.keys(state.fields),'state---');

      let defaultExportFields = this.renderer.columns
        .filter(
          (field) =>
            field.tag === "field" &&
            state.fields[field.attrs.name].exportable !== false
        )
        .map((field) => field.attrs.name);

      let groupedBy = this.renderer.state.groupedBy;
      const domain = this.isDomainSelected && state.getDomain();
      return new DataExport(
        this,
        state,
        Object.keys(state.fields),
        groupedBy,
        domain,
        this.getSelectedIds()
      );
    },
  });
  var SaleOrderListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
      Controller: TreeButton,
    }),
  });
  viewRegistry.add("export_in_freight", SaleOrderListView);
});

odoo.define("ml_worldwide-main.filter_buttons", function (require) {
  "use strict";
  var ListController = require("web.ListController");
  var ListView = require("web.ListView");
  var viewRegistry = require("web.view_registry");
  var DataExport = require("web.DataExport");
  var core = require("web.core");
  var QWeb = core.qweb;
  var ajax = require("web.ajax");
  var rpc = require("web.rpc");
  var registry = require("web.Registry");
  const ActionModel = require("web.ActionModel");
  const Dialog = require("web.Dialog");

  var FilterButton = ListController.extend({
    buttons_template: "ml_worldwide-main.package.buttons",
    events: _.extend({}, ListController.prototype.events, {
      "click .packagebtn": "onclick",
      "click .pop_up_button": "onclickpopup",
    }),

    init: function (parent, context) {
      this._super.apply(this, arguments);
      // console.log(parent,'-=================--------', context);
      this.terminals = [];
      this.config = context;
      this.parent = parent;
    },

    onclick: function () {
      var self = this;
      $(document)
        .off()
        .on("click", ".packagebtn", function () {
          // console.log($(this).attr('id'),'id====--');
          // console.log(self.terminals);
          var context =
            self.parent.__widget.controlPanelProps.searchModel.config;
          var env =
            self.config.__parentedParent.config.__parentedParent
              .controlPanelProps.searchModel.env;
          var mapping =
            self.config.__parentedParent.config.__parentedParent
              .controlPanelProps.searchModel.mapping;
          var extensions =
            self.config.__parentedParent.controlPanelProps.searchModel
              .extensions;
          var subscriptions =
            self.config.__parentedParent.controlPanelProps.searchModel
              .subscriptions;
          var actionModel = new ActionModel(self.parent);
          actionModel.config = context;
          actionModel.subscriptions = subscriptions;
          actionModel.mapping = mapping;
          actionModel.env = env;
          actionModel.extensions = extensions;
          let filter = actionModel.get("filters", (f) => f.type === "filter");
          // console.log(filter,'======');

          for (let i = 0; i < self.terminals.length; i++) {
            if (self.terminals[i] == $(this).attr("id")) {
              // console.log(self.terminals[i],'-lmao----');
              var myFilter = [
                {
                  description: self.terminals[i],
                  domain: `[["terminal", "=", "${self.terminals[i]}"]]`,
                  type: "filter",
                },
              ];

              for (let j = 0; j < filter.length; j++) {
                if (filter[j].description == self.terminals[i]) {
                  return self.displayNotification({
                    type: "warning",
                    title: "Warning",
                    message: "Filter with same name already exists",
                    sticky: true,
                  });
                }
              }
              actionModel.dispatch("createNewFilters", myFilter);
            }
          }
        });
    },

    start: function () {
      return this._super.apply(this, arguments);
    },

    willStart: function () {
      var self = this;
      return $.when(ajax.loadLibs(this), this._super()).then(function () {
        return self.fetch_data();
      });
    },

    fetch_data: function () {
      var self = this;
      var def1 = this._rpc({
        model: "freights.packages",
        method: "get_filtered_records",
      }).then(function (result) {
        self.terminals = result;
      });
      return $.when(def1);
    },
    onclickpopup: function (ev) {
      var self = this;
      console.log(
        self.config.__parentedParent.controlPanelProps.actionMenus,
        "=self.config.__parentedParent.controlPanelProps.actionMenus"
      );
      if (self.config.__parentedParent.controlPanelProps.actionMenus == null) {
        return self.displayNotification({
          type: "warning",
          title: "Warning",
          message: "You must select field",
          sticky: true,
        });
      }
      var selected_ids =
        self.config.__parentedParent.controlPanelProps.actionMenus.activeIds;
      ev.preventDefault();
      $(document)
        .off()
        .on("click", ".pop_up_button", function () {
          self.do_action({
            name: "Change states",
            type: "ir.actions.act_window",
            res_model: "packages.pop.up",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: { default_selected_package_ids: selected_ids },
          });
        });
    },
  });
  var filterButtonView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
      Controller: FilterButton,
    }),
  });
  viewRegistry.add("filter_buttons", filterButtonView);
});

// odoo.define("ml_worldwide-main.refresh", function (require) {
//   "use strict";

//   var FormController = require("web.FormController");

//   FormController.include({
//     init: function (parent, model, renderer, params) {
//       this._super.apply(this, arguments);
//     },
//     _onFieldChanged: function (event) {
//       this._super.apply(this, arguments);
//       if (event.name == "field_changed") {
//         if (event.data.changes.freights_routes_shipment) {
//           location.reload();
//         }
//       }
//     },
//   });
// });
