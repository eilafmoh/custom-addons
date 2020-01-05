# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, fields, models, tools, _ 
from odoo.exceptions import  ValidationError

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	qualification_ids = fields.One2many('hr.employee.qualification' , 'employee_id' , domain=[('state','=','approved')])
	

class hr_qualification(models.Model):
	_name = "hr.qualification"
	_description = "Hr Qualification"

	name = fields.Char('Name',required=True)
	amount = fields.Float('Amount')
	active = fields.Boolean(string="Active",default=True)



class HREmployeeQualification(models.Model):
	_name = "hr.employee.qualification"

	employee_id = fields.Many2one('hr.employee' , string='Employee')
	qualification_id =  fields.Many2one('hr.qualification' , string='Qualification')
	qualification_date = fields.Date(string='Date')
	active = fields.Boolean(string="Active",default=True)
	note = fields.Text(string='Note')
	state = fields.Selection([
		('draft' , 'Draft') ,('confirmed' , 'Confirmed'),
		('reviewed' , 'Reviewed'),('approved' , 'Approved'),
		('stopped' , 'Stopped'),('refused' , 'Refused')] , 
		string="State" ,default="draft") 

	@api.multi
	@api.depends('employee_id', 'qualification_id ')
	def name_get(self):

		result = []
		for X in self:
			name = ( X.employee_id.name + ' - ' or "")+ ' ( ' + X.qualification_id.name  + ' ) '

			result.append((X.id, name)) 
			
		return result
   
	def confirm_button(self):
		self.state = 'confirmed'

	def review_button(self):
		self.state = 'reviewed'	

	def approve_button(self):
		self.write({'state': 'approved'})
		
	def stop_button(self):
		self.write({'state': 'stopped'})

	def refuse_button(self):
		self.write({'state': 'refused'})

	def set_to_draft(self):
		self.write({'state': 'draft'})
