odoo.define('pos_product_gift_card.PosModel', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var Model = require('web.DataModel');
var PopupWidget = require('point_of_sale.popups');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;

var GreetingCardTemp = screens.ScreenWidget.extend({
        template: 'GreetingCardTemp',
        back_screen:   'product',

        init: function(parent, options){
            this._super(parent);
            var  self = this;
        },
        renderElement: function(){
            var self = this;
            this._super();

            this.$('.back').click(function(){
                self.gui.back();
            });

            this.$('.print_browser').click(function(){
                window.print();

            });

            this.$('.print_printer').click(function(){
               if(self.pos.config.iface_print_via_proxy){
                   var printers = self.pos.printers;
                   var receipt = QWeb.render('GreetingCardTemp',{widget:this});
                   printers[0].print(receipt);
               }else {
                   self.gui.show_popup('error',{
                       'title': _t('Error: No Connected Printers Found'),
                      'body': _t('You Must Have At Least One Printer Connected To Print The Card')});


               }

            });
        },


    })
gui.define_screen({'name': 'GreetingCardTemp', 'widget': GreetingCardTemp, });





var GiftCardForm = PopupWidget.extend({
template: 'GiftCardForm',
show: function(options){
    options = options || {};
    this._super(options);

    this.renderElement();
    this.$('input,text').focus();
    },
click_confirm: function(){
    var value = this.$('input,text').val();
    this.gui.close_popup();
    if( this.options.confirm ){
        this.options.confirm.call(this,value);

    }
    },
  });

gui.define_popup({name:'giftcardpopup', widget: GiftCardForm});


var PrintGiftButton = screens.ActionButtonWidget.extend({
    template: 'PrintGiftButton',
    button_click: function(){
        var self = this;
        this.gui.show_popup('giftcardpopup',{
                'title':_t('Greetings Card Form'),
                'confirm': function(value) {
                    var receiver = this.$('.to').val();
                    var message = this.$('.message').val();
                    var sender = this.$('.from').val();

                    document.getElementById('lbl_sender').innerHTML = '<b><u>From</u></b> : ' + sender;
                    document.getElementById('lbl_message').innerHTML = '<b><u>Message</u></b> : ' + message;
                    document.getElementById('lbl_receiver').innerHTML = '<b><u>To</u></b> : '+ receiver;

                    this.gui.show_screen('GreetingCardTemp');
                },
            });
    },


});

screens.define_action_button({
    'name': 'giftcard',
    'widget': PrintGiftButton,
    'condition': function(){
        return this.pos.config.iface_greeting_Card ;
    },
});

});
