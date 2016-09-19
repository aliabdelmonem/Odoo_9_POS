{
    'name': 'POS Greetings Card',
    'version': '1.0',
    'category': 'Point of sale',
    'author': 'Ali Abdelmonem',
    'website': 'aliabdelmonem2@gmail.com',
    'summary': 'Print Greetings Card In POS ',
    'description': """ This Module Created For Print Greeings Card Via POS Only By Clicking The Button Of Greeting Card And Fill The

    Fields And Print""",
    'depends': ['point_of_sale'],
    'data': [
        'pos_greeting_card_view.xml',
        'views/templates.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
    'active': False,
    'auto_install': False,
}
