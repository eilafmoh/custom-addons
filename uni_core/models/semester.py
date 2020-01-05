from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _


class Semester(models.Model):
    _name = 'uni.faculty.semester'
    _description = 'Semester'
    _rec_name = 'order'

    name = fields.Char(string='Name', required=True, translate=True)
    # TODO : add order to specific group (acdmic adminstration), selection
    order = fields.Selection(string='Order', selection=[
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
        (9, "9"),
        (10, "10"),
        (11, "11"),
        (12, "12"),
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
