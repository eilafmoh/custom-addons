
from odoo import models, fields, api , _
		
class EmployeePromotion(models.Model):
	_name = 'hr.employee.promotion'
	_rec_name = 'employee_id'

	employee_id = fields.Many2one('hr.employee', string="Employee",
	domain="[('state','=', 'in_service')]",
	)
	old_job_id = fields.Many2one('hr.job', string='Old Job Position',related='employee_id.job_id')
	old_degree_id = fields.Many2one("hr.degree", string="Old Degree",related='employee_id.degree_id')
	new_job_id = fields.Many2one('hr.job', string='New Job Position')
	new_degree_id = fields.Many2one("hr.degree", string="New Degree",domain="[('job_id','=',new_job_id)]")
	
	approve_date = fields.Date('Approve Date',compute='_approve_date')
	last_promotion_date = fields.Date('Last Promotion Date',compute='_last_promotion_date')
	state = fields.Selection(
		[('draft', 'Draft'),
		('confirmed', 'Confirmed') ,
		('approved', 'Approved'),
		('reject','Reject')], string="State", default="draft")
	note = fields.Text(string="Note", )

	@api.onchange('employee_id')
	def _default_job(self):
		if self.employee_id:
			self.new_job_id = self.employee_id.job_id.id 

	def _approve_date(self):
		self.approve_date = fields.Date.today()

	def _last_promotion_date(self):
		last_promotion_id = max(self.search([('employee_id','=',self.employee_id.id)]).ids)
		if len(self.search([('employee_id','=',self.employee_id.id)]).ids) > 1:
			last_promotion = self.browse(last_promotion_id)
			self.last_promotion_date = last_promotion.approve_date

	def confirm_button(self):
		self.state = 'confirmed'

	def approve_button(self):
		con_id = max(self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')]).ids)
		self.env['hr.contract'].browse(con_id).write({
			'job_id': self.new_job_id.id, 
			'degree_id': self.new_degree_id.id,
			'wage':self.new_degree_id.amount
		})
		self.employee_id.write({
			'job_id': self.new_job_id.id, 
			'degree_id': self.new_degree_id.id,
		})
		self.state = 'approved'

	def set_reject_action(self):
		self.state = 'reject'