
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime, timedelta

class post_check_action(models.Model):
    _name = "post.check.action"
    _description = "Check posting"

    name = fields.Char('Check Number', help="Reference", required=True)
    partner_id = fields.Many2one('res.partner', 'Vendor', required=True)
    amount = fields.Float('Amount', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    line_id = fields.Many2one('oncreadit.check.line')

    def create_move(self, ref, journal_id):
        move = self.env['account.move']
        vals = {
            'ref': ref,
            'journal_id': journal_id,
        }
        return move.create(vals)

    def create_move_line(self, partner_id, name, move_id, account_id, debit, credit):
        move_line = self.env['account.move.line']
        vals = {
            'partner_id': partner_id,
            'name': name,
            'move_id': move_id,
            'account_id': account_id,
            'debit': debit,
            'credit': credit,
        }
        return move_line.with_context(check_move_validity=False).create(vals)

    def update_state(self, check_line_obj,invoice):
        if check_line_obj.amount == check_line_obj.amount_posted:
            check_line_obj.state = 'paid'
        # TODO it needs some refactoring
        # flag = True
        # for line in check_line_obj.check_lines:
        #     if not line.move_id:
        #         flag = False
        # if flag:
        #     check_line_obj.write({'state': 'paid'})
            # if 1 == 1:
            # 	# TODO it came from voucher 'voucher must closed '
            # 	print('on voucher ')
        # if self.line_id.line_id.amount_due == 0:
        #     self.line_id.line_id.write({'state': 'paid'})
        #     if invoice:
        #         invoice.write({'state': 'paid'})

    def Post_check(self):
        if self.amount > (self.line_id.amount - self.line_id.paid_amount):
            raise UserError(
                _('It seems that amount you want to pay is more than check amount ,, can you please post current check and register partial payment on next check *_^'))
        ref = self.line_id.check_number
        journal_id = self.journal_id.id
        print ('=========================================='.self.line_id.line_id.project_id.currency_id.id)

        payment_method_id = self.env['account.payment.method'].search([('payment_type' ,'=' , 'outbound')] ,limit=1)
        invoice_id = self.env['account.invoice'].with_context(active_test=False).search([('project_id', '=', self.line_id.line_id.project_id.id),('partner_id','=',self.line_id.line_id.partner_id.id)])
        payment_id = self.env['account.payment'].create({
            'invoice_ids':[(6, 0,invoice_id.ids)],
            'amount' : self.amount,
            'currency_id' :self.line_id.line_id.project_id.currency_id.id,
            'journal_id':self.journal_id.id,
            'payment_date' : datetime.now(),
            'payment_method_id' :  payment_method_id.id,
            'payment_type' : 'outbound',
            'partner_id' : self.line_id.line_id.partner_id.id,
            'partner_type' : 'supplier',
            'state' : 'draft'
            })
        payment_id.action_validate_invoice_payment()
        paid_amount = self.line_id.paid_amount + self.amount
        self.line_id.write({
            #'move_id': move_id.id,
            'paid_amount': paid_amount,
            'check_status': 'paid' if paid_amount == self.line_id.amount else 'schedule',
            'move_check': True if paid_amount == self.line_id.amount else False
        })

        self.update_state(self.line_id.line_id , invoice_id)

class post_customer_check_action(models.Model):
    _name = "post.customer.check.action"
    _description = "posting customer check"

    name = fields.Char('Check Number', help="Reference", required=True)
    partner_id = fields.Many2one('res.partner', 'customer', required=True)
    amount = fields.Float('Amount', required=True)

    journal_id = fields.Many2one(
        'account.journal', 'Journal', required=True)
    line_id = fields.Many2one('customer.check.line')
    description = fields.Char('Description', required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,)
    company_currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)

    def create_move(self, ref, journal_id):
        move = self.env['account.move']
        vals = {
            'ref': ref,
            'journal_id': journal_id,
        }

        return move.create(vals)

    def create_move_line(self, partner_id, name, move_id, account_id, debit, credit ,invoice_id):
        move_line = self.env['account.move.line']
        vals = {
            'partner_id': partner_id,
            'name': name,
            'move_id': move_id,
            'account_id': account_id,
            'debit': debit,
            'credit': credit,
            'invoice_id' :invoice_id,
        }

        return move_line.with_context(check_move_validity=False).create(vals)

    def update_state(self, check_line_obj):
        # TODO: needs some refactoring
        if check_line_obj.amount == check_line_obj.amount_posted:
            check_line_obj.write({'state': 'paid'})
        '''flag = True
		for line in check_line_obj.check_lines:
			if not line.move_ids:
				flag = False
		if flag:
			check_line_obj.write({'state': 'paid'})
			if 1 == 1:
				# TODO it came from voucher 'voucher must closed '
				print('on voucher ')
			elif check_line_obj.invoice_id:
				check_line_obj.invoice_id.write({'state': 'paid'})
		'''
    @api.onchange('currency_id')
    def _onchange_currency(self):
        self.amount = abs(self._compute_payment_amount())
        # Set by default the first liquidity journal having this currency if exists.
        journal = self.env['account.journal'].search(
            [('type', 'in', ('bank', 'cash')), ('currency_id', '=', self.currency_id.id)], limit=1)
        if journal:
            return {'value': {'journal_id': journal.id}}

    @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        '''
        Compute the total amount for the payment wizard.
        '''
        # Get the payment currency
        if not currency:
            payment_currency = self.currency_id
        if payment_currency == self.line_id.currency_id:
            return self.line_id.amount - self.line_id.paid_amount
        else:
            return self.line_id.line_id.currency_id._convert(self.amount, payment_currency, self.env.user.company_id, self.line_id.due_date or fields.Date.today())

    @api.model
    def _compute_amount_fields(self, amount, payment_currency, customer_check_currency):
        """ Helper function to compute value for fields debit/credit/amount_currency based on an amount and the currencies given in parameter"""
        amount_currency = False
        currency_id = False
        date = self.env.context.get('date') or fields.Date.today()
        company = self.env.context.get('company_id')
        company = self.env['res.company'].browse(
            company) if company else self.env.user.company_id
        if payment_currency != customer_check_currency:
            amount_currency = amount
            amount = payment_currency._convert(
                amount, customer_check_currency, company, date)
            currency_id = payment_currency.id

        return amount, amount_currency, currency_id

    def Post_check(self):
        amount_currency = False
        move_obj = self.env['account.move']
        if self.line_id.check_line_id:
            raise UserError(
                _('This Check has parent group please check it first.'))
        if self.line_id.related_lines:
            # lunching mearg customers feature
            raise UserError(
                _('Please contact System administrator.'))

            for line in self.line_id.related_lines:
                partner_id = line.line_id.partner_id.id
                invoice_id = line.line_id.reservation_id.invoice_id.id
                ref = self.line_id.check_number
                journal_id = self.journal_id.id
                move_id = self.create_move(ref, journal_id)
                if line.description:
                    name = line.description
                else:
                    name = '/'
                account_id = self.journal_id.default_debit_account_id.id
                
                if self.currency_id != self.company_id.currency_id :
                    amount_currency = line.amount
                    debit =  self.currency_id._convert(line.amount, self.company_id.currency_id, self.env.user.company_id,fields.Date.today())
                    credit = 0.0
                else:
                    debit = line.amount
                    credit = 0.0

                self.create_move_line(
                    partner_id, name, move_id.id, account_id, debit, credit , invoice_id)

                account_id = self.partner_id.property_account_receivable_id.id
                
                if self.currency_id != self.company_id.currency_id :
                    amount_currency = line.amount
                    debit =  0.0 
                    credit = self.currency_id._convert(line.amount, self.company_id.currency_id, self.env.user.company_id,fields.Date.today())
                else:
                    debit = 0.0
                    credit = line.amount
                self.create_move_line(
                    partner_id, name, move_id.id, account_id, debit, credit ,invoice_id)
                line.write({
                    'move_id': move_id.id,
                    'check_status': 'paid',
                    'move_check': 'true'
                })

                account_move = move_obj
                account_move.write({
                    'state': 'posted',
                })
            check_line_obj = self.line_id.line_id
            self.line_id.write({
                'move_id': move_id.id,
                'check_status': 'paid'
            })
            self.update_state(check_line_obj)

        else:
            amount, amount_currency, currency_id = self._compute_amount_fields(
                self.amount, self.currency_id, self.line_id.currency_id)

            invoice_id = self.line_id.reservation_id.invoice_id.id

            if self.currency_id and self.company_id.currency_id and self.currency_id != self.company_id.currency_id:
                if int(amount) > (int(self.line_id.amount - self.line_id.paid_amount)):
                    raise UserError(
                        _('It seems that amount you want to pay is more than check amount ,, can you please post current check and register partial payment on next check *_^'))
            # TODO: below move must review
            ref = self.line_id.check_number
            journal_id = self.journal_id.id
            move_id = self.create_move(ref, journal_id)

            if self.currency_id != self.company_id.currency_id :
                amount_currency = self.amount
                debit =  self.currency_id._convert(self.amount, self.company_id.currency_id, self.env.user.company_id,fields.Date.today())
                credit = 0.0
            else:
                debit = self.amount
                credit = 0.0

            self.create_move_line(
                self.partner_id.id, self.description, move_id.id, self.journal_id.default_debit_account_id.id, debit, credit,invoice_id)
            
            if self.currency_id != self.company_id.currency_id :
                amount_currency = self.amount
                debit =  0.0 
                credit = self.currency_id._convert(self.amount, self.company_id.currency_id, self.env.user.company_id,fields.Date.today())
            else:
                debit = 0.0
                credit = self.amount

            self.create_move_line(
                self.partner_id.id, self.description, move_id.id, self.partner_id.property_account_receivable_id.id, debit, credit,invoice_id)
            if self.currency_id == self.company_id.currency_id :
                paid_value = self.line_id.paid_amount + self.amount
                paid_amount = self.currency_id._convert(paid_value, self.line_id.line_id.currency_id, self.env.user.company_id,fields.Date.today())
            else:
                paid_amount = self.line_id.paid_amount + self.amount

            # here we will compute differance
            self.line_id.write({
                'move_id': move_id.id,
                'paid_amount': paid_amount,
                'check_status': 'paid' if int(paid_amount) == int(self.line_id.amount) else 'schedule',
                'move_check': True if int(paid_amount) == int(self.line_id.amount) else False
            })

            self.update_state(self.line_id.line_id)
            account_move = move_obj
            move_id.write({
                'state': 'posted',
                'check_line_id': self.line_id.id,
            })
