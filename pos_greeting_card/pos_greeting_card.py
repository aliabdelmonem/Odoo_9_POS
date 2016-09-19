
from openerp.osv import fields, osv

class pos_config(osv.osv):
    _inherit = 'pos.config'
    _columns = {
        'iface_greeting_Card': fields.boolean('Allow Print Greetings Card', help='Allow the cashier to print greetings card.'),
 }
    _defaults = {
        'iface_greeting_Card': True,
    }
