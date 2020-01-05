{
    'name': 'Cash Order',
    'version': '1.1',
    'author': 'App-Script For Software',
    'category': ' ',
    'sequence': 10,
    'summary': 'cash order',
    'description': """
""",
    'website': ' ',
    'depends': ['base', 'hr', 'account_voucher'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/hr_view.xml',
        'views/cash_request_view.xml',
        'views/beneficiary.xml',
        'reports/cash_order_report.xml',
        'reports/cash_order_report_view.xml',
        'views/views.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
