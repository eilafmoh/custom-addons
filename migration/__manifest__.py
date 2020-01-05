# -*- coding: utf-8 -*-  
{
    'name': "HR Migration",

    'summary': """
        This module Manage HR data migration process""",

    'author': "Masa",
    'website': "http://www.masa.technology",
    'category': 'custom',
    'version': '1.0',
    'depends': ['hr'],
    'data': [
        
        'security/ir.model.access.csv',
        'views/view.xml',
        'wizard/migration_wizard_view.xml',
    ],  

    'installable':True,
    'auto_install':False,
    'application':True,  
}
