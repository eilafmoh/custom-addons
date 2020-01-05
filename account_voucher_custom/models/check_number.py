from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, AccessError


class check_number(models.Model):
    _name = 'check.number'
    _description = "check Number"

    check_number = fields.Integer(string='First Check Number', required=True)
    amount_per_month = fields.Float(string="Amount per Month")
    start_date = fields.Date(string='Date')
    date = fields.Date(string='Date')
    num_of_monthes = fields.Integer(string="Number Of Monthes")
    investment = fields.Integer("Investment")
    customer_check_id = fields.Many2one('customer.check')
    onc_check_id = fields.Many2one('oncreadit.check')
    customer_bank_account = fields.Char('Customer Bank Account')
    rack = fields.Integer('Rack Number')
    journal_id = fields.Many2one('account.journal', 'Journal')
    type = fields.Selection([
        ('in', 'in'),
        ('out', 'out'),
    ], 'Type')

    def Post_check(self):
        if self.type == 'in':

            line = self.env['customer.check.line']
            check_line = line.search([('line_id' ,'=' , self.customer_check_id.id)])
            for check in check_line:
                print ('---------- in for ********')
                check.unlink()
            check_number = int(self.check_number)
            start_date = datetime.strptime(str(self.date), '%Y-%m-%d')
            for month in range(0, self.investment):
                line.create({
                    'line_id': self.customer_check_id.id,
                    'check_number': check_number,
                    'date': self.date,
                    'due_date': start_date,
                    'amount': self.amount_per_month,
                    'rack': int(self.rack),
                    'account_id': self.customer_bank_account
                })
                start_date = start_date + \
                    relativedelta(months=self.num_of_monthes)
                check_number += 1
        elif self.type == 'out':
            line = self.env['oncreadit.check.line']
            check_number = int(self.check_number)
            start_date = datetime.strptime(str(self.start_date), '%Y-%m-%d')
            for month in range(0, self.investment):
                line.create({
                    'line_id': self.onc_check_id.id,
                    'check_number': check_number,
                    'date': self.date,
                    'due_date': start_date,
                    'amount': self.amount_per_month,
                    'journal_id': self.journal_id.id,
                })
                start_date = start_date + \
                    relativedelta(months=self.num_of_monthes)
                check_number += 1
        return True
