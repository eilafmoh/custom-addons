from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _


class Level(models.Model):
    _name = 'uni.faculty.level'
    _description = 'Years'
    _rec_name = 'order'

    name = fields.Char(string='Name', required=True, translate=True)

    order = fields.Selection(string='Order', selection=[
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
    ],
        required=True
    )

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        string='Faculty',
        required=True
    )

    # _sql_constraints = [
    #     ('name_unique',
    #      'unique(faculty_id,name)',
    #         'The name must be unique')
    # ]

    # _sql_constraints = [
    #     ('order_unique',
    #      'unique(faculty_id,order)',
    #      'The order must be unique')
    # ]
