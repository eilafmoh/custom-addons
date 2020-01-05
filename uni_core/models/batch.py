from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _


class Batch(models.Model):
    _name = 'uni.faculty.department.batch'
    _description = 'Batch'
    _rec_name = 'code'

    name = fields.Char(string="Name", translate=True, required=True)
    code = fields.Char(string="Code", required=True)

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
        domain="[('faculty_id', '=', faculty_id)]",
        #required=True
    )

    program_id = fields.Many2one(
        string="Program",
        comodel_name="uni.faculty.department.program",
        domain="[('department_id', '=', department_id)]",
        #required=True
    )

    _sql_constraints = [
        (
            'code_unique',
            'UNIQUE(department_id, code)',
            _('The code must be unique')
        )
    ]
