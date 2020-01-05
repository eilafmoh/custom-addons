# -*- coding: utf-8 -*-
##############################################################################
#
#    ZOO, zoo-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################

{
    'name': "Payroll Custom",

    'author': "app script",
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
       
        'hr_payroll','hr_contract','hr_custom' , 'recruitment_custom'
        
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'data/rules_data.xml',
        'views/configration.xml',
        'views/salary_structure_contract_view.xml',
 	'views/hr_salary_rule_views.xml',
        'views/hr_qualification.xml',
        'views/hr_overtime_view.xml',
        'views/employee_promotion_view.xml',

        'wizard/employee_details_wizard_view.xml',
        'wizard/gross_net_wizard_view.xml',
        'report/employee_details_template.xml',
        'wizard/employee_payroll_details_wizard_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
