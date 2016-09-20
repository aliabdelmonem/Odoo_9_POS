from openerp import models ,fields , api


class installation_contract(models.Model) :
    _name = 'installation.contract'

    name = fields.Char(string='Contract Description',required=True)
    customer = fields.Many2one(comodel_name='res.partner',string="Customer",required=True,domain="[('customer', '=', True)]")
    start_date = fields.Date(string='Start Date',required=True)
    end_date = fields.Date(string='End Date',required=True)
    amount_to_contract= fields.Float(string='Contract Amount',required=True)
    down_payment = fields.Float(string='Down Payment (%)',required=True)
    contract_payments = fields.One2many(comodel_name='contract.payments',inverse_name='contract',string='Contract Payments')
    journal = fields.Many2one(comodel_name='account.journal',string='Journal',required=True)

    donw_payment_paid = fields.Boolean('Down Payment Paid',readonly=True)
    account_entry_d_payment = fields.Many2one(comodel_name='account.move',string='Down Payment Entry',readonly=True)

    account_for_deferred_reveunes = fields.Many2one(comodel_name='account.account',string='Deferred Account',domain="[('type', '=', 'other')]",required=True)
    account_for_revenues = fields.Many2one(comodel_name='account.account',string='Revenues Account',domain="[('type', '=', 'other')]",required=True)
    customer_account = fields.Many2one(comodel_name='account.account',string='Customer Account',domain="[('type', '=', 'receivable')]",required=True)

    no_money_back = fields.Boolean('No Money Back',readonly=True)
    account_entry_no_money_paid = fields.Many2one(comodel_name='account.move',string='No Money Back Entry',readonly=True)
    contract_items = fields.One2many(comodel_name='contract.items',inverse_name='contract',string='Items To Be Delivered')
    delivery_order_id = fields.Many2one(comodel_name='stock.picking' ,string='Delivery Order',readonly=True)
    src_location = fields.Many2one(comodel_name='stock.location' ,string="Source Location",required=True)
    delivery_order_created = fields.Boolean('Delivery Order Created',readonly=True)




    @api.multi
    def gen_amount_entry(self):

        amount_to_contract = self.amount_to_contract * self.down_payment
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')

        period_ids = period_obj.find(self.env.cr,self.env.uid,self.start_date, context=None)
        partner_id = self.customer

        debit_account = self.customer_account
        credit_account =self.account_for_deferred_reveunes

        def_journal = self.journal

        move_date = self.start_date
        move_vals = {
             'name': '/',
             'date': move_date,
             'ref': self.name +'First Payment',
             'period_id': period_ids and period_ids[0] or False,
             'journal_id': def_journal.id ,
        }
        move_id = move_obj.create(self.env.cr, self.env.uid, move_vals, context=self.env.context)

        print (move_id)
        move_line_obj.create(self.env.cr, self.env.uid, {
               'name': self.name,'ref': partner_id.name +'/'+ str(move_date)
              ,'move_id': move_id,'account_id':debit_account.id,
               'debit': amount_to_contract,'credit': 0.0,'period_id': period_ids and period_ids[0] or False,
                          'journal_id': def_journal.id, 'partner_id': partner_id.id,
                          'currency_id': False,
                          'amount_currency': 0.0, 'date': move_date,})
        move_line_obj.create(self.env.cr, self.env.uid, {
                          'name': self.name , 'ref': partner_id.name + '/'+ str(move_date),
                          'move_id': move_id,'account_id':credit_account.id,
                          'debit': 0.0,
                          'credit': amount_to_contract,'period_id': period_ids and period_ids[0] or False,
                          'journal_id': def_journal.id, 'partner_id': partner_id.id,
                          'currency_id': False,
                          'amount_currency': 0.0, 'date': move_date,
        })
        self.write({'account_entry_d_payment' : move_id,'donw_payment_paid':True , 'state' : 'stage_1'})


        return True


    @api.multi
    def gen_not_refund(self):

        amount_to_contract = self.amount_to_contract * self.down_payment
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')

        period_ids = period_obj.find(self.env.cr,self.env.uid,self.start_date, context=None)
        partner_id = self.customer

        debit_account = self.account_for_deferred_reveunes
        credit_account =self.account_for_revenues

        def_journal = self.journal

        move_date = self.start_date
        move_vals = {
             'name': '/',
             'date': move_date,
             'ref': self.name +'No Refund Money',
             'period_id': period_ids and period_ids[0] or False,
             'journal_id': def_journal.id ,
        }
        move_id = move_obj.create(self.env.cr, self.env.uid, move_vals, context=self.env.context)

        print (move_id)
        move_line_obj.create(self.env.cr, self.env.uid, {
               'name': self.name,'ref': partner_id.name +'/'+ str(move_date)
              ,'move_id': move_id,'account_id':debit_account.id,
               'debit': amount_to_contract,'credit': 0.0,'period_id': period_ids and period_ids[0] or False,
                          'journal_id': def_journal.id, 'partner_id': partner_id.id,
                          'currency_id': False,
                          'amount_currency': 0.0, 'date': move_date,})
        move_line_obj.create(self.env.cr, self.env.uid, {
                          'name': self.name , 'ref': partner_id.name + '/'+ str(move_date),
                          'move_id': move_id,'account_id':credit_account.id,
                          'debit': 0.0,
                          'credit': amount_to_contract,'period_id': period_ids and period_ids[0] or False,
                          'journal_id': def_journal.id, 'partner_id': partner_id.id,
                          'currency_id': False,
                          'amount_currency': 0.0, 'date': move_date,
        })

        self.write({'no_money_back' : True , 'account_entry_no_money_paid' : move_id})
        return True

    @api.multi
    def gen_delivery_order(self):
        stock_picking_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        stock_picking_type = self.env['stock.picking.type'].search([('code','=','outgoing'),('default_location_src_id','=',self.src_location.id)])
        print (stock_picking_type)

        picking_vals = {
            'partner_id': self.customer.id,'origin' : self.name ,'picking_type_id' :stock_picking_type.id ,'move_type' : 'direct',
        }

        stock_picking = stock_picking_obj.create(picking_vals)


        for items in self.contract_items :
            move_vals = {
                'picking_id' :stock_picking.id,
                'product_id' : items.product.id,
                'procure_method' : 'make_to_stock',
                'product_uom_qty' :items.product_qty,
                'product_uom' : items.product.uom_id.id,
                'name' : items.product.name,
                'location_id' :self.src_location.id,
                'location_dest_id' : self.customer.property_stock_customer.id


            }
            stock_move_obj.create( move_vals)

        self.write({'delivery_order_id' : stock_picking.id , 'delivery_order_created' : True})


        return True





class contract_payments(models.Model):
    _name = 'contract.payments'

    name = fields.Char(string='Payment Desc',required=True)
    due_date = fields.Date(string='Due Date',required=True)
    amount = fields.Float(string='Payment Amount',required=True)
    percentage = fields.Float(string='Percentage %',required=True)
    contract = fields.Many2one(comodel_name='installation.contract',string='Contract',default=lambda self: self.env.context.get('contract', False),)
    stage = fields.Selection(selection= [('stage_3', 'Ducts Installation'),('stage_4', 'Internal Machines'),
         ('stage_5', 'External Machines'),('stage_6','Operation')], string='Stage')
    paid = fields.Boolean(string='Posted')
    move_id = fields.Many2one(comodel_name='account.move',string='Entry',readonly=True)

    estimate_start = fields.Date(string='Estimate Start Date')
    estimate_end = fields.Date(string='Estimate End Date')
    actual_start = fields.Date(string='Actual Start Date')
    actual_end = fields.Date(string='Actual End Date')







    @api.onchange('percentage')
    def _check_change(self):
        self.amount = self.percentage * self.contract.amount_to_contract

    @api.multi
    def gen_payment_entry(self):
        amount = self.amount
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')

        period_ids = period_obj.find(self.env.cr,self.env.uid,self.due_date, context=None)
        partner_id = self.contract.customer

        debit_account = self.contract.customer_account
        credit_account =self.contract.account_for_revenues

        def_journal = self.contract.journal

        move_date = self.due_date
        move_vals = {
             'name': '/',
             'date': move_date,
             'ref': self.name + ' - '+self.stage,
             'period_id': period_ids and period_ids[0] or False,
             'journal_id': def_journal.id ,
        }
        move_id = move_obj.create(self.env.cr, self.env.uid, move_vals, context=self.env.context)

        move_line_obj.create(self.env.cr, self.env.uid, {
               'name': self.name,'ref': partner_id.name +'/'+ str(move_date)
              ,'move_id': move_id,'account_id':debit_account.id,
               'debit': amount,'credit': 0.0,'period_id': period_ids and period_ids[0] or False,
                          'journal_id': def_journal.id, 'partner_id': partner_id.id,
                          'currency_id': False,
                          'amount_currency': 0.0, 'date': move_date,})
        move_line_obj.create(self.env.cr, self.env.uid, {
                          'name': self.name , 'ref': partner_id.name + '/'+ str(move_date),
                          'move_id': move_id,'account_id':credit_account.id,
                          'debit': 0.0,
                          'credit': amount,'period_id': period_ids and period_ids[0] or False,
                          'journal_id': def_journal.id, 'partner_id': partner_id.id,
                          'currency_id': False,
                          'amount_currency': 0.0, 'date': move_date,
        })
        self.write({'move_id' : move_id,'paid':True })


        install_contract_obj = self.env['installation.contract'].browse(self.contract.id)

        install_contract_obj.write({'state' : self.stage})




        return True

class contract_items(models.Model):
    _name = 'contract.items'

    product = fields.Many2one(comodel_name='product.template' , string="Product")
    product_qty = fields.Float(string="Quantity")
    contract = fields.Many2one(comodel_name='installation.contract',string='Contract',default=lambda self: self.env.context.get('contract', False),)





