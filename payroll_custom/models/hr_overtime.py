
from datetime import datetime
import calendar
from odoo import api, fields, models, tools, _ 

class Overtime(models.Model):
	_name = "hr.overtime"
	_rec_name = 'employee_id'

	employee_id = fields.Many2one('hr.employee',required=True)
	hour = fields.Float('Hours',required=True)
	holiday = fields.Boolean(string="In Holiday")
	amount = fields.Float('Amount',compute='calc_amount')
	date = fields.Date(
		string="Date", default=fields.Date.today(), readonly=True)
	state = fields.Selection([
		('draft', 'Draft'),
		('approve', 'Approved'),
		('done', 'Done'),
	], string="State", default='draft')
	voucher_id = fields.Many2one('account.voucher', 'Voucher')

	@api.one
	@api.depends('hour','holiday')
	def calc_amount(self):
		contract = self.env['hr.contract'].search([
			('employee_id','=',self.employee_id.id),
			('state','=','open')
		])
		if len(contract) > 1:
			contract = self.env['hr.contract'].browse(max(contract.ids))
		
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
				
				if self.holiday:
					self.amount = gross_per_hour * self.hour * 2
				else:
					self.amount = gross_per_hour * self.hour

	def to_approve(self):
		self.state = 'approve'

	def to_done(self):
		journal_id = self.env['account.journal'].search(
			[('type', '=', 'purchase')], limit=1)

		voucher = self.env['account.voucher'].create({
			'partner_id': self.employee_id.partner_id.id,
			'amount': self.amount,
			'journal_id': journal_id.id,
			'account_id': self.employee_id.partner_id.property_account_payable_id.id,
			'date': fields.Date.today(),
			'state': 'draft',
			'voucher_type': 'purchase',
		})

		self.env['account.voucher.line'].create({
			'voucher_id': voucher.id,
			'account_id': self.env.user.company_id.over_time_acc.id,
			'price_unit': self.amount,
			'name': self.employee_id.name + ' Overtime',
		})

		self.write({
			'voucher_id':voucher.id,
			'state': 'done'
		})


