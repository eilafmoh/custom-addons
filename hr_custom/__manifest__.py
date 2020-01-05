    
{
    'name': "HR Custom",
    'author': "app script",

    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','account','hr_payroll','hr_contract'
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'data/data.xml',
        'views/hr_employee.xml',
        'views/hr_contract.xml',
        'views/hr_department.xml',
        'views/hr_degree.xml',
        'views/finice_deduction.xml',
        'views/hr_leaves.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
