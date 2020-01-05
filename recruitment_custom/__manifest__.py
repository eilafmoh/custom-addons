# -*- coding: utf-8 -*-
##############################################################################
#
#    ZOO, zoo-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################
{
    'name': "Recruitment Custom",

    'summary': """ """,

    'description': """
        Long description of module's purpose
    """,

    'author': "zoo-business",
    'website': "http://www.zoo-business.com",
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_recruitment',
        'hr_custom',
    ],

    # always loaded
    'data': [
        'views/menus_view.xml'
        # 'views/view.xml',
        # 'views/hr_job_custom_view.xml',
        # 'report/recruitment_templates.xml',
        # 'report/recruitment_reports.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
