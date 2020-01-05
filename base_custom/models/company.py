# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    name = fields.Char(
        related='partner_id.name',
        string='Name',
        required=True,
        store=True,
        translate=True
    )

    type = fields.Selection(
        string="Type",
        selection=[
            ('faculty', 'Faculty'),
            ('institute', 'Institute'),
			('center','Center'),
            ('administration', 'Administration'),
            ('campus', 'Campus'),
        ],
        invisible=True,
        default='faculty'
    )
