# -*- coding: utf-8 -*-
##############################################################################
#
#    ZOO, zoo-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################
import time
import calendar
from datetime import date , datetime, timedelta
from dateutil import relativedelta
import babel
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp


class HRPayslip(models.Model):
	_inherit = 'hr.payslip'
	'''
	@api.multi
	def compute_sheet(self):
		super(HRPayslip, self).compute_sheet()
		hr_deduction = self.env['hr.deduction']
		payslip_line = self.env['hr.payslip.line']
		for payslip in self:
			deduction = hr_deduction.search([('state','=','approve'),('employee_id','=',payslip.employee_id.id)])
			for item in deduction:
				payslip_line.create({
					'name':item.type_id.rule_id.name,
					'category_id':item.type_id.rule_id.category_id.id,
					'amount':(item.de_amount * -1),
					'salary_rule_id':item.type_id.rule_id.id,
					'code':item.type_id.rule_id.code,
					'rate':100,
					'slip_id':payslip.id,
					'total':(item.de_amount * -1),
					'amount_fix':(item.de_amount * -1),
					'amount_percentage':0,
					'condition_range_min':0
				})
		return True
	'''


class hr_payslip(models.Model):
	_inherit = 'hr.payslip'

	employee_id = fields.Many2one('hr.employee', string='Employee',domain=[('state', '=', 'in_service')]) 

	@api.one
	def compute_total_dedection(self):
		total = 0.00
		for line in self.ded_ids:
			if line.state == 'approve':
				total += line.amount
		self.total_amount_ded = total

	ded_ids = fields.One2many('hr.emp.deduction', 'payroll_id', string="DED")
	total_amount_ded = fields.Float(
		string="Total DED Amount", compute='compute_total_dedection')

	@api.multi
	def get_ded(self):
		payslip_line = self.env['hr.emp.deduction']
		payslip_line.search([('payroll_id', '=', self.id)]).unlink()
		ded_ids = self.env['hr.deduction'].search([('employee_id', '=', self.employee_id.id),('state','=','approve'),('date','>=', self.date_from)])
		for loan in ded_ids:
			vals = {
				'name': loan.name,
				'amount': loan.amount,
				'employee_id': loan.employee_id.id,
				'payroll_id': self.id,
				'date': loan.date,
				'state': loan.state
			}
			payslip_line.create(vals)

	   
		return True

	@api.multi
	def compute_sheet(self):
		super(HRPayslip, self).compute_sheet()
		return True

	def compute_sheet(self):
		self.get_ded()
		self.get_loan()
		print('------------------------------- on compute sheet ded custom addons')
		for payslip in self:
			number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
			# delete old payslip lines
			payslip.line_ids.unlink()
			# set the list of contract for which the rules have to be applied
			# if we don't give the contract, then the rules to apply should be for all current contracts of the employee
			contract_ids = payslip.contract_id.ids or \
				self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)

			contract_ids2 = self.env['hr.contract'].browse(contract_ids)

			for con in contract_ids2:
				if con.trial_date_end:
					if self.date_from <= con.trial_date_end or self.date_from <= con.trial_date_end <= self.date_to:
						self.env['hr.salary.rule'].search([('code','=','BASIC')]).amount_python_compute = 'result = contract.trail_wage'
					else :
						self.env['hr.salary.rule'].search([('code','=','BASIC')]).amount_python_compute = 'result = contract.wage'
				else :
					self.env['hr.salary.rule'].search([('code','=','BASIC')]).amount_python_compute = 'result = contract.wage'

			lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]

			actual_lines = self.compute_net_per_day(lines)
			
			payslip.write({'line_ids': actual_lines, 'number': number}) 

			if (self.date_to - self.date_from).days + 1 == self.get_month():
				# write net salary in contract record
				net_record = self.env['hr.payslip.line'].search([('slip_id','=',self.id),('code','=','NET')]) 
				#print ('the toal is --------------',net_record.total)
				contract_ids2.write({'net_salary': net_record.total })
		return True

	def compute_net_per_day(self , lines):
		month_days = self.get_month()
		for line in lines:
			amount_per_day = 0
			
			if month_days == 28:
				amount_per_day = round(line[2]['amount'] / 28 , 2)
			elif month_days == 29:
				amount_per_day = round(line[2]['amount'] / 29 , 2)
			elif month_days == 30:
				amount_per_day = round(line[2]['amount'] / 30 , 2)
			elif month_days == 31:
				amount_per_day = round(line[2]['amount'] / 31 , 2)

			if self.date_from.day == 15:
				actual_amount = ((self.date_to - self.date_from).days) * amount_per_day
			else:
				actual_amount = ((self.date_to - self.date_from).days+1) * amount_per_day
			line[2]['amount'] = round(actual_amount,0)
			#print('uuuuuuuuuuuuuuuuuuuuuuuuuuuu',actual_amount)

		return lines

	def get_month(self):
		str_date = str(self.date_from)
		date = datetime.strptime(str_date , "%Y-%m-%d")

		month_days = calendar.monthrange(date.year , date.month)[1]
		return month_days

		   
	@api.model
	def hr_verify_sheet(self):
		self.compute_sheet()
		array = []
		for line in self.ded_ids:
			if line.paid:
				array.append(line.id)
				line.action_paid_amount()
			else:
				line.payroll_id = False
		self.ded_ids = array
		return self.write({'state': 'verify'})
