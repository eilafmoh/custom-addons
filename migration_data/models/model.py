from datetime import datetime
from odoo import api, fields, models, tools


class receivable(models.Model):
    _name = 'uni.migration'

    std_reg_no = fields.Char(string="University No")
    std_course_id = fields.Char(string="Faculty")
    debit = fields.Char( string="debit")
    credit = fields.Char( string="credit")
    balance = fields.Char(string="Balance")
    currency_id = fields.Char('Currency')



class receivable(models.Model):
    _name = 'uni.notfound'

    std_reg_no = fields.Char(string="University No")
    std_course_id = fields.Char(string="Faculty")
    debit = fields.Char( string="debit")
    credit = fields.Char( string="credit")
    balance = fields.Char(string="Balance")
    currency_id = fields.Char('Currency')


class notpayable(models.Model):
    _name = 'uni.notfound.payable'

    partner_name = fields.Char('Name')
    partner_id = fields.Integer('Partner id')
    std_reg_no = fields.Char(string="University No")
    std_course_id = fields.Char(string="Faculty")
    debit = fields.Char( string="debit")
    credit = fields.Char( string="credit")
    balance = fields.Char(string="Balance")
    discription = fields.Char('Discreption')
    currency_id = fields.Char('Currency')
    account_id = fields.Char('Account')



class payable(models.Model):
    _name = 'uni.migration.payable'

    partner_name = fields.Char('Name')
    partner_id = fields.Integer('Partner id')
    std_reg_no = fields.Char(string="University No")
    std_course_id = fields.Char(string="Faculty")
    debit = fields.Char( string="debit")
    credit = fields.Char( string="credit")
    balance = fields.Char(string="Balance")
    discription = fields.Char('Discreption')
    currency_id = fields.Char('Currency')
    account_id = fields.Char('Account')
