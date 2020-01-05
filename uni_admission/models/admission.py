from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.addons.uni_core.utils import get_default_faculty
from datetime import datetime, timedelta


class Admission(models.Model):
    _name = "uni.admission"
    _inherit = ['mail.thread']
    _rec_name = "student_id"

    date = fields.Date(
        string="Date", default=fields.Date.today(), readonly=True)

    student_id = fields.Many2one(
        'uni.student',
        string="Student",
        required=True
    )
    student_name = fields.Char(string='Student' ,related='student_id.name')

    faculty_id = fields.Many2one(
        'res.company',
        related='student_id.faculty_id',
        string='Faculty',
        store=True
    )

    department_id = fields.Many2one(
        'uni.faculty.department',
        domain="[('faculty_id', '=', faculty_id)]",
        string='Department'
    )

    university_id = fields.Char(
        related='student_id.university_id',
        string='University ID',
        store=True
    )

    specialization_id = fields.Many2one(
        'uni.faculty.department.specialization',
        string='Specialization',
        domain="[('department_id.faculty_id', '=', faculty_id)]",
    )

    certificate_type_id = fields.Many2one(
        comodel_name='uni.certificate.type',
        string='Certificate Type',
        related='student_id.certificate_type_id',
        store=True,
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('form', 'application Form'),
            ('committee', 'Faculty Committee'),
            ('reg_office' , 'Registration Office'),
            ('payment', 'Payment'),
            ('reg_form', 'Registration Form'),
            ('clinic', 'Medical Examination'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ],
        default='draft',
    )

    batch_id = fields.Many2one(
        string="Batch",
        comodel_name="uni.faculty.department.batch",
        domain="[('faculty_id','=',faculty_id)]"
    )

    clinic_notes = fields.Text(string="Doctor's remarks")

    medical_condition = fields.Selection(
        string="The doctor's decision",
        selection=[
            ('fit', 'Medically fit'),
            ('unfit', 'Medically unfit'),
            ('wait', 'Waiting another operation'),
        ],
        default="fit",
    )

    committee_notes = fields.Html(string="Committee's Notes", )

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        related='student_id.year_id',
        readonly=True,
    )

    category_id = fields.Many2many(
        string="Discount Type",
        comodel_name="uni.student_category",
    )

    medical_data = fields.Many2one(
        string="Medical Data",
        comodel_name="uni.health_service.medical_data",
    )

    fees_ids = fields.One2many(
        string="Student Fees",
        comodel_name="student.fees",
        inverse_name="student_id",
        readonly=True,
        related='student_id.fees_ids',
    )

    is_installment = fields.Boolean(string="Installment")

    add_fees = fields.Many2many('uni.add_fees' , string="Additional Fees")

    sec_subject = fields.One2many(
        comodel_name='student.result',
        inverse_name='admission_id',)

    have_brother = fields.Boolean('Have Brothers in University?')

    bro_detail_ids = fields.One2many(
        comodel_name='brother.details',
        inverse_name='admission_id',)


    _sql_constraints = [
        (
            'student_id_unique',
            'UNIQUE(student_Id)',
            _('You can not have two admission requests for the same student')
        ),
    ]

    def get_first_level(self, student_id):
        domain = [('faculty_id', '=', student_id.faculty_id.id)]
        level = self.env['uni.faculty.level'].search(
            domain, limit=1, order="order asc")
        semester = self.env['uni.faculty.semester'].search(
            domain, limit=1, order="order asc")
        return level, semester

    def approve(self):
        medical_data = self.env['uni.health_service.medical_data'].create(
            {'student_id': self.student_id.id}
        )

        self.write({'state': 'form', 'medical_data': medical_data.id})

    def cancel_addmission(self):
        self.write({'state': 'cancel'})

    def clinic_approval(self):

        self.write({'state': 'done'})

    def create_move_line(self, move_id, account_id, partner_id, lable, debit, credit, date):
        self.env['account.move.line'].with_context({
            'check_move_validity': False
        }).create({
            'account_id': account_id,
            'name': lable,
            'debit': debit,
            'credit': credit,
            'date': date,
            'move_id': move_id,
            'partner_id': partner_id,
        })
    ref = None

    def create_move(self, amount, ref, journal_id, debit_account, credit_account, partner_id, date, lable, payment_id=False):
        move_id = self.env['account.move'].create({
            'journal_id': journal_id,
            'date': date,
            'ref': ref,
            'payment_id': payment_id,
        })
        # recivable
        self.create_move_line(move_id.id, debit_account, partner_id,
                              lable, amount, 0.0, date)
        # payment
        self.create_move_line(move_id.id, credit_account, partner_id,
                              lable, 0.0, amount, date)

        move_id.post()

    def create_payment(self, student_id, amount, currency):
        self.env['uofk.payment'].create({
            'reference': student_id.university_id,
            'name': student_id.name,
            # TODO: service must be generic
            'service': 1001,
            'currency': currency,
            'amount': amount,
        })

    def get_student_fees(self):
        dept_fees = self.env['uni.study_fees.departments'].search([
            ('department_id', '=', self.department_id.id),
            ('certificate_type_id', '=',
             self.certificate_type_id.id),
            ('year_id', '=', self.year_id.id),
            ('state', '=', 'done')
        ], limit=1)

        if not dept_fees:
            # No dept fees? let's try the global faculty fees
            faculty_fees = self.env['uni.study_fees.line'].search([
                ('faculty_id', '=', self.faculty_id.id),
                ('certificate_type_id', '=',
                 self.certificate_type_id.id),
                ('year_id', '=', self.year_id.id), ('state', '=', 'done')
            ], limit=1)

        return dept_fees or faculty_fees

    def committee_approval(self):
        # TODO: rewrite this function on proper way
        
        self.write({'state': 'reg_office'})

    def reg_confirmation(self):
        fees = self.get_student_fees()
        if not fees:
            raise Warning(
                _('Please configure the faculty tuition fees for this academic year!')
            )
        include_registration_fees = False

        discount_percentage = 0.0

        discount = 0.0

        category_name =""

        std_fees = fees.study_fees/2

        value = 0.0

        if self.category_id:
            for category in self.category_id:
                discount_percentage += category.general_discount
                value = category.general_discount
                include_registration_fees = category.include_registration_fees

                discount += ((fees.registration_fees * discount_percentage) /
                            100.0) if include_registration_fees else 0.0

                discount += (std_fees * value) / 100.0

                std_fees -= discount 

                category_name += category.name + ","

        print('----------- discount',discount)
        domain = [('faculty_id', '=', self.faculty_id.id)]
        level_ids = self.env['uni.faculty.level'].search(domain)
        semester_ids = self.env['uni.faculty.semester'].search(domain)
        if not level_ids or not semester_ids:
            msg = "Please create levels and semesters for "+self.student_id.faculty_id.name
            raise Warning(
                _(msg)
            )

        discount_desc = category_name+" ----> " + \
            str(discount_percentage) if discount > 0 else ""

        admission_id = self.env['uni.admission'].search([('student_id','=',self.student_id.id)])
        student_id = self.env['student.fees'].search([('student_id','=',self.student_id.id)])
        student_id.unlink()
        for level in level_ids:
            flag = True
            registration_fees = fees.registration_fees
            if self.is_installment:
                semester_ids = semester_ids[0]
            for semester in semester_ids:
                # registration fees is per year
                if not flag:
                    registration_fees = 0



                self.env['student.fees'].create({
                    'student_id': self.student_id.id,
                    'level_id': level.id,
                    'semester_id': semester.id,
                    'registration_fees': registration_fees,
                    'study_fees': fees.study_fees/2,
                    'discount': discount/2,
                    'other_fees' : [(6, 0, self.add_fees.ids)] if (level.order == 1 and semester.order == 1) else 0,
                    'discount_desc': discount_desc,
                })
                flag = False
        
        amount = fees.registration_fees + fees.study_fees - discount
        if amount == 0:
            self.write({'state': 'done'})
        else:
            currency = self.certificate_type_id.currency_id.name
         
        self.student_id.write({
            'category_id' : [(6, 0, self.category_id.ids)],
            'admission_rec' : admission_id.id,
            })
        self.write({'state': 'payment'})


    