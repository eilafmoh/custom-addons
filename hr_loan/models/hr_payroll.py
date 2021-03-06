from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.osv import osv

class hr_payslip(models.Model):
	_inherit = 'hr.payslip'
	
	@api.one
	def compute_total_paid_loan(self):
		total = 0.00
		for line in self.loan_ids:
			if line.paid == True:
				total += line.paid_amount
		self.total_amount_paid = total
	
	loan_ids = fields.One2many('hr.loan.line', 'payroll_id', string="Loans")
	total_amount_paid = fields.Float(string="Total Loan Amount", compute= 'compute_total_paid_loan')
	
	@api.multi
	def get_loan(self):
		array = []
		current_month=0
		payslip_line = self.env['hr.loan.line']
		loan_ids = self.env['hr.loan.line'].search([('employee_id','=',self.employee_id.id),
		('month_number','=', self.date_from.month),('state','=','running')])

		if loan_ids:
			for line in loan_ids:
				if line.paid_date.month==self.date_from.month:
					current_month=self.date_from.month
	
		for loan in loan_ids:
			loan.write({
				'payroll_id': self.id,
				'paid':True,
				'state': 'paid'
			})
			loan.action_paid_amount()
		return array
		
	@api.model
	def hr_verify_sheet(self):
		self.compute_sheet()
		array = []
		for line in self.loan_ids:
			if line.paid:
				array.append(line.id)
				line.action_paid_amount()
			else:
				line.payroll_id = False
		self.loan_ids = array
		return self.write({'state': 'verify'})