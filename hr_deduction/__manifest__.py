# -*- coding: utf-8 -*-
##############################################################################
#
#   app-script
#
##############################################################################
{
    'name': "HR Deduction",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "App-script",
    'website': "http://www.app-script.com",

    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_custom','payroll_custom'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        
        #'views/salary_structure_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
