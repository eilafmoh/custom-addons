# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class TuitionFees(models.Model):
    _name = 'uni.study_fees'
    _description = 'Tuition fees'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        required=True,
    )

    certificate_type_id = fields.Many2one(
        comodel_name='uni.certificate.type',
        string='Certificate Type',
        required=True,
    )

    fees_line_ids = fields.One2many(
        comodel_name="uni.study_fees.line",
        inverse_name="fees_id",
    )

    department_line_ids = fields.One2many(
        comodel_name="uni.study_fees.departments",
        inverse_name="fees_id",
    )

    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related='certificate_type_id.currency_id',
        readonly=True,
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('approve', 'Waiting for approval'),
            ('done', 'Approved'),
        ],
        default="draft"
    )

    def approve(self):
        if not self.fees_line_ids and not self.department_line_ids:
            raise Warning(
                _('Please add faculty and/or department fees!')
            )
        self.write({'state': 'approve'})

    def done(self):
        self.write({'state': 'done'})

    def rest_draft(self):
        self.write({'state': 'draft'})


class TuitionFeesLine(models.Model):
    _name = 'uni.study_fees.line'
    _description = 'Faculty Fees'

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        domain="[('type', '=', 'faculty')]",
        string='Faculty',
        required=True
    )

    fees_id = fields.Many2one(
        string="Tuition fees",
        comodel_name="uni.study_fees",
    )

    certificate_type_id = fields.Many2one(
        comodel_name='uni.certificate.type',
        string='Certificate Type',
        related='fees_id.certificate_type_id',
    )

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        related='fees_id.year_id',
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('approve', 'Waiting for approval'),
            ('done', 'Approved'),
        ],
        default="draft",
        related='fees_id.state',
    )

    registration_fees = fields.Float(string="Registration Fees", required=True)
    study_fees = fields.Float(string="Tuition Fees", required=True)
   

class TuitionFeesDepartment(models.Model):
    _name = 'uni.study_fees.departments'
    _description = 'Department Fees'

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        domain="[('type', '=', 'faculty')]",
        string='Faculty',
        required=True
    )

    department_id = fields.Many2one(
        comodel_name='uni.faculty.department',
        domain="[('faculty_id', '=', faculty_id)]",
        string="Department",
        required=True,
    )

    fees_id = fields.Many2one(
        string="Tuition fees",
        comodel_name="uni.study_fees",
    )

    certificate_type_id = fields.Many2one(
        comodel_name='uni.certificate.type',
        string='Certificate Type',
        related='fees_id.certificate_type_id',
    )
  
    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        related='fees_id.year_id',
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('approve', 'Waiting for approval'),
            ('done', 'Approved'),
        ],
        default="draft",
        related='fees_id.state',
    )

    registration_fees = fields.Float(string="Registration Fees", required=True)
    study_fees = fields.Float(string="Tuition Fees", required=True)

class additionalFees(models.Model):
    _name = 'uni.add_fees'

    name = fields.Char(
        string='Name',
        required=True
    )

    amount = fields.Float(
        string="Amount",
        required=True,
    )

    account_id = fields.Many2one('account.account')

    @api.multi
    @api.depends('name', 'amount ')
    def name_get(self):

        result = []
        for X in self:
            name = ( X.name + '-' or "") + str(X.amount)

            result.append((X.id, name)) 
            
        return result