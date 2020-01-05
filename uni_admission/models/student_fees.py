# -*- encoding: utf-8 -*-
from odoo import api, fields, models


class student_fees(models.Model):
    _name = 'student.fees'
    _description = 'Student Fees'
    _rec_name = "student_id"

    @api.one
    @api.depends('registration_fees', 'study_fees','other_fees','other_discount' , 'total_discount',)
    def _compute_amount(self):
        discount_amount = 0.0
        fees_amount =0.0
        residual_fees = self.study_fees - self.total_discount
        for rec in self.other_discount:
            discount_perc = 0.0

            discount_perc = rec.general_discount
            discount_amount += ( residual_fees * discount_perc ) / 100

            residual_fees -= discount_amount

        for fees in self.other_fees:
            fees_amount += fees.amount

        self.sub_total = fees_amount + self.registration_fees + self.study_fees  - self.total_discount

    @api.one
    @api.depends('other_discount','discount')
    def _compute_discount(self):
        discount_amount = 0.0

        total_fees = self.study_fees - self.discount
        for rec in self.other_discount:

            discount_amount += (total_fees * rec.general_discount ) / 100

        self.total_discount = self.discount + discount_amount
     

    @api.one
    @api.depends('sub_total', 'paid_amount')
    def _compute_res_amount(self):
        self.residual_amount = self.sub_total - self.paid_amount

    def amount_calc(self):
        return self.sub_total - self.paid_amount 

    student_id = fields.Many2one(
        'uni.student',
        string="Student",
        readonly=True
    )

    faculty_id = fields.Many2one(
        'res.company',
        related='student_id.faculty_id',
        string='Faculty',
        store=True
    )

    department_id = fields.Many2one(
        'uni.faculty.department',
        related='student_id.department_id',
        store=True,
        string='Department'
    )

    specialization_id = fields.Many2one(
        'uni.faculty.department.specialization',
        related='student_id.specialization_id',
        string='Specialization',
        store=True,
        domain="[('department_id','=',department_id)]"
    )

    level_id = fields.Many2one(
        'uni.faculty.level',
        string='Level',
        readonly=True
    )

    semester_id = fields.Many2one(
        'uni.faculty.semester',
        string='Semester',
        readonly=True
    )

    registration_fees = fields.Float(string="Registration Fees")
    
    study_fees = fields.Float(string="Tuition Fees", readonly=True)

    discount = fields.Float(
        string="Admission Discount",
        readonly=True ,
        )

    total_discount = fields.Float(
        string="Total Discount",
        readonly=True ,
        store=True,
        compute='_compute_discount'
        )
    
    discount_desc = fields.Text(string="Discount Note", readonly=True)
    
    sub_total = fields.Float(
        string="Sub Total",
        store=True,
        readonly=True,
        compute='_compute_amount'
    )

    other_discount = fields.Many2many('uni.student_category' , string="Other discounts")
    
    other_fees = fields.Many2many('uni.add_fees' , string='Other Fees', readonly=False)

    paid_amount = fields.Float(string="Paid Amount", store=True, readonly=True)
    
    residual_amount = fields.Float(string="Residual Amount", store=True, readonly=True)
    
    move_ids = fields.One2many(
        string="Journal Enteries",
        comodel_name="account.move",
        inverse_name="fees_move_line",
        store=True,
        readonly=True,
    )
    paid = fields.Boolean(string="Paid ?", readonly=True)

    payment_date = fields.Date(string="Payment Date", readonly=True)
    
    invoice_id = fields.Many2one('account.invoice',string="Invoice", readonly=True)

    state = fields.Selection([('draft','Draft'),('open','Open'),('paid','Paid')],default='draft')

    def get_student_fees(self):
        dept_fees = self.env['uni.study_fees.departments'].search([
            ('department_id', '=', self.student_id.department_id.id),
            ('certificate_type_id', '=',
             self.student_id.certificate_type_id.id),
            ('year_id', '=', self.student_id.year_id.id),
            ('state', '=', 'done')
        ], limit=1)

        if not dept_fees:
            # No dept fees? let's try the global faculty fees
            faculty_fees = self.env['uni.study_fees.line'].search([
                ('faculty_id', '=', self.student_id.faculty_id.id),
                ('certificate_type_id', '=',
                 self.student_id.certificate_type_id.id),
                ('year_id', '=', self.student_id.year_id.id), ('state', '=', 'done')
            ], limit=1)

        return dept_fees or faculty_fees


class account_move(models.Model):
    _inherit = 'account.move'

    fees_move_line = fields.Many2one(
        string="Fees Line",
        comodel_name="student.fees",
        readonly=True,
    )