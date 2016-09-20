from openerp.osv import fields, osv


class installation_contract(osv.osv):
    _inherit = 'installation.contract'
    _columns =  {'state' : fields.selection(
        [('stage_1', 'Contract Signed'),('stage_2', 'Draft Agreements'),
         ('stage_3', 'Ducts Installation'),('stage_4', 'Internal Machines'),
         ('stage_5', 'External Machines'),('stage_6','Operation')],'Status',select=True,),}
