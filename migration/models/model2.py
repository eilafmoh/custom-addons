# -*- encoding: utf-8 -*-

from odoo import api, fields, models
    
# class Migration2(models.Model):
#     _name = 'migration.migration'
#     _description = 'Migration'

#     emp_code = fields.Char()
#     relation_identity=fields.Char(string="relation identity")
#     emp_identity=fields.Char(string="EMP identity")

#     name = fields.Char()
#     relation = fields.Char()
#     birthday = fields.Date()
#     company_id = fields.Char()


# class Migration3(models.Model):
#     _name = 'res.bank.migration'
#     _description = 'Migration'

#     name = fields.Char()


class Migration4(models.Model):
    _name = 'bank.migration'
    _description = 'Migration'

    name = fields.Char()
    account_bank = fields.Char()
    ipan = fields.Char()
    # currency = fields.Char()
    # company_id = fields.Char()

class Migration0(models.Model):
    _name = 'contype.migration'
    _description = 'Migration'

    name = fields.Char()
    _type = fields.Char()
    # date = fields.Date()


# class Migration5(models.Model):
#     _name = 'insurance.migration'
#     _description = 'Migration'

#     doc_num = fields.Char()
#     categ_code = fields.Char()
#     price = fields.Char()
#     emp_insur = fields.Char()


# class Migration6(models.Model):
#     _name = 'employee.insurance.migration'
#     _description = 'Migration'

#     emp_code = fields.Char()
#     doc_num = fields.Char()
#     categ_code = fields.Char()
#     price = fields.Char()
#     emp_insur = fields.Char()
