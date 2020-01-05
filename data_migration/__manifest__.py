# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Data Migration',
    'version': '1.0',
    'sequence': 1,
    'summary': 'show residential complexes and her lands ',
    'description': "",
    'website': 'https://www.app-script.com',
    'depends': ['residential_complex'],
    'data': [
        'security/ir.model.access.csv',
        'views/view.xml',
        'wizards/import_wizard_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
