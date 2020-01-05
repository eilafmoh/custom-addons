# -*- coding: utf-8 -*-
# Copyright 2012-2013 Federico Manuel Echeverri Choux
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models , _
from odoo.exceptions import UserError, ValidationError
MODULE_UNINSTALL_FLAG = '_force_unlink'

class HrContractExtended(models.Model):
	_inherit = "hr.contract"

	employee_id = fields.Many2one('hr.employee', string='Employee',domain=[('state', '=', 'in_service')]) 
	trail_wage = fields.Float("Trail Wage")
	net_salary = fields.Float(string='Net Salary', readonly=True)
	contract_salary = fields.Float(string='Contract Salary')

	# medical = fields.Float('Medical')
	cola_subsidy = fields.Float('Cost of Living Subsidy')
	housing_subsidy = fields.Float('Cost of Housing Subsidy')
	other_allow = fields.Float('Other Allowances')
	transport = fields.Float('Transport')
	other_ded = fields.Float('Other Deduction')

	social_insurance = fields.Boolean('Social Insurance')
	health_insurance = fields.Boolean('Health Insurance')
	pit_exempted = fields.Boolean('Personal Income Tax')
	over_50 = fields.Boolean('Over 50')


	