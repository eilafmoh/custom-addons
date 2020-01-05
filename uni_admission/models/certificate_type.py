# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import _


class CertificateType(models.Model):
    _name = 'uni.certificate.type'
    _description = 'Certificate Type'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True)

    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True
    )

    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        (
            'name_unique',
            'UNIQUE(name)',
            _('The name must be unique')
        ),
    ]
