from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _


class Department(models.Model):
    _name = 'uni.faculty.department'
    _description = 'Department'

    name = fields.Char(string='Name', required=True, translate=True)

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        domain="[('type', '=', 'faculty')]",
        string='Faculty',
        default=lambda self: get_default_faculty(self),
        required=True
    )

    specialization_ids = fields.One2many(
        comodel_name='uni.faculty.department.specialization',
        inverse_name='department_id',
        string='Specializations',
        readonly=True
    )

    branch_id = fields.Many2one(
        string="Branch",
        comodel_name="uni.faculty.branch",
        domain="[('faculty_id', '=', faculty_id)]"
    )

    _sql_constraints = [
        (
            'name_unique',
            'UNIQUE(faculty_id, name)',
            _('The name must be unique')
        ),
    ]
