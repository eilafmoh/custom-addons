# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the

from openerp import models, fields, api
import time
import datetime
import calendar
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from datetime import datetime, timedelta

class hr_end_service(models.Model):
	_inherit = 'account.invoice'

	end_service_id = fields.Many2one('employee.final.sattelment')



class hr_end_service(models.Model):
	_name = "hr.end.of.service"
	_inherit = ['mail.thread']

	_description = "Employee end of service process"

	@api.one
	def _get_old_loan(self):
		old_amount = 0.00
		loan_obj = self.env['hr.loan']
		for loan in loan_obj.search([('employee_id', '=', self.employee_id.id)]):
			old_amount += loan.balance_amount
		self.emp_loans = old_amount

	name = fields.Char(string="Name", default="#", readonly=True)
	employee_id = fields.Many2one(
		'hr.employee', 'Employee Name', help="The employee",domain=[('state', '=', 'in_service')])
	user_id = fields.Many2one(
		'res.users', string="Made By", default=lambda self: self.env.user)
	date = fields.Date(
		string="Date", default=fields.Date.today(), readonly=True)
	last_day_of_work = fields.Date(string="Last day of work")
	parent_id = fields.Many2one(
		'hr.employee', related="employee_id.parent_id", string="Manager")
	department_id = fields.Many2one(
		'hr.department', related="employee_id.department_id", readonly=True, string="Department")
	job_title = fields.Many2one(
		'hr.job', related="employee_id.job_id", readonly=True, string="Job Position")
	emp_exit_interview = fields.Many2one(
		'survey.survey', string="Employee Exit survey")
	emp_salary = fields.Float(
		string="Employee Salary", readonly=True)
	emp_loans = fields.Float(string="Employee Loan",
							compute='_get_old_loan')
	contract_id = fields.Many2one('hr.contract',string="Contract",)

	state = fields.Selection([
		('draft', 'Draft'),
		('wait_depart_manager', 'Waiting Depart Manager'),
		('wait_hr_manager', 'Waiting HR Manager'),
		# ('wait_finice_manager', 'Waiting finice Manager'),
		('wait_gm_manager', 'Waiting General Manager'),
		('refuse', 'Refused'),
		('done', 'Done'),
	], string="State", default='draft', track_visibility='onchange', copy=False,)
	exit_type = fields.Selection([
		('by_employee', 'End of contract'),
		('by_department_manager', 'Resignation'),
		('termination', 'Termination'),

	], string="Exit Type",  track_visibility='onchange', copy=False, required=True, readonly=True, states={'draft':
																										   [('readonly', False)]})
	datails = fields.Html('Other Details')
	reject_status = fields.Text()
	exit_reson = fields.Text(string="Exit Reson", required=True, readonly=True,
							 states={'draft': [('readonly', False)]})
	emp_confirm_date = fields.Date(string="Employee Confirm", readonly=True)
	dep_manager_confirm_date = fields.Date(
		string="Department manager Confirm", readonly=True)
	hr_manager_confirm_date = fields.Date(
		string="HR Manager Confirm", readonly=True)
	# finance_confirm_date = fields.Date(
	# 	string="Finance Manager Confirm", readonly=True)
	gm_confirm_date = fields.Date(
		string="General Manager Confirm", readonly=True)
	finice_department = fields.Boolean(string="Finice Department")
	hr_department = fields.Boolean(string="HR Department")
	company_covenant = fields.Boolean(string="Company Covenant")
	experince_certificate = fields.Boolean(string="Experince Certificate")
	hr_uniform = fields.Boolean(string="The Uniform")
	emp_card = fields.Boolean(string="Employee Card")
	hr_check_list_other = fields.Boolean(string="Other")
	finice_loan = fields.Boolean(string="The loan")
	finice_old_loan = fields.Boolean(string="Long Term Loan")
	finice_check_list_other = fields.Boolean(string="Other")
	experince_certificate = fields.Boolean(string="Experince Certificate")
	progress_bar = fields.Integer(string="Exit Progress", default=0)
	exit_servey = fields.Html(string="Exit Survey")
	final_statment_id = fields.Many2one('employee.final.sattelment')

	@api.model
	def create(self, values):
		values['name'] = self.env['ir.sequence'].next_by_code(
			'end.service.employee.seq') or ' '
		res = super(hr_end_service, self).create(values)
		return res

	# @api.onchange('finice_department')
	# def change_finice_department(self):
	# 	if self.finice_department:
	# 		self.progress_bar += 20
	# 	if self.finice_department == False:
	# 		if self.progress_bar > 0:
	# 			self.progress_bar -= 20

	# @api.onchange('hr_department')
	# def change_hr_department(self):
	# 	if self.hr_department:
	# 		self.progress_bar += 20
	# 	if self.hr_department == False:
	# 		if self.progress_bar > 0:
	# 			percintage = self.progress_bar
	# 			percintage -= 20
	# 			self.create({'progress_bar': percintage})

	# @api.onchange('company_covenant')
	# def change_company_covenant_department(self):
	# 	if self.company_covenant:
	# 		self.progress_bar += 20
	# 	if self.company_covenant == False:
	# 		if self.progress_bar > 0:
	# 			self.progress_bar -= 20

	# @api.onchange('experince_certificate')
	# def change_experince_certificate_department(self):
	# 	if self.experince_certificate:
	# 		self.progress_bar += 20
	# 	if self.experince_certificate == False:
	# 		if self.progress_bar > 0:
	# 			self.progress_bar -= 20

	@api.multi
	def action_approve(self):
		self.write({
			'state': 'wait_depart_manager',
			'emp_confirm_date': fields.Date.today()

		})

	@api.multi
	def action_reject(self):
		state = self.state
		if state == 'wait_depart_manager':
			self.reject_status = "reject in department Manager"
			self.state = "refuse"
		if state == 'wait_hr_manager':
			self.reject_status = "reject in HR Manager"
			self.state = "refuse"
		if state == 'wait_gm_manager':
			self.reject_status = "reject in General Manager"
			self.state = "refuse"

	@api.multi
	def action_hr_aprrove(self):
		custody_obj = self.env['hr.custody.line'].search([('employee_id','=',self.employee_id.id),('state','=','with_employee')])
		if custody_obj:
			raise except_orm(_('This employee has custody that not deliverd'))
		else:
			self.it_department = True
			self.progress_bar += 30
			self.write({
				# 'state': 'wait_finice_manager',
				'state': 'wait_gm_manager',
				'hr_manager_confirm_date': fields.Date.today()
			})
	
	# @api.multi
	# def action_finice_aprrove(self):
	# 	if self.finice_department == False:
	# 		raise except_orm(_(
	# 			' Check the Finice Department'))
	# 	else:
	# 		self.write({
	# 			'state': 'wait_gm_manager',
	# 			'finance_confirm_date':fields.Date.today()
	# 		})

	@api.multi
	def action_department_approve(self):
		self.write({
			'state': 'wait_hr_manager',
			'dep_manager_confirm_date': fields.Date.today()
		})

		self.progress_bar += 30


	@api.multi
	def action_gm_approve(self):
		annual_leave = 0
		# legal_leaves = self.employee_id.remaining_leaves
		public_holiday = 0
		un_paid = 0
		over_time = 0
		holiday_obj = self.env['hr.leave']
		final_sattelment_obj = self.env['employee.final.sattelment']
		emp_leves = holiday_obj.search(
			[('user_id', '=', self.employee_id.user_id.id)])
		for leve in emp_leves:
			if leve.type == 'remove':
				un_paid -= leve.number_of_days_temp

		   
		finial_sattelment_vals = {
			'employee_id': self.employee_id.id,
			'employee_salary': self.contract_id.net_salary,
			'annual_leave': annual_leave,
			'legal_leave': self.employee_id.remaining_leaves,
			'current_salary': self.emp_salary,
			'unpaid_leave': un_paid,
			'last_date': self.last_day_of_work,
			'emp_loan':self.emp_loans,
			'contract_id':self.contract_id.id
		}
		self.final_statment_id = final_sattelment_obj.create(finial_sattelment_vals)

		self.write({
			'state': 'done',
			'gm_confirm_date': fields.Date.today()
		})
		self.employee_id.write({'state': 'out_of_service'})

		if self.exit_type == 'by_employee':
			self.contract_id.write({'state':'ended'})
		elif self.exit_type == 'by_department_manager':
			self.contract_id.write({'state':'resigned'})
		elif self.exit_type == 'termination':
			self.contract_id.write({'state':'terminated'})
		self.progress_bar += 40

class employee_final_sattelment(models.Model):
	_name = "employee.final.sattelment"
	_description = "Employee finial sattelment process"

	@api.multi
	def _compute_salary(self):
		month_days = self.get_month_days()
		amount_per_day = 0.0
		if month_days == 28:
			amount_per_day = round(self.employee_salary / 28 , 2)
		elif month_days == 29:
			amount_per_day = round(self.employee_salary / 29 , 2)
		elif month_days == 30:
			amount_per_day = round(self.employee_salary / 30 , 2)
		elif month_days == 31:
			amount_per_day = round(self.employee_salary / 31 , 2)
		
		self.salary_per_day = amount_per_day

	name = fields.Char(string="Name", default="#", readonly=True)
	employee_id = fields.Many2one(
		'hr.employee', 'Employee Name', help="The employee",domain=[('state', '=', 'in_service')])
	date = fields.Date(
		string="Date", default=fields.Date.today(), readonly=True)
	employee_salary = fields.Float(
		string="Total Paysllip", readonly=True)
	last_date = fields.Datetime(string="Last Work Date", readonly=True)
	current_month_salary = fields.Boolean(string="With current month Salary ?")

	state = fields.Selection([
		('draft', 'Draft'),
		('in_progress', 'In Progress'),
		('done', 'Done'),

	], string="State",  track_visibility='onchange', copy=False, required=True, default="draft")
	annual_leave = fields.Float(string="Days Annual Leave")
	legal_leave = fields.Float(string="Legal Leave")
	unpaid_leave = fields.Float(string="Unpaid Leave", readonly=True)
	public_holiday = fields.Float(string="Public Holiday")
	over_time = fields.Float(string="Over Time Hours")
	over_amount = fields.Float(string="Over Time Amount",compute='_compute_overtime')
	remaining_days = fields.Integer(string="Remining Days")
	emp_loan = fields.Float(string="Employee Loans",readonly=True)
	salary_per_day = fields.Float(
		string="salary per day", compute="_compute_salary", readonly=True)
	current_salary = fields.Float(string="Current Month Salary")
	total_amount = fields.Float(string="Total amount", readonly=True)
	note = fields.Html(string="Note", readonly=True)

	# voucher_id = fields.Many2one('account.voucher', 'Voucher')
	contract_id = fields.Many2one('hr.contract',
		string="Contract",)
	invoice_id = fields.Many2one(
		string="Invoice",
		comodel_name="account.invoice",
		readonly=True,
	)

	@api.model
	def create(self, values):
		values['name'] = self.env['ir.sequence'].next_by_code(
			'end.service.final.sattelment.seq') or ' '
		res = super(employee_final_sattelment, self).create(values)
		return res

	@api.onchange('over_time')
	def _compute_overtime(self):
		contract = self.contract_id
		if contract:
			rule = contract.struct_id.rule_ids.search([('code','=','GROSS')])
			gross =  rule.compute_allowed_deduct_amount(contract)

			_calendar = contract.resource_calendar_id
			_date = fields.Datetime.from_string(self.date)
			work_data = {}
			if _calendar:
				start = _date.replace(day=1)
				num_days = calendar.monthrange(_date.year, _date.month)[1]
				end = _date.replace(day=num_days)
				work_data = self.employee_id.get_work_days_data(start,end, contract=contract,calendar=_calendar)
				gross_per_day = gross / work_data['days']
				gross_per_hour = gross_per_day / contract.resource_calendar_id.hours_per_day
				self.over_amount = 	gross_per_hour * self.over_time
				

	def get_month_days(self):
		str_date = str(self.date)
		date = datetime.strptime(str_date , "%Y-%m-%d")

		month_days = calendar.monthrange(date.year , date.month)[1]
		return month_days

	@api.multi
	def on_change_checkout(self):
		remain_days_salary = 0.0
		due_days = self.last_date.day

		if self.current_month_salary:
			remain_days_salary = self.employee_salary 
		else:
			remain_days_salary = due_days * self.salary_per_day
		
		allocate_amount = self.legal_leave * self.salary_per_day
		over_time_amount = self.over_amount
		emp_loan = self.emp_loan

		total_salary = remain_days_salary + allocate_amount + over_time_amount - emp_loan
		self.total_amount = total_salary


	def action_approve(self):
		self.state = 'in_progress'


	def action_department_approve(self):
		if not self.env.user.company_id.end_serv_acc:
			raise ValidationError(_('Please config the end of service account!'))
		
		if self.total_amount > 0:
			invoice_id = self.env['account.invoice'].create({
				'partner_id': self.employee_id.partner_id.id,
				'date': fields.Date.today(),
				'date_invoice' : fields.Date.today(),
				'type': 'out_invoice',
				'currency_id': self.employee_id.company_id.currency_id.id,
				'end_service_id' : self.id,
			})
			self.env['account.invoice.line'].create({
				'name': "End Of Service",
				'invoice_id': invoice_id.id,
				'price_unit': self.total_amount,
				'account_id': self.env.user.company_id.end_serv_acc.id,
			})
			invoice_id.action_invoice_open()
		
		else:
			invoice_id = self.env['account.invoice'].create({
				'partner_id': self.employee_id.partner_id.id,
				'date': fields.Date.today(),
				'date_invoice' : fields.Date.today(),
				'type': 'in_invoice',
				'currency_id': self.employee_id.company_id.currency_id.id,
				'end_service_id' : self.id,
			})
			self.env['account.invoice.line'].create({
				'name': "End Of Service",
				'invoice_id': invoice_id.id,
				'price_unit': self.total_amount * -1 ,
				############ مفروض يتغير الحساب للحساب الحتدخل فيهو القروش دي 
				'account_id': self.env.user.company_id.end_serv_acc.id,
			})
			invoice_id.action_invoice_open()

		self.write({
			'invoice_id':invoice_id.id,
			'state': 'done'
		})

		if self.emp_loan:
			loan_ids = self.env['hr.loan.line'].search([('employee_id','=',self.employee_id.id),('state','=','running')])
			for loan in loan_ids:
				loan.write({
					'paid_date':fields.Date.today(),
					'paid':True,
					'state': 'paid'
				})
				loan.action_paid_amount()

		# journal_id = self.env['account.journal'].search(
		# 	[('type', '=', 'purchase')], limit=1)
		 
		# voucher_id = self.env['account.voucher'].create({
		# 	#'partner_id': self.employee_id.id,
		# 	'amount': self.total_amount,
		# 	'journal_id': journal_id.id,
		# 	'account_id': self.env.user.company_id.loan_acc.id,
		# 	'date': self.date,
		# 	'state': 'draft',
		# 	'voucher_type': 'purchase',
		# 	'end_of_service_id': self.id,
		# })

		# self.env['account.voucher.line'].create({
		# 	'voucher_id': voucher_id.id,
		# 	'account_id': self.env.user.company_id.end_serv_acc.id,
		# 	'price_unit': self.total_amount,
		# 	'name': self.employee_id.name + ' ' + self.name,
		# })

		# self.write({
		# 	'voucher_id':voucher_id.id,
		# 	'state': 'done'
		# })

		
