
from odoo import models, fields, api , _
from odoo.exceptions import  ValidationError

class hr_custody_deliver(models.Model):
	_name = "hr.custody.deliver"
	_inherit = ['mail.thread']
	_description = "Things with employee"

	name = fields.Char(string="Name", default="/", readonly=True)
	date = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
	user_id = fields.Many2one('res.users', string="Made By",default=lambda self: self.env.user)
	employee_id =fields.Many2one('hr.employee', 'Employee Name',
			required=True)
	job_id = fields.Many2one('hr.job', string="Job Position",related='employee_id.job_id',)
	
	department_id = fields.Many2one('hr.department',string="Department" ,related='employee_id.department_id',)
	state = fields.Selection([
		('draft','Draft'),
		('running','Runnig'),
		('done','Done'),
	], string="State", default='draft', track_visibility='onchange', copy=False,)
	
	note  = fields.Text(string='Note')
	custody_line_ids = fields.One2many(comodel_name='hr.custody.line', 
		inverse_name='deliver_id', string='')


	@api.onchange('employee_id')
	def change_lines(self):
		emp_lines = self.env['hr.custody.line'].search([('employee_id','=',self.employee_id.id)])
		print('-------------------- emp_lines ',emp_lines)
		self.custody_line_ids = emp_lines

	@api.one
	def action_approve(self):
		self.write({
			'state':'running'
		})
	
	@api.one
	def action_maneger_approve(self):
		emp_lines = self.env['hr.custody.line'].search([('employee_id','=',self.employee_id.id)])
		for line in emp_lines:
			if line.to_deliver:
				line.state = 'done'
			else:
				raise ValidationError(_("There are some lines doesn't deliverd."))

		emp_lines_cus = self.env['hr.custody'].search([('employee_id','=',self.employee_id.id)])
		for line in emp_lines_cus:
			line.state = 'done'
			for lin in line.custody_line_ids:
				lin.state = 'done'
			self.state='done'
				
			
	@api.one
	def action_maneger_reject(self):
		self.write({
			'state':'refuse'
		})
