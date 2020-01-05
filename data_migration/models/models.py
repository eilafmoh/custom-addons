# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class emaar_migration(models.Model):
    _name = 'emaar.migration'

    complex_id = fields.Char(string="Complex", )
    land_id = fields.Integer(string="land", )
    area = fields.Float(string="Area", )

    customer_name = fields.Char(string="Customer Name", )
    phone = fields.Char(string="Phone", )
    sale_date = fields.Date(string="Sale Date", )
    sale_type = fields.Char(string="Sale Type", )
    purchase_type = fields.Date(string="Purchase Type", )
    sale_amount = fields.Float(string="Sale Amount", )
    advance = fields.Float(string="Advane", )
    total_installment = fields.Float(string="Total installment", )
    installment_num = fields.Integer(string="Installment", )
    install_amount = fields.Float(string="Installment Amount", )
    first_installment_date = fields.Date(string="First installment date", )
    last_installment_date = fields.Date(string="Last installment date", )
    collection_date = fields.Selection(
        string="Collection Date",
        selection=[
            (5, '5'),
            (10, '10'),
            (15, '15'),
            (20, '20'),
            (25, '25'),
            (30, '30'),
        ], default=5,
    )
    sale_person = fields.Char(string="Sale Person", )
    paid_amount = fields.Float(string="Paid Amount", )
    residual_amount = fields.Float(string="Residual Amount", )

class check_migration(models.Model):
    _name = 'check.migration'

    customer_id = fields.Integer('customer id')
    date = fields.Date(string="check date", )
    amount = fields.Float(string="Amount", )
    deliverd = fields.Float(string="Delvired Amount", )
    residual_amount = fields.Float(string="Residual Amount", )
    check_number = fields.Float(string="Check Number", )
    bank = fields.Char(string="Bank", )
    vendor = fields.Char('Vendor')
    amount_usd = fields.Float(string="Amount($)", )