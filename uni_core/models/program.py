from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.addons.uni_core.utils import get_default_faculty


class Program(models.Model):
    _name = 'uni.faculty.department.program'
    _description = 'Program'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)

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
        required=True
    )

    program_line_ids = fields.One2many(
        string="Program Details",
        inverse_name="program_id",
        comodel_name="uni.faculty.department.program.line",
    )

    @api.one
    def generate(self):
        self.program_line_ids.unlink()

        self.env.cr.execute(
            '''
			INSERT INTO uni_faculty_department_program_line (
				program_id,
				level_id,
				semester_id,
				specialization_id,
				subject_id,
				credit_hours
			)
			SELECT  prog.id ,
					line.level_id,
					line.semester_id,
					line.specialization_id,
					line.subject_id,
					line.credit_hours
			FROM uni_faculty_subject_line AS line

			LEFT JOIN uni_faculty_department_program AS prog
			ON prog.id = %s

			WHERE line.specialization_id IN (
				SELECT id
				FROM uni_faculty_department_specialization
				WHERE department_id = %s
			)
			''',
            (self.id, self.department_id.id)
        )


class ProgramLine(models.Model):
    _name = 'uni.faculty.department.program.line'
    _description = 'Program Details'
    _rec_name = 'program_id'

    program_id = fields.Many2one(
        string="Program",
        comodel_name='uni.faculty.department.program',
    )

    # To use later in domains
    faculty_id = fields.Many2one(
        comodel_name='res.company',
        related='program_id.faculty_id',
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
        domain="[('faculty_id', '=', faculty_id)]",
        required=True
    )

    credit_hours = fields.Float(string='Credit hours', required=True)

    @api.multi
    @api.constrains('credit_hours')
    def _check_credit_hours(self):
        for r in self:
            if r.credit_hours <= 0:
                raise ValidationError(
                    _('Credit hours must be greater than zero')
                )
