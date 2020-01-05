from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.addons.uni_core.utils import get_default_faculty


class Subject(models.Model):
    _name = 'uni.faculty.subject'
    _description = 'Subject'

    name = fields.Char(string='Name', required=True, translate=True)

    code = fields.Char(string='Code')

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        string='Faculty',
        domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        required=True
    )

    subject_line_ids = fields.One2many(
        string="Subject Details",
        inverse_name="subject_id",
        comodel_name="uni.faculty.subject.line",
    )

    _sql_constraints = [
        (
            'code_unique',
            'UNIQUE(faculty_id, code)',
            _('The code must be unique')
        ),
    ]


class SubjectLine(models.Model):
    _name = 'uni.faculty.subject.line'
    _description = 'Subject Details'
    _rec_name = 'subject_id'

    # To use later in domains
    faculty_id = fields.Many2one(
        comodel_name='res.company',
        related='subject_id.faculty_id',
        string='Faculty',
    )

    level_id = fields.Many2one(
        string="Level",
        comodel_name="uni.faculty.level",
        domain="[('faculty_id', '=', faculty_id)]",
        required=True
    )

    semester_id = fields.Many2one(
        string="Semester",
        comodel_name="uni.faculty.semester",
        domain="[('faculty_id', '=', faculty_id)]",
        required=True
    )

    specialization_id = fields.Many2one(
        string="Specialization",
        comodel_name="uni.faculty.department.specialization",
        domain="[('department_id.faculty_id', '=', faculty_id)]",
        required=True
    )

    subject_id = fields.Many2one(
        string="Subject",
        comodel_name="uni.faculty.subject",
    )

    credit_hours = fields.Float(string='Credit hours')

    # _sql_constraints = [
    #     (
    #         'subject_details_unique',
    #         'UNIQUE(faculty_id, level_id, semester_id, specialization_id, subject_id)',
    #         _('The subject details must be unique')
    #     ),
    # ]

    @api.multi
    @api.constrains('credit_hours')
    def _check_credit_hours(self):
        for r in self:
            if r.credit_hours <= 0:
                raise ValidationError(
                    _('Credit hours must be greater than zero')
                )
