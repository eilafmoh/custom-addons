# -*- coding: utf-8 -*-
##############################################################################
#
#    App-Script business Solution
#    Copyright (C) 2017-2020 app-script (<http://www.app-script.com>).
#
##############################################################################
{
    'name' : 'End Of Service',
    'author': "App-script",
    'website': "http://www.app-script.com",

    'category': 'HR',
    'sequence': 320,
    
    'summary' : 'custom attendce , contract,',
    'description' : "hr end of service and finall sattelment",
    'depends' : [
        'survey',
        'hr_loan',
         'hr_custody',
    ],
    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/end_service_employee_seq.xml',
        'views/hr_end_service.xml',
        
    ],

    'installable' : True,
    'application' : False,
}
