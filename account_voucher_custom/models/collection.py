
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, AccessError


class customer_check(models.Model):
	_name = "customer.check"
	_inherit = ['mail.thread']
	_rec_name = 'partner_id'
	_description = "customers checks"

	@api.model
	def _default_currency(self):
		return self.env.user.company_id.currency_id

	def paid_amount_calc(self):
		return round(self.amount_posted + self.paid_amount , 2)

	def residual_amount_calc(self):
		return round(self.total_amount - (self.amount_posted + self.paid_amount) , 2)

	def amount_calc(self):
		return round(sum (line.amount for line in self.check_lines if line.paid_amount>0),2)

	def residual_calc(self):
		return round(sum (line.amount - line.paid_amount for line in self.check_lines) + self.amount_due , 2)

	@api.one
	@api.depends('check_lines.amount', 'check_lines.paid_amount', 'total_amount', 'paid_amount')
	def _compute_amount(self):
		self.amount = round(self.total_amount - self.paid_amount,2)
		self.amount_posted = round(sum (line.paid_amount for line in self.check_lines),2)
		self.amount_due = round(self.amount - self.amount_posted,2)


	@api.model
	def _default_journal(self):
		return self.env['account.journal'].search([('type', '=', 'sale')], limit=1)


	name = fields.Char('Sequance',help="Reference",readonly=True)
	state = fields.Selection([
		('draft','Draft'),
		('open', 'Open'),
		('marged', 'Marged'),
		('paid', 'Paid'),
		('cancel','Cancelled'),
	], 'Status', readonly=True, track_visibility='onchange', copy=False ,default='draft')

	partner_id = fields.Many2one('res.partner', 'Customer',required=True ,readonly=True, states={'draft':[('readonly',False)]})
	date = fields.Date('Date', required=True ,readonly=True ,default=datetime.now().strftime('%Y-%m-%d'))
	amount = fields.Float(string= 'Residual Amount', store=True, readonly=True, compute='_compute_amount')
	with_equal_periods= fields.Boolean('With Equal Periods', help="Check this box to let odoo creat your checks.",readonly=True, states={'draft':[('readonly',False)]} , default=True)
	total_amount= fields.Float(string= 'Total amount',readonly=True, states={'draft':[('readonly',False)]})
	paid_amount = fields.Float(string='paid amount',readonly=True,states={'draft':[('readonly',False)]})
	monthes = fields.Integer(string='Number of Investment',readonly=True, states={'draft':[('readonly',False)]})
	start_date = fields.Date('Start Date' ,readonly=True, default=fields.Date.today(), states={'draft':[('readonly',False)]})
	journal_id =fields.Many2one('account.journal', 'Journal',
		readonly=True, states={'draft':[('readonly',False)]} , domain="[('type', '=', 'sale')]",default=lambda self: self._default_journal())
	account_id =fields.Many2one('account.account', 'Account')
	check_lines = fields.One2many('customer.check.line', 'line_id', 'Check Lines' )
	periods = fields.Selection(
		[('1','Monthley'),
		 ('3','Every Three monthes'),
		 ('6','Every Sex monthes'),
		 ('12','Year')
				], 'Period', readonly=True,states={'draft':[('readonly',False)]} , default='1')
	amount_posted =fields.Float(string='Amount Posted', digits=dp.get_precision('Account'),
		store=True, readonly=True, compute='_compute_amount')
	amount_due =fields.Float(string='Amount Due ', digits=dp.get_precision('Account'),
		store=True, readonly=True, compute='_compute_amount')
	account_move_line_ids =fields.One2many('account.move.line','onc_check_id', 'Entries', readonly=True, states={'draft':[('readonly',False)]})
	move_id =fields.Many2one('account.move','Entries',readonly=True ,states={'draft':[('readonly',False)]} )
	# sale_order =fields.Many2one('sale.order','Sale Order',readonly=True)
	advance_amount =fields.Float('Advance amount')
	rack =fields.Integer('Rack Number')
	customer_bank_name =fields.Char('Customer Bank Name')
	serilaization =fields.Boolean('More Help ?', readonly=True, states={'draft':[('readonly',False)]})
	serial_amount =fields.Float(string= 'Amount')
	check_number = fields.Integer(string='Check Number',readonly=True, states={'draft':[('readonly',False)]})
	active =fields.Boolean(string='active',default=True)
	check_line_id =fields.Many2one('customer.check','Parent Line',readonly=True)
	related_lines =fields.One2many('customer.check','check_line_id','Related Lines',readonly=True)
	last_batch_number =fields.Integer(string='Last batch Number',default=1)
	rak_number = fields.Char('Rack Nmubers', help="Rack Number")
	currency_id = fields.Many2one('res.currency', string='Currency',
							   required=True, readonly=True, states={'draft': [('readonly', False)]},
							   default=_default_currency, track_visibility='always')
	
	def add_rak_num(self):
		for line in self.check_lines:
			line.rack = self.rak_number

	def create_check(self):
		active_id = self
		if active_id.amount <= 0:
			raise  UserError(_('Incorrect amount\nThere is now residual amount to create checks.'))
		elif active_id.monthes <= 0 :
			raise  UserError(_('Incorrect Number of Month\nThe value of Number of Investment must be more than 0.'))
		elif not active_id.periods :
			raise  UserError(_('period not selected\nplease select one type of periods'))
		else:
			amount_per_month = active_id.amount/active_id.monthes
			num_of_monthes = int (active_id.periods)
			investment = active_id.monthes
			return {
				'name': _('First Check Number'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'check.number',
				'type': 'ir.actions.act_window',
				'target':'new',
				'context':{
					'default_amount_per_month':amount_per_month,
					'default_start_date':active_id.start_date,
					'default_num_of_monthes':num_of_monthes,
					'default_investment':investment,
					'default_customer_check_id':active_id.id,
					'default_date':active_id.date,
					'default_type':'in',
					}
				}


	def draft_customer(self):
		if not self.check_lines:
			raise UserError(_('Check Lines \nPlease add some checks then try validate again ^__^'))
		else:
			if int(self.amount_due) != int(self.amount):
				raise UserError(_('Amount\nchecks amount and total amount are not equal . please review them again ^__^'))
			self.state = 'open'

	def open_customer(self):
		self.state = 'marged'

	def merge_customer(self):
		self.state = 'paid'


	def bank_rack(self):
		for customer in self:
			if not customer.rack:
				raise UserError(_('Rack\nYou did\'t entered Rack Number.can you add it please ^__^'))
			if not customer.customer_bank_name:
				raise UserError(_('Customer Bank Name\nYou did\'t entered Customer Bank Name.can you add it please ^__^'))

			for line in customer.check_lines:
				line.write({'rack':customer.rack , 'account_id':customer.customer_bank_name})
		return True
	def check_description(self):
		mapping = {
			'1':'الاول','2':'الثانى','3':'الثالث','4':'الرابع',
			'5':'الخامس','6':'السادس','7':'السابع','8':'الثامن',
			'9':'التاسع','10':'العاشر','11':'الحادى عشر','12':'الثانى عشر',
			'13':'الثالث عشر','14':'الرابع عشر','15':'الخامس عشر','16':'السادس عشر',
			'17':'السابع عشر','18':'الثامن عشر','19':'التاسع عشر','20':'العشرون',
			'21':'الحادى والعشرون','22':'الثانى والعشرون','23':'الثالث والعشرون','24':'الرابع والعشرون',
			'25':'الخامس والعشرون','26':'السادس والعشرون','27':'السابع والعشرون','28':'الثامن والعشرون',
			'29':'التاسع والعشرون','30':'الثلاثين','31':'الحادى والثلاثين','32':'الثانى والثلاثين',
			'33':'الثالث والثلاثين','34':'الرابع والثلاثين','35':'الخامس والثلاثين','36':'السادس والثلاثين',
			'37':'السابع والثلاثين','38':'الثامن والثلاثين','39':'التاسع والثلاثين','40':'الاربعين',
			'41':'الحادى و الاربعين ','42':'الثانى والاربعين ','43':'الثالث والاربعين','44':'الرابع والاربعين ',
			'45':'الخامس والاربعين ','46':'السادس والاربعين ','47':'السابع والاربعين ','48':'الثامن والاربعين ',
			'49':'التاسع والاربعين ','50':'الخمسين ','51':'الحادى والخمسين ','52':'الثانى والخمسين ',
			'53':'الثالث والخمسين ','54':'الرابع والخمسين ','55':'الخامس والخمسين ','56':'السادس والخمسين ',
			'57':'السابع والخمسين ','58':'الثامن والخمسين ',
			'59':'التاسع و الخمسين ','60':'الستين ','61':'الحادى والستين ','62':'الثانى والستين ',
			'63':'الثالث والستين ','64':'الرابع والستين ','65':'الخامس والستين ','66':'السادس والستين ',
			'67':'السابع والستين ','68':'الثامن والستين ','69':'التاسع والستين ','70':'السبعين ',
			'71':'الحادى والسبعين ','72':'الثانى والسبعين ','73':'الثالث والسبعين ','74':'الرابع والسبعين ',
			'75':'الخامس والسبعين ','76':'السادس والسبعين ','77':'السابع والسبعين ','78':'الثامن والسبعين ',
			'79':'التاسع والسبعين ','80':'الثمانون','81':'الحادى والثمانون','82':'الثانى والثمانون',
			'83':'الثالث والثمانون','84':'الرابع والثمانون','85':'الخامس والثمانون','86':'السادس والثمانون',
			'87':'السابع والثمانون','88':'الثامن والثمانون','89':'التاسع والثمانون','90':'التسعون',
			'91':'الحادى والتسعون','92':'الثانى والتسعون','93':'الثالث والتسعون ','94':'الرابع و التسعون ',
			'95':'الخامس والتسعون ','96':'السادس والتسعون ','97':'السابع والتسعون ',
			'98':'الثامن والتسعون ','99':'التاسع والتسعون ','100':'المئة'
		}
		cu_check_obj = self
		if not cu_check_obj.check_lines:
			raise UserError(_( 'Please add some checks then try again ^__^'))

		else:
			counter = cu_check_obj.last_batch_number
			for line in  cu_check_obj.check_lines:
				line.description = "القسط "+mapping[str(counter)]
				counter+=1

	def amount_check_number(self):
		for customer in self:
			if not customer.serial_amount:
				raise UserError(_('You did\'t entered Amount.can you add it please ^__^'))
			if not customer.check_number:
				raise UserError(_('You did\'t entered Check Number.can you add it please ^__^'))
			check_number = customer.check_number
			for line in customer.check_lines:
				line.write({'amount':customer.serial_amount , 'check_number':check_number})
				check_number = check_number + 1

		return True


class customer_check_line(models.Model):
	_name = 'customer.check.line'
	_order = 'due_date'
	_rec_name = 'description'
	_description = "customer checks details"


	def _get_move_check(self):
		res = {}
		for line in self :
			res[line.id] = bool(line.move_id)
			line.update({
				'move_check': res,
				})

	@api.depends('amount', 'currency_id', 'company_currency_id','due_date')
	def _compute_amount_in_base_currency(self):
		for line in self:
			#print ('-------------amount',line.amount)
			if line.currency_id and line.company_id and line.currency_id != line.company_id.currency_id:
				currency_id = line.currency_id
				#print('--------------- currency_id',line.amount,currency_id , line.company_id.currency_id)
				line.amount_base_currency = currency_id._convert(line.amount, line.company_id.currency_id, line.company_id, line.due_date or fields.Date.today())
				#print('---------------- amount_base_currency',line.amount_base_currency)

	@api.depends('amount', 'paid_amount')
	def _compute_payment_differance(self):
		for line in self:
			line.differance = int(line.amount) - int(line.paid_amount)
			 
	def _get_name(self):
		res = {}
		for line in self:
			if line.description and line.rack:
			 new_name = line.description+"   / Land " + \
							 line.land_id.realestate_num+"/"+line.due_date
			 res[line.id] = new_name
			 line.name=new_name

			else:
				new_name=line.due_date
				res[line.id] = new_name
				line.name=new_name


	description = fields.Char('Description')
	check_number = fields.Char('Reference', help="Check Number")
	rack = fields.Char('Rack Nmubers', help="Rack Number")
	date = fields.Date('Date', required=True)
	due_date = fields.Date('Due Date', required=True)
	amount = fields.Float('Total Amount', required=True, default=0.0)
	amount_base_currency = fields.Float(
		'Base Currency Amount', required=True, compute='_compute_amount_in_base_currency')
	differance = fields.Float('Diffrance', readonly=True,
	                          default=0.0, compute='_compute_payment_differance')
	line_id = fields.Many2one('customer.check', required=True, ondelete='restrict')
	move_ids = fields.One2many(
		string="Journal Enteries",
		comodel_name="account.move",
		inverse_name="check_line_id",
	)
	move_check = fields.Boolean(compute='_get_move_check', method=True, string='Posted', store=True)
	customer_bank = fields.Char('Customer bank Name')
	partner_id = fields.Many2one(related='line_id.partner_id',  relation="res.partner", string="Partner")
	state = fields.Selection(related='line_id.state', type="char",  string="state")
	check_line_id = fields.Many2one('customer.check.line',string='Parent Line',readonly=True)
	related_lines = fields.One2many('customer.check.line','check_line_id','Related Lines',readonly=True)

	name = fields.Char(compute='_get_name', string='Checks Name', store=True)
	check_status = fields.Selection([
		('revise','Revise'),
		('schedule','Schedule'),
		('merge','Merge'),
		('paid','Paid'),
		('not_arrive','Not Arrive')
	], 'check state',default='schedule')
	paid_amount = fields.Float(string="Paid Amount",readonly=True)
	revise_reson = fields.Char('Revise Reason')

	currency_id = fields.Many2one(relation='res.currency', string='Currency', readonly=True , related="line_id.currency_id")
	company_currency_id = fields.Many2one(
		'res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	company_id = fields.Many2one('res.company', string='Company', readonly=True,
							  default=lambda self: self.env.user.company_id)

	reservation_id = fields.Many2one('reservation.request',compute="_compute")

	def _compute(self):
		related_reserv = self.env['reservation.request'].search([('customer_check_id' , '=' , self.line_id.id)])
		print('--------------------- reservation_re',related_reserv)
		self.reservation_id = related_reserv.id

	
	def create_move(self):
		if self.line_id.state == 'draft':
			raise UserError(_('Please press validate button that appears on the top left ^_^ .'))
		return {
			'name': _('On Credit Checks'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'post.customer.check.action',
			'type': 'ir.actions.act_window',
			'target':'new',
			'context':{
				'default_name':self.check_number,
				'default_partner_id':self.line_id.partner_id.id,
				'default_amount': self.amount - self.paid_amount,
				'default_line_id':self.id,
				'default_description':self.description,
				'default_currency_id':self.currency_id.id,
				}

		}

	@api.multi
	def print_payment_report(self):
		if len(self.move_ids) > 1:
			return {
				'name': _('Payment Report'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'payment.report.action',
				'type': 'ir.actions.act_window',
				'target':'new',
				'context':{
					'default_partner_id':self.partner_id.id,
					'default_check_no':self.check_number,
					'default_line_id':self.id,
					'default_total':self.amount,
					},
			}
		else:
			return self.env.ref('account_voucher_custom.payment_report').report_action(self)


class PaymentReport(models.Model):
	_name="payment.report.action"
	_description = "payment report action"

	partner_id = fields.Many2one('res.partner', 'customer', required=True)
	check_no = fields.Integer('Check Number', required=True)
	line_id = fields.Many2one(
		'customer.check.line',
		string="line",
		required=True
	)
	payment_no = fields.One2many(
		'account.move',
		'payment_id',
		string="Payments",
		required=True
	)
	total = fields.Float('Check Amount', required=True)
	amount = fields.Float(compute="compute_amount",store=True)


	@api.depends('payment_no')
	@api.onchange('payment_no')
	def compute_amount(self):
		if len(self.payment_no) == 1:
			self.amount = self.payment_no.amount
		else:
			for line in self.payment_no:
				self.amount += line.amount


	def print_payment_record(self):
		return self.env.ref('account_voucher_custom.payment_moves_report').report_action(self)




