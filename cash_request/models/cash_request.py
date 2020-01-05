from odoo import api, fields, models, _
from . import amount_to_text as amount_to_text_ar
from odoo.exceptions import UserError, ValidationError


class cash_order(models.Model):
    _name = "cash.order"
    _inherit = ['mail.thread']

    def action_confirm(self):
        return self.write({
            'state': 'confirm',
            'name': 'CO/0'+str(self.id),
        })

    def action_refuse_confirm(self):
        self.state = 'draft'

    def action_department(self):
        self.state = 'department' if self.amount > 5000 else 'general'

    def action_refuse_department(self):
        self.state = 'confirm'

    def action_general(self):
        self.state = 'general'

    def action_refuse_general(self):
        self.state = 'confirm'

    def action_auditor(self):
        for order in self :
            scheduled_amount = sum(line.amount for line in order.payment_schedule_ids)
            if scheduled_amount != order.amount:
                raise UserError(
                    _('Please make suer that schedule amount is equal to total amount  ^_^'))
            order.state = 'auditor'

    def action_finance(self):
        self.state = 'financial'

    def action_refuse_finance(self):
        scheduled_amount = sum(line.amount for line in self.payment_schedule_ids)
        if scheduled_amount != self.amount:
            raise UserError(
                _('Please make suer that schedule amount is equal to total amount  ^_^'))
        else:
            self.state = 'general'

    @api.depends('amount')
    def compute_amount(self):
        self.amount_in_word = amount_to_text_ar.amount_to_text(
            self.amount, 'ar')
    
    def create_move(self, ref, journal_id):
        move = self.env['account.move']
        vals = {
            'ref': ref,
            'journal_id': journal_id,
        }
        return move.create(vals)

    def create_move_line(self, partner_id, name, move_id, account_id, debit, credit,analytic_account_id):
        move_line = self.env['account.move.line']
        vals = {
            'partner_id': partner_id,
            'name': name,
            'move_id': move_id,
            'account_id': account_id,
            'debit': debit,
            'credit': credit,
            'analytic_account_id':analytic_account_id.id
        }
        return move_line.with_context(check_move_validity=False).create(vals)

    def action_pay(self):
        total = sum(line.amount for line in self.payment_schedule_ids)
        if int(self.amount) != int(total):
            raise UserError(
                _('invalid amount \n pleas check that the amount is equals to liens amount  ^_^'+str(self.amount)+'  '+str(total)))
        if self.payment_type == 'now':
            for item in self.payment_schedule_ids:
                move_id = self.create_move(str(self.name+' / '+ item.check_number if item.check_number else '') , item.journal_id.id)
                credit_line = self.create_move_line(self.partner_id.id, self.name, move_id.id, item.journal_id.default_credit_account_id.id, 0.0, item.amount,item.analytic_account_id )
                self.create_move_line(self.partner_id.id, item.description, move_id.id, item.account_id.id, item.amount, 0.0,item.analytic_account_id)
                move_id.action_post()
                item.move_id = move_id.id
        elif self.payment_type == 'onc_check':
            #TODO: 7 is purchase journal id and must came from configuration
            move_id = self.create_move(str(self.name) , 7)
            #TODO: 232 is supplier and purchses in payble must be read from configuration 
            credit_line = self.create_move_line(self.partner_id.id, self.name, move_id.id, 232, 0.0, self.amount)
            for item in self.payment_schedule_ids:
                self.create_move_line(self.partner_id.id, item.description, move_id.id, item.account_id.id, item.amount, 0.0)
            move_id.action_post()
            self.move_related = move_id.id
            onc_check_id = self.env['oncreadit.check'].create({
                'date':fields.Date.today(),
                'reference':self.name,
                'partner_id':self.partner_id.id,
                'amount':self.amount,
            })
            # self.on_credit_check_id = onc_check_id.id

            for item in self.payment_schedule_ids:
                self.env['oncreadit.check.line'].create({
                    'date':fields.Date.today(),
                    'due_date':item.date,
                    'amount':item.amount,
                    'check_number':item.check_number,
                    'journal_id':item.journal_id.id,
                    'line_id':onc_check_id.id,
                })
            onc_check_id.check_description()
        self.write({'state' : 'paid' , 'move_related':move_id.id})

    company_id = fields.Many2one('res.company', 'Company',  readonly=True, states={
        'draft': [('readonly', False)]}, default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one(
        "hr.employee", string='Employee', readonly=True, )
    
    partner_id = fields.Many2one(
        "res.partner", string="Vendor", required=True)
    department_id = fields.Many2one(
        "hr.department", string="Department", readonly=True)
    amount = fields.Float('Amount by Numbers', required=True)
    amount_in_word = fields.Char(
        compute="compute_amount", store=True, string="Amount in Text", readonly=True)
    disc = fields.Text(string="Description", required=True)
    name = fields.Char(string="Sequence", default="/")
    recever_name = fields.Char(string="Recever Name",)
    date = fields.Date("Date", readonly=True, default=fields.Date.today())
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'wating for Department Manager'), ('department', 'Waiting For General Manger'),
                              ('general', 'Waiting for Finacial Manager'),
                              ('financial', 'waiting for Auditor'),
                              ('auditor', 'Wating for Payment'),
                              ('paid', 'Paid'), ('refuse', 'Refused')], "State", default="draft")
    payment_type = fields.Selection(
        string="Payment Type",
        selection=[
                ('now', 'Now'),
                ('onc_check', 'Later'),
        ],default='now',
    )
    #active = fields.Boolean("active", default=True)
    move_ids = fields.One2many(
        string="Journals",
        comodel_name="account.move",
        inverse_name="cash_order_move",
        readonly=True)

    move_related = fields.Many2one(
        string="Journal Item",
        comodel_name="account.move",
        store=True,
        readonly=True,
    )
    # on_credit_check_id = fields.Many2one(
    #     string="On Credit Check",
    #     comodel_name="oncreadit.check",
    #     readonly=True,
    # )
    # exchange_id = fields.Many2one(
    #     string="Exchange Item",
    #     comodel_name="exchange.item",
    # )
    payment_schedule_ids = fields.One2many(
        string="Payment Schedule",
        comodel_name="payment.schedule",
        inverse_name="order_id",
    )

    @api.multi
    def unlink(self):
        for order in self :
            if order.state != 'draft':
                raise UserError(_('You cannot perform this action on cash order not on state draft.'))
        return super(cash_order, self).unlink()

    @api.model
    def create(self, vals):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if not employee_id:
            raise UserError(_('Current user has no related employee'))
        vals ['user_id'] = employee_id.id,
        vals['department_id'] = employee_id.department_id.id
        result = super(cash_order, self).create(vals)
        return result

class partner_beneficiary(models.Model):
    _inherit = ['res.partner']

    beneficiary = fields.Boolean("beneficiary", default=False)


class account_move(models.Model):
    _inherit = "account.move"

    cash_order_move = fields.Many2one('cash.order')
