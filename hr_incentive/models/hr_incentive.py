# -*- coding: utf-8 -*-
##############################################################################
#
#    ZOO, zoo-business Solution
#    Copyright (C) 2017-2020 zoo (<http://www.zoo-business.com>).
#
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import Warning
import odoo.addons.decimal_precision as dp


class HRIncentive_type(models.Model):
    _name = 'hr.incentive.type'

    name = fields.Char('Name', required=True)
    payment_method = fields.Selection(selection=[
        ('payroll', 'Through Payroll'),
        ('cash', 'Direct Cash/Cheque')], string='payment Method', select=True, default='cash')
    rule_id = fields.Many2one('hr.salary.rule', string='Rule salary ')
    account_id = fields.Many2one('account.account', string="Account")
    debt_account_id = fields.Many2one('account.account', string="Debit Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    credit_account_id = fields.Many2one('account.account', string="Credit Account")
    no_month = fields.Integer(string="No Of Month", default=1)


class HRIncentive(models.Model):
    _name = 'hr.incentive'
    _description = 'HR Incentive'
    _order = "date desc, id desc"

    name = fields.Char(string='Number', readonly=True)
    request_id = fields.Many2one(
        'res.users', string='Requestor', default=lambda self: self.env.user)
    date = fields.Date(default=lambda self: fields.Date.context_today(self), readonly=True,
                       states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    manager_id = fields.Many2one('hr.employee', string='Manager')
    types = fields.Selection([
        ('all_staff', 'All Staff'),
        ('employee', 'certain Employee'),
        ('selected', 'Selected Employees'), ], string='Types', default='all_staff', readonly=True,
        states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True,
                                  states={'draft': [('readonly', False)]},domain=[('state', '=', 'in_service')])
    employee_ids = fields.Many2many('hr.employee', string='Employees', readonly=True,
                                    states={'draft': [('readonly', False)]},domain=[('state', '=', 'in_service')])
    type_in = fields.Selection([
        ('percentage', 'Percentage (%)'),
        ('fix', 'Fixed Amount'),
        ('manual', 'Manual Amount'), ], string='Incentive By', default='fix', readonly=True,
        states={'draft': [('readonly', False)]})
    amountx = fields.Float(string="Amount", readonly=True,
                           states={'draft': [('readonly', False)]})
    percentage = fields.Float(string=" Percentage (%)")

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,  states={'draft': [(
        'readonly', False)], 'submit': [('readonly', False)]}, default=lambda self: self.env.user.company_id.id)
    payment_method_id = fields.Many2one(
        'hr.incentive.type', string='Payment Method', ondelete='cascade', required=True)

    state = fields.Selection([
        ('draft', 'Open'),
        ('submit', 'Submit'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
        ('reject', 'Reject'),
    ], string='State', readonly=True, default='draft')
    incentive_line = fields.One2many('hr.incentive.line', 'incentive_id', readonly=True,
                                     states={'draft': [('readonly', False)], 'submit': [('readonly', False)]})
    reason = fields.Text(readonly=True,
                         states={'draft': [('readonly', False)]})
    voucher_id = fields.Many2one('account.voucher', 'Voucher', readonly=True)
    active = fields.Boolean('active', default=True)

    @api.multi
    def action_draft(self):
        self.state = 'draft'
    
    @api.multi
    def action_submit(self):
        if self.incentive_line:
            if self.amountx > self.company_id.incentive_double_validation_amount:
                self.state = 'submit'
            else:
                self.state = 'approved'
        else:
            raise Warning(
                    _('Plese compute the incentive line by press compute method'))


    @api.multi
    def action_approve(self):
        if self.payment_method_id.payment_method == 'cash':
            self.bt_money_received()
        self.state = 'approved'

    @api.multi
    def compute_incentive_line(self):
        incentive_line = self.env['hr.incentive.line']
        incentive_line.search([('incentive_id', '=', self.id)]).unlink()
        if self.types == 'all_staff':
            employees = self.env['hr.employee'].search([('active', '=', True),('state', '=', 'in_service')])
        elif self.types == 'employee':
            employees = self.employee_id
        elif self.types == 'selected':
            employees = self.employee_ids
        percentage = self.percentage
        amountx = self.amountx
        for re in employees:
            percentage = self.percentage
            fix = self.amountx
            if self.type_in == 'percentage':
                amount = re.contract_id.net_salary * (percentage/100)
                amountx = 0
            elif self.type_in == 'fix':
                amount = amountx
                percentage = 0
            else:
                amountx = 0
                amount = 0
                percentage = 0

            line_id = incentive_line.create({
                'incentive_id': self.id,
                'wage': re.contract_id.wage,
                'type_in': self.type_in,
                'amountx': amountx,
                'percentage': percentage,
                'payment_method_id': self.payment_method_id.id,
                'amount': amount,
                'date': self.date,
                'incentive_state': self.state,
                'reason': self.reason,
                'employee_id': re.id,
            })

        return True

    #     return True
    @api.multi
    def bt_money_received(self):
        account_id = self.env['account.account'].search(
            [('internal_type', '=', 'liquidity')])
        if not account_id:
            raise Warning(_('please define account with typ liquidity.'))
        vals = {
            'date': self.date,
            'pay_now': 'pay_now',
            'journal_id': self.company_id.hr_journal_id.id,
            'voucher_type': 'purchase',
            'account_id': account_id[0].id
        }
        voucher_id = self.env['account.voucher'].create(vals)
        total = 0.0
        for x in self.incentive_line:
            total += x.amount
        name = self.name or " "

        vals = {
            'name': name,
            'account_id': self.payment_method_id.account_id.id,
            'price_unit': total,
            'voucher_id': voucher_id.id,
        }
        self.env['account.voucher.line'].create(vals)
        self.voucher_id = voucher_id.id
        # self.state = "money_received"

    @api.multi
    def action_reject(self):
        self.state = 'reject'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.incentive')
        return super(HRIncentive, self).create(vals)

    @api.multi
    def unlink(self):
        for incentive in self:
            if incentive.state not in ('draft', 'cancel'):
                raise Warning(
                    _('You can not delete an incentive which is not draft or cancelled.'))
        return super(HRIncentive, self).unlink()


class HRIncentiveLine(models.Model):
    _name = 'hr.incentive.line'
    _rec_name = 'employee_id'
    _order = 'date desc, department_id, amount desc'

    incentive_id = fields.Many2one(
        'hr.incentive', string='incentive', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee', required=True, domain=[('state', '=', 'in_service')])
    jab_id = fields.Many2one('hr.job', string='Job Title',
                             compute='_get_employee', store=True, readonly=True)
    department_id = fields.Many2one(
        'hr.department', string=' Department', compute='_get_employee', store=True, readonly=True)
    wage = fields.Float(string="Employee Salary",
                        readonly=True)
    type_in = fields.Selection(
        related='incentive_id.type_in', string='Incentive By', default='fix')
    amountx = fields.Float(string="Amount")
    percentage = fields.Float(string=" Percentage (%)")
    payment_method_id = fields.Many2one(
        'hr.incentive.type', string='Payment Method', ondelete='cascade')

    amount = fields.Float(digits=dp.get_precision(
        'Payroll'), string='Amount incentive', required=True)
    date = fields.Date(related='incentive_id.date', store=True)
    incentive_state = fields.Selection(
        related='incentive_id.state', string='Status incentive', store=True, default='draft', readonly=True)
    reason = fields.Text(related='incentive_id.reason')
    state = fields.Selection([
        ('open', 'Open'),
        ('paid', 'Paid'),
    ], string='State', readonly=True, default='open')

    @api.one
    @api.depends('employee_id')
    def _get_employee(self):
        self.jab_id = self.employee_id.job_id.id
        self.department_id = self.employee_id.department_id.id


class HRIncentiveLinepayslip(models.Model):
    _name = 'hr.incentive.line.payslip'
    _rec_name = 'employee_id'
    _order = 'date desc, department_id, amount desc'

    incentive_id = fields.Many2one(
        'hr.incentive', string='incentive', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee', required=True, domain=[('state', '=', 'in_service')])
    jab_id = fields.Many2one('hr.job', string='Job Title',
                             compute='_get_employee', store=True, readonly=True)
    department_id = fields.Many2one(
        'hr.department', string=' Department', compute='_get_employee', store=True, readonly=True)
    wage = fields.Float(string="Employee Salary",
                        readonly=True)
    type_in = fields.Selection(
        related='incentive_id.type_in', string='Incentive By', default='fix')
    amountx = fields.Float(string="Amount")
    percentage = fields.Float(string=" Percentage (%)")
    payment_method_id = fields.Many2one(
        'hr.incentive.type', string='Payment Method', ondelete='cascade')

    amount = fields.Float(digits=dp.get_precision(
        'Payroll'), string='Amount incentive', required=True)
    date = fields.Date(related='incentive_id.date', store=True)
    incentive_state = fields.Selection(
        related='incentive_id.state', string='Status incentive', store=True, default='draft', readonly=True)
    reason = fields.Text(related='incentive_id.reason')
    state = fields.Selection([
        ('open', 'Open'),
        ('paid', 'Paid'),
    ], string='State', readonly=True, default='open')
    payroll_id = fields.Many2one('hr.payslip', string="Payslip Ref.")


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def compute_sheet(self):
        super(HRPayslip, self).compute_sheet()
        hr_incentive = self.env['hr.incentive.line']
        payslip_line = self.env['hr.payslip.line']
        for payslip in self:
            incetive = hr_incentive.search(
                [('state', '=', 'open'), ('employee_id', '=', payslip.employee_id.id)])
            for item in incetive:
                payslip_line.search([('code','=',item.payment_method_id.rule_id.code)]).unlink()
                payslip_line.create({
                    'name': item.payment_method_id.rule_id.name,
                    'category_id': item.payment_method_id.rule_id.category_id.id,
                    'amount': item.amount,
                    'salary_rule_id': item.payment_method_id.rule_id.id,
                    'code': item.payment_method_id.rule_id.code,
                    'rate': 100,
                    'slip_id': payslip.id,
                })
        return True


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def compute_total_incentive(self):
        total = 0.00
        for line in self.inc_ids:
            if line.state == 'open':
                total += line.amount
        self.total_amount_inc = total

    inc_ids = fields.One2many(
        'hr.incentive.line.payslip', 'payroll_id', string="Inc")
    total_amount_inc = fields.Float(
        string="Total inc Amount", compute='compute_total_incentive')

    @api.multi
    def get_inc(self):
       
        payslip_line = self.env['hr.incentive.line.payslip']
        payslip_line.search([('payroll_id', '=', self.id)]).unlink()
        inc_ids = self.env['hr.incentive.line'].search(
            [('employee_id', '=', self.employee_id.id)])
        for loan in inc_ids:
            vals = {
                'incentive_id': loan.incentive_id.id,
                'amount': loan.amount,
                'employee_id': loan.employee_id.id,
                'payroll_id': self.id,
                'date': loan.date
            }
            payslip_line.create(vals)

        #self.inc_ids = array
        return True

    @api.model
    def hr_verify_sheet(self):
        self.get_inc()
        self.get_loan()
        self.compute_sheet()
        array = []
        for line in self.inc_ids:
            if line.paid:
                array.append(line.id)
                line.action_paid_amount()
            else:
                line.payroll_id = False
        self.inc_ids = array
        return self.write({'state': 'verify'})
