# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
import time
import datetime
from openerp.osv.orm import except_orm

class hrCustody(models.Model):
	_name = "hr.custody"
	_inherit = ['mail.thread']
	_description = "Things with employee"

	_sql_constraints = [('employee_uniq', 'check(1=1)', 'No error'),]

	name = fields.Char(string="Name", default="/", readonly=True)
	date = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
	user_id = fields.Many2one('res.users', string="Made By",default=lambda self: self.env.user)
	employee_id =fields.Many2one('hr.employee', 'Employee Name',
			required=True)
	job_id = fields.Many2one('hr.job', string="Job Position",related='employee_id.job_id',)
	department_id = fields.Many2one('hr.department',string="Department" ,related='employee_id.department_id',)
	state = fields.Selection([
		('draft','Draft'),
		('to_approve','To Approve'),
		('with_employee','With Employee'),
		('done','Delivered'),
	], string="State", default='draft', track_visibility='onchange', copy=False,)
	custody_line_ids = fields.One2many(comodel_name='hr.custody.line', inverse_name='custody_id', string='')

	description = fields.Html('Description')
	note  = fields.Text(string='Note')
	
	
	@api.model
	def create(self, values):
		values['name'] = self.env['ir.sequence'].get('hr.custody.seq') or ' '
		res = super(hrCustody, self).create(values)
		return res

	@api.one
	def action_approve(self):
		if not self.custody_line_ids:
			raise except_orm(_('Please Add some custody to this employee'))
		else:
			self.write({
				'state':'to_approve'
			})

	@api.one
	def action_maneger_approve(self):
		if not self.employee_id.contract_id:
			raise except_orm(_('Make sure is that employee have Contract'),_("you can find it in contract menu"))
		
		for line in self.custody_line_ids:
			line.state='with_employee'
			
		self.write({
			'state':'with_employee'
		})

	# @api.one
	# def action_maneger_reject(self):
	# 	self.write({
	# 		'state':'refuse'
	# 	})


class hr_custody_line(models.Model):
	_name = "hr.custody.line"
	
	asset_id = fields.Many2one(comodel_name='account.asset.asset', string='Custody Product')
	to_deliver = fields.Boolean(string='Deliver ?')
	deliver_id = fields.Many2one(comodel_name='hr.custody.deliver', string='')
	custody_id = fields.Many2one(comodel_name='hr.custody', string='Custody Product')
	state = fields.Selection([
		('available', 'Available'),
		('with_employee','With Employee'),
		('done','Receved Done'),
	], string="State", default='available',
	)

	employee_id = fields.Many2one(comodel_name='hr.employee',related='custody_id.employee_id')
