# -*- coding: utf-8 -*-
##############################################################################
#
#    App-script,app-script-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################
{
    'name' : 'Hr custody',
    'author': "App-Script",
    'website': "http://www.app-script.com",

    'category': 'HR',
    'sequence': 320,
    
    'summary' : 'covenant in employee',
    'description' : "Employee custody",
    'depends' : [
        'hr',
        'account_asset','payroll_custom'
    ],
    'data' : [
        'security/custody_security.xml',
        'security/ir.model.access.csv',
        'sequence/custody_seq.xml',
        'views/hr_custody_view.xml',
        'views/custody_delivery_view.xml',
        # 'report/custody_report_template.xml',
        # 'report/custody_dev_report.xml',
        # 'report/report_menu.xml',
       
    ],

    'installable' : True,
    'application' : True,
}
