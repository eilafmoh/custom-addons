# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty


class Migration(models.Model):
    _name = 'student.migration'
    _description = 'Student Migration'
    _rec_name = 'university_id'

    university_id = fields.Char(string="University ID", required=True)
    first_name = fields.Char(string="First Name", required=True)
    middle_name = fields.Char(string="Middle Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    fourth_name = fields.Char(string="Fourth Name", required=True)

    secondary_school = fields.Char(string="Secondary School", required=True)

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        domain="[('type', '=', 'faculty')]",
        string='Faculty',
        default=lambda self: get_default_faculty(self),
        required=True
    )

    department_id = fields.Many2one(
        comodel_name='uni.faculty.department',
        domain="[('faculty_id', '=', faculty_id)]",
        string="Department",
    )
