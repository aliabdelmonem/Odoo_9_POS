odoo.define('pos_res_transfer_table.transfer_table', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var PopupWidget = require('point_of_sale.popups');
var _t = core._t;
var Model = require('web.DataModel');
var QWeb = core.qweb;

models.load_models({
    model: 'restaurant.table',
    label :'Tables',
    fields: ['name','id','floor_id'],
    loaded: function(self,tables){
         self.tables = tables;
    },
});

var TransferWidget = PopupWidget.extend({
template: 'TransferWidget',

    show: function(options){
            options = options || {};
            this._super(options);

            this.renderElement();
            },
    click_confirm: function(){
        var value = this.$('.transfer.select').val();
        this.gui.close_popup();
        if( this.options.confirm ){
            this.options.confirm.call(this,value);

            this.pos.get_order().table = this.pos.tables_by_id[value] ;
            this.pos.set_table(null);



        }
    },
  });
gui.define_popup({name:'transferwidget', widget: TransferWidget});



var TransferTable = screens.ActionButtonWidget.extend({
    template: 'TransferTable',
    button_click: function(){
        var self = this;
        this.gui.show_popup('transferwidget',{
                'title':_t('Transfer Table'),
                'confirm': function(value) {


                },
            });
    },
});

screens.define_action_button({
    'name': 'transfer_table',
    'widget': TransferTable,

});


});
