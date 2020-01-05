#App-Script business Solution
#    Copyright (C) 2017-2020 app-script (<http://www.app-script.com>).
{
	'name' : 'Loan',
	'version' : '0.1',
	'author' : 'Mahammed ogba',
	'category' : 'Human Resources',
	'description' : """

	""",

	'depends' : ['hr', 'hr_payroll', 'account','account_voucher','payroll_custom'],
	'data': [
		'security/security.xml',
		'security/ir.model.access.csv',
		'sequences/hr_loan_sequence.xml',
		# 'data/loan_payroll.xml',
		'views/hr_loan_view.xml',
		'views/hr_payroll_view.xml',
		
		
		
		#	'views/board_hr_loan_statistical_view.xml',
	],

	'installable': True,
	'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
