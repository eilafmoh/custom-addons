from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _


class Specialization(models.Model):
    _name = 'uni.faculty.department.specialization'
    _description = 'Specialization'

    name = fields.Char(string='Name', required=True, translate=True)

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        string='Faculty',
        domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        required=True
    )

    department_id = fields.Many2one(
        'uni.faculty.department',
        string='Department',
        required=True, domain="[ ('faculty_id', '=', faculty_id)]"
    )

    parent_id = fields.Many2one(
        'uni.faculty.department.specialization',
        string='Parent Specialization'
    )

    parent_left = fields.Integer(string='Parent Left', invisible=True)
    parent_right = fields.Integer(string='Parent Right', invisible=True)

    _sql_constraints = [
        (
            'name_unique',
            'UNIQUE(department_id, name)',
            _('The name must be unique')
        ),
    ]
