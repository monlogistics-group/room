
odoo.define('ml_worldwide-main.WorldwideFreigthsModel', function (require) { 
    "use strict";
    var core = require('web.core');
    var dialogs = require('web.view_dialogs');
    var registry = require('web.field_registry');
    var rel_fields = require('web.relational_fields');
    var _t = core._t;

    var FieldMany2ManyTagLinks = rel_fields.FieldMany2ManyTags.extend({
        
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _render: function () {
            console.log('-------');
            this._super.apply(this, arguments);
            
            var childNodes = this.$el[0].childNodes;
            for (var i = 0; i < childNodes.length; i++) {
                if (childNodes[i].tagName == "DIV") {
                    childNodes[i].className = childNodes[i].className + ' ' + 'o_tag_color_' + i;
                    childNodes[i].style.cursor = 'pointer';
                    console.log(i); 
                }
            }
        },
        get_badge_id: function (el) {
        if ($(el).hasClass('badge')) return $(el).data('id');
            return $(el).closest('.badge').data('id');
        },
        events: _.extend({}, rel_fields.FieldMany2ManyTags.prototype.events, {
        'click .badge': function (e) {
            e.stopPropagation();
            var self = this;
            var record_id = this.get_badge_id(e.target);
            new dialogs.FormViewDialog(self, {
                    res_model: self.field.relation,
                    res_id: record_id,
                    context: self.record.getContext(),
                    title: _t('Open: ') + self.field.string,
                    readonly: !self.attrs.can_write,
                }).on('write_completed', self, function () {
                    self.dataset.cache[record_id].from_read = {};
                    self.dataset.evict_record(record_id);
                    self.render_value();
                }).open();
            }
        }),
    });

    registry.add('many2many_taglinks', FieldMany2ManyTagLinks);

    return {
        FieldMany2ManyTagLinks: FieldMany2ManyTagLinks
    };
        
});

odoo.define('ml_worldwide-main.custom_radio', function (require) {
    "use strict";
    var core = require('web.core');
    var registry = require('web.field_registry');
    var rel_fields = require('web.relational_fields');
    var _t = core._t;
    var ajax = require("web.ajax");
    var FieldRadio = rel_fields.FieldRadio;

    var custom_radio = FieldRadio.extend({
        init: function (parent, context) {
            this._super.apply(this, arguments);
            this.type = parent;
          },
        _render: function () {
            var type = this.type['state']['data']['type']['data']['display_name'];
            var loaded_id
            var unloaded_id
            var cs_id
            var formdc_id
            var fc_id
            var cf_id
            var thc_id
            var storage_id
            for(let i = 0; i<this.purpose_data.length; i++){
                if(this.purpose_data[i].name == 'Loaded'){
                    loaded_id = this.purpose_data[i].id
                }
                else if(this.purpose_data[i].name == 'Unloaded'){
                    unloaded_id = this.purpose_data[i].id
                }
                else if(this.purpose_data[i].name == 'Clearance Service'){
                    cs_id = this.purpose_data[i].id
                }
                else if(this.purpose_data[i].name == 'Form Declaration Cost'){
                    formdc_id = this.purpose_data[i].id
                }
                else if(this.purpose_data[i].name == 'Form Cost'){
                    fc_id = this.purpose_data[i].id
                }
                else if(this.purpose_data[i].name == 'Clearance Fee'){
                    cf_id = this.purpose_data[i].id
                }
                else if(this.purpose_data[i].name == 'THC'){
                    thc_id = this.purpose_data[i].id
                }
                else if(this.purpose_data[i].name == 'Storage'){
                    storage_id = this.purpose_data[i].id
                }
            }
            if (type == 'Package'){
                this.type['__parentedChildren'][10]['values'] = [
                    [loaded_id,'Loaded'],
                    [unloaded_id,'Unloaded'],
                ]
            }
            else if(type == 'Customs'){
                this.type['__parentedChildren'][10]['values'] = [
                    [cs_id,'Clearance Service'],
                    [formdc_id,'Form Declaration Cost'],
                    [fc_id,'Form Cost'],
                    [cf_id,'Clearance Fee'],
                ]
            }
            else if(type == 'THC'){
                this.type['__parentedChildren'][10]['values'] = [
                    [thc_id,'THC'],
                    [storage_id,'Storage'],
                ]
            }
            this._super.apply(this, arguments);
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
              model: "freights.service",
              method: "get_filtered_purpose_data",
            }).then(function (result) {
              self.purpose_data = result;
            });
            return $.when(def1);
        },
    });

    registry.add('custom_radio', custom_radio);
    return custom_radio
})
