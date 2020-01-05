# -*- coding: utf-8 -*-
##############################################################################
#
#    ZOO, zoo-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################
from odoo import models, fields, api , _
from odoo.exceptions import  ValidationError


class HrCustom(models.Model):
	_inherit = 'hr.employee'

	@api.model
	def _get_type(self, context=None):
		if self._context.get('employee_type', False):
			return self._context['employee_type']

	state = fields.Selection([("draft", "Draft"),
					  ("in_service", "In Service"),
					  ("out_of_service", "Out of Service") ], default='draft',string="Status")
	pass_port_img = fields.Binary(string='Passport')
	pass_port_exp_data = fields.Date(string='Expairation Date')
	drive_lincese = fields.Binary(string='Drive Lincese')
	drive_lincese_end = fields.Date(string='Exparition Date')
	expert_year = fields.Integer(string='Years of experience')
	my_company_year = fields.Integer(string='My Company Year')
	emp_code = fields.Char('Employee Code' , readonly=True)
	structure_id = fields.Many2one('hr.payroll.structure',string="Salary Structure", readonly=True , store=True)
	degree_id = fields.Many2one("hr.degree", string="Degree", readonly=True , store=True)
	is_acadimic = fields.Boolean(string='Is Academic')
	employment_date =fields.Date(string="Employment Date")
	first_employment_date =fields.Date(string="First Employment Date")
	employee_type = fields.Selection([('trainee', 'Trainee'),('conscript', 'Conscript'),
	('employee', 'Employee'),('contractor', 'Contractor'),], string='Employee Type',default=_get_type)
	join_date = fields.Date('Join Date')
	partner_id = fields.Many2one('res.partner', 'Related Partner')
	old_id = fields.Char('olld')
	
	@api.one
	def bt_in_service(self):
		self.state = "in_service"

	@api.model
	def create(self,vals):
		vals['emp_code'] = self.env['ir.sequence'].next_by_code('hr.employee.seq.code')
		return super(HrCustom,self).create(vals)

	def get_work_days_data(self, from_datetime, to_datetime, contract=None,calendar=None):
		"""
		modify the origin method in resource ==> resource_mixin 
		@param contract: payslip contract 
		@param date_from: date field
		@param date_to: date field
		@return: returns dictionary off employee worked days and hours based on employee contract types
		"""
		if calendar :
			return super(HrCustom, self).get_work_days_data(from_datetime,to_datetime,calendar)    
	

class HrDegree(models.Model):
	_name="hr.degree"

	name = fields.Char('Name',required=True)
	job_id = fields.Many2one('hr.job',string="Job Position",required=True)
	amount = fields.Float('Amount',required=True)

class HrJob(models.Model):
	_inherit="hr.job"

	degree_ids = fields.One2many('hr.degree','job_id',string="Degrees",required=True)
	


