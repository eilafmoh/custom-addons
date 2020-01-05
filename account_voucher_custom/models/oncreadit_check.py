
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError

class oncreadit_check(models.Model):
	_name = 'oncreadit.check'
	_inherit = ['mail.thread']
	_rec_name = 'name'
	_description = "on creadit Checks "

	@api.one
	@api.depends('check_lines.amount', 'check_lines.paid_amount')
	def _compute_amount(self):
		self.amount_posted = sum(line.paid_amount for line in self.check_lines)
		self.amount_due = self.amount - self.amount_posted

	name = fields.Char('Sequance', help="Reference")

	@api.model
	def create(self, vals):
		seq = self.env['ir.sequence'].next_by_code('oncreadit.check') or '/'
		vals['name'] = seq
		return super(oncreadit_check, self).create(vals)

	state = fields.Selection([
		('draft', 'Draft'),
		('cancel', 'Cancelled'),
		('open', 'Open'),
		('paid', 'Paid')
	], 'Status', track_visibility='onchange', copy=False, default='draft',
		help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed on credit checks. \
					\n* The \'open\' when voucher is in open status,on credit check has aserial number. \
					\n* The \'paid\' status is used when all check lines are paid \
					\n* The \'Cancelled\' status is used when user cancel on credit check.')

	partner_id = fields.Many2one('res.partner', 'Vendor', required=True, readonly=True, states={
								 'draft': [('readonly', False)]})
	reference = fields.Char('Transaction Reference', help="Transaction reference", readonly=True, states={
							'draft': [('readonly', False)]})
	date = fields.Date('Date', required=True, readonly=True, states={
					   'draft': [('readonly', False)]})
	amount = fields.Float('Total amount', required=True, readonly=True, states={
						  'draft': [('readonly', False)]})
	with_equal_periods = fields.Boolean(
		'With Equal Periods', help="Check this box to let odoo creat your checks.", readonly=True, states={'draft': [('readonly', False)]})
	monthes = fields.Integer(string='Number of Investment', readonly=True, states={
							 'draft': [('readonly', False)]})

	periods = fields.Selection([
		('1', 'Monthley'),
		('3', 'Every Three monthes'),
		('6', 'Every Sex monthes'),
		('12', 'Year')
	], 'Period', readonly=True, states={'draft': [('readonly', False)]})

	start_date = fields.Date('Start Date', readonly=True, states={
							 'draft': [('readonly', False)]})
	journal_id = fields.Many2one('account.journal', 'Journal', readonly=True, states={
	                             'draft': [('readonly', False)]})
	broker_account = fields.Many2one('account.account', 'Broker account', readonly=True, states={
									 'draft': [('readonly', False)]})
	check_lines = fields.One2many(
		'oncreadit.check.line', 'line_id', 'Check Lines', readonly=True,)
	amount_posted = fields.Float(
		string='Amount Posted', compute='_compute_amount')
	amount_due = fields.Float(string='Amount Due', compute='_compute_amount')
	invoice_id = fields.Many2one('account.invoice', 'Voucher',  readonly=True)
	voucher_id = fields.Many2one('account.voucher', 'Invoice', readonly=True)
	account_move_line_ids = fields.One2many(
		'account.move.line', 'onc_check_id', 'Entries', readonly=True, states={'draft': [('readonly', False)]})

	last_batch_number = fields.Integer(string='Last batch Number', default=1, readonly=True,
										states={'draft': [('readonly', False)]})

	def create_check(self):
		if self.amount <= 0:
			raise ValidationError(
				_('Incorrect amount \n The value of  Amount must be more than zero.'))
		elif self.monthes <= 0:
			raise ValidationError(
				_('Incorrect Number of Month \n The value of Number of Investment must be more than 0.'))
		elif not self.periods:
			raise ValidationError(
				_('period not selected \n please select one type of periods'))
		else:

			amount_per_month = self.amount/self.monthes
			num_of_monthes = int(self.periods)
			investment = self.monthes

			return {
				'name': _('First Check Number'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'check.number',
				'type': 'ir.actions.act_window',
				'target': 'new',
				'context': {
					'default_amount_per_month': amount_per_month,
					'default_start_date': self.start_date,
					'default_num_of_monthes': num_of_monthes,
					'default_investment': investment,
					'default_onc_check_id': self.id,
					#'default_journal_id': self.journal_id.id,
					'default_date': self.date,
					'default_type': 'out',
				}
			}

	def draft_on_credit(self):
		if not self.check_lines:
			raise ValidationError(
				_('Check Lines \n Please add some checks then try validate again ^__^'))
		else:
			sum = 0
			ref = ""
			for check in self.check_lines:
				ref += str(check.check_number)
				ref += " - "
				sum += check.amount

			if int(sum) != int(self.amount):
				raise ValidationError(
					_('Amount \n checks amount and total amount are not equal . please review them again ^__^'))

			# post_check = self.env['post.check.action']

			# journal_id = self.journal_id.id
			# partner_id = self.partner_id.id

			# for line in self.check_lines:
			# 	move_id = post_check.create_move(
			# 		line.check_number, self.journal_id.id)
			# 	if line.description:
			# 		name = line.description
			# 	else:
			# 		name = " / "
			# 	analytic_id = line.analytic_id.id

			# 	account_id = self.broker_account.id
			# 	credit_lines = post_check.create_move_line(
			# 		partner_id, name, move_id.id, account_id, 0, line.amount)

			# 	account_id = self.partner_id.property_account_payable_id.id
			# 	debit_lines = post_check.create_move_line(
			# 		partner_id, self.voucher_id.name, move_id.id, account_id, line.amount, 0)

			return self.write({
				'state': 'open',
				'name': self.reference,
			})

	def check_description(self):
		mapping = {
			'1': 'الاول', '2': 'الثانى', '3': 'الثالث', '4': 'الرابع',
			'5': 'الخامس', '6': 'السادس', '7': 'السابع', '8': 'الثامن',
			'9': 'التاسع', '10': 'العاشر', '11': 'الحادى عشر', '12': 'الثانى عشر',
			'13': 'الثالث عشر', '14': 'الرابع عشر', '15': 'الخامس عشر', '16': 'السادس عشر',
			'17': 'السابع عشر', '18': 'الثامن عشر', '19': 'التاسع عشر', '20': 'العشرون',
			'21': 'الحادى والعشرون', '22': 'الثانى والعشرون', '23': 'الثالث والعشرون', '24': 'الرابع والعشرون',
			'25': 'الخامس والعشرون', '26': 'السادس والعشرون', '27': 'السابع والعشرون', '28': 'الثامن والعشرون',
			'29': 'التاسع والعشرون', '30': 'الثلاثين', '31': 'الحادى والثلاثين', '32': 'الثانى والثلاثين',
			'33': 'الثالث والثلاثين', '34': 'الرابع والثلاثين', '35': 'الخامس والثلاثين', '36': 'السادس والثلاثين',
			'37': 'السابع والثلاثين', '38': 'الثامن والثلاثين', '39': 'التاسع والثلاثين', '40': 'الاربعين',
			'41': 'الحادى و الاربعين ', '42': 'الثانى والاربعين ', '43': 'الثالث والاربعين', '44': 'الرابع والاربعين ',
			'45': 'الخامس والاربعين ', '46': 'السادس والاربعين ', '47': 'السابع والاربعين ', '48': 'الثامن والاربعين ',
			'49': 'التاسع والاربعين ', '50': 'الخمسين ', '51': 'الحادى والخمسين ', '52': 'الثانى والخمسين ',
			'53': 'الثالث والخمسين ', '54': 'الرابع والخمسين ', '55': 'الخامس والخمسين ', '56': 'السادس والخمسين ',
			'57': 'السابع والخمسين ', '58': 'الثامن والخمسين ',
			'59': 'التاسع و الخمسين ', '60': 'الستين ', '61': 'الحادى والستين ', '62': 'الثانى والستين ',
			'63': 'الثالث والستين ', '64': 'الرابع والستين ', '65': 'الخامس والستين ', '66': 'السادس والستين ',
			'67': 'السابع والستين ', '68': 'الثامن والستين ', '69': 'التاسع والستين ', '70': 'السبعين ',
			'71': 'الحادى والسبعين ', '72': 'الثانى والسبعين ', '73': 'الثالث والسبعين ', '74': 'الرابع والسبعين ',
			'75': 'الخامس والسبعين ', '76': 'السادس والسبعين ', '77': 'السابع والسبعين ', '78': 'الثامن والسبعين ',
			'79': 'التاسع والسبعين ', '80': 'الثمانون', '81': 'الحادى والثمانون', '82': 'الثانى والثمانون',
			'83': 'الثالث والثمانون', '84': 'الرابع والثمانون', '85': 'الخامس والثمانون', '86': 'السادس والثمانون',
			'87': 'السابع والثمانون', '88': 'الثامن والثمانون', '89': 'التاسع والثمانون', '90': 'التسعون',
			'91': 'الحادى والتسعون', '92': 'الثانى والتسعون', '93': 'الثالث والتسعون ', '94': 'الرابع و التسعون ',
			'95': 'الخامس والتسعون ', '96': 'السادس والتسعون ', '97': 'السابع والتسعون ',
			'98': 'الثامن والتسعون ', '99': 'التاسع والتسعون ', '100': 'المئة'
		}
		if not self.check_lines:
			raise UserError(_('Please add some checks then try again ^__^'))
		else:
			counter = self.last_batch_number
			for line in self.check_lines:
				line.write({
					'description': "القسط "+mapping[str(counter)]
				})
				counter += 1
			return True


class oncredit_check(models.Model):
	_name = "oncreadit.check.line"
	_description = "on creadit checks details"

	def _get_move_check(self):
		res = {}
		for line in self:
			res[line.id] = bool(line.move_id)
		return res

	check_number = fields.Char('Reference', help="Check Number")
	date = fields.Date('Date', required=True)
	due_date = fields.Date('Due Date', required=True)
	amount = fields.Float('Total amount', required=True)
	line_id = fields.Many2one(
		'oncreadit.check', required=True, ondelete='restrict', select=True)
	move_ids = fields.One2many(
		string="Journal Enteries",
		comodel_name="account.move",
		inverse_name="on_creadit_check_line",
		readonly=True,
	)
	move_check = fields.Boolean(
		compute='_get_move_check',  string='Posted', store=True)
	journal_id = fields.Many2one('account.journal', 'Journal', )
	analytic_id = fields.Many2one(
		'account.analytic.account', 'Analytic Account')
	description = fields.Text('description')
	paid_amount = fields.Float(string="Paid Amount", readonly=True)
	check_status = fields.Selection([
		('revise', 'Revise'),
		('schedule', 'Schedule'),
		('merge', 'Merge'),
		('paid', 'Paid'),
		('not_arrive', 'Not Arrive')
	], 'check state', default='schedule')

	def create_move(self):
		if self.line_id.state == 'draft':
			raise ValidationError(
				_('Check State \n Please press validate button that appears on the top left ^_^ .'))
		if self.check_status != 'schedule':
			#TODO: review message
			raise ValidationError(
				_('Check State \n Please press validate button that appears on the top left ^_^ .'))
		return {
			'name': _('On Credit Checks'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'post.check.action',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': {
				'default_name': self.check_number,
				'default_partner_id': self.line_id.partner_id.id,
				'default_amount': self.amount - self.paid_amount,
				'default_line_id': self.id,
				'default_journal_id': self.journal_id.id,
			}

		}
