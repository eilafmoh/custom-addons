# -*- coding: utf-8 -*-
##############################################################################
#
#    App-Script business Solution
#    Copyright (C) 2017-2020 app-script (<http://www.app-script.com>).
##############################################################################
{
    'name' : 'HR Incentive',
    'summary': """ """,

    'description': """
        Long description of module's purpose
    """,

    'author': "app-script",
    'website': "http://www.app-script.com",

    'category': 'HR',
    'version': '0.1',

    'depends':['payroll_custom','account_voucher','hr_contract'],
    
    'data' : [
        'data/sequence.xml',
        'views/hr_incentive_view.xml',
        'views/res_config_view.xml',
        'report/incentive_report.xml',
        'report/incentive_templates.xml',
        'security/ir.model.access.csv',
    ],

    'installable':True,
    'auto_install':False
}

