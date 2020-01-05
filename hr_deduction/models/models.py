# -*- coding: utf-8 -*-
##############################################################################
#
#    ZOO, zoo-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

class hr_deduct_conf(models.Model):
	_name = 'hr.deduct.conf'
	
	name = fields.Char(string="Name" , required=True)
	

class hr_deduction(models.Model):

	_name = 'hr.deduction'
	_inherit = ['mail.thread']
	_description= "HR Deduction"

	@api.one		
	def _compute_de_amount(self):
		de_amount = 0.00
		if self.deducted_by == 'hours':
			hours = self.wage / 176
			de_amount = self.hours_ded * hours 
		if self.deducted_by == 'amount':
			de_amount =self.amount
		self.de_amount = de_amount

	name = fields.Char(string="Ref:", default="/", readonly=True)
	date = fields.Date(string="Date Request", default=fields.Date.today(), readonly=True)
	employee_id = fields.Many2one('hr.employee', 
		string="Employee", required=True,domain=[('state', '=', 'in_service')])
	parent_id = fields.Many2one('hr.employee', related= "employee_id.parent_id", string="Manager",domain=[('state', '=', 'in_service')])
	company_id = fields.Many2one('res.company', related="employee_id.company_id", readonly=True, string="Fucalty")
	department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True, string="Department")
	job_id = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position")
	wage = fields.Float(string="Employee Salary", readonly=True)
	deducted_by  =  fields.Selection(string='Deduct By',required=True,
		selection=[('amount', 'Amount'), ('hours', 'Hours')] , default='amount'
	)

	# type_id =fields.Many2one('hr.deduct.conf' ,string="Type")
	hours_ded= fields.Float(string='Deduct Hours', help='Number of houres')
	amount = fields.Float(string=" Amount")
	de_amount = fields.Float(string="Deduct Amount" , compute='_compute_de_amount',readonly=True )
	
	description =fields.Html(string='Description')

	state = fields.Selection([
		('draft','Draft'),
		('approve','Approved'),
		('refuse','Refused'),
		('done','Done'),
	], string="State", default='draft', track_visibility='onchange', copy=False,)
	payroll_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
	
	@api.model
	def create(self, values):
		values['name'] = self.env['ir.sequence'].get('hr.deduction.req') or ' '
		res = super(hr_deduction, self).create(values)
		return res

	@api.multi
	def action_refuse(self):
		return self.write({'state': 'refuse'})
		
		
	@api.multi
	def action_set_to_draft(self):
		return self.write({'state': 'draft'})

	@api.multi
	def action_approve(self):
		self.write({'state': 'approve'})

	@api.multi
	def action_done(self):
		self.write({'state': 'done'})





class hr_emp_deduction(models.Model):

	_name = 'hr.emp.deduction'
	

	
	name = fields.Char(string="Ref:", default="/", readonly=True)
	date = fields.Date(string="Date Request", default=fields.Date.today(), readonly=True)
	employee_id = fields.Many2one('hr.employee', 
		string="Employee", required=True,domain=[('state', '=', 'in_service')])
	
	amount = fields.Float(string=" Amount")
	
	state = fields.Selection([
		('draft','Draft'),
		('approve','Approved'),
		('refuse','Refused'),
		('done','Done'),
	], string="State", default='draft', track_visibility='onchange', copy=False,)
	payroll_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
	