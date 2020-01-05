from odoo import api, fields, models


class Student(models.Model):
    _inherit = 'uni.student'


    def calc_total_residaul(self):
        return sum (line.sub_total - line.paid_amount  for line in self.fees_ids if line.paid_amount != 0)
    

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        readonly=True,
    )

    certificate_type_id = fields.Many2one(
        comodel_name='uni.certificate.type',
        string='Certificate Type',
    )

    currency_id = fields.Many2one('res.currency' , string="Currency")

    admission_date = fields.Date(string='Admission date')

    admission_rec = fields.Many2one('uni.admission', string="Admission Record")

    category_id = fields.Many2many(
        string="Discount Type",
        comodel_name="uni.student_category",
        readonly=True,
    )

    fees_ids = fields.One2many(
        string="Student Fees",
        comodel_name="student.fees",
        inverse_name="student_id",
        readonly=False
    )

    fees_payment_ids = fields.One2many(
        string="Fees Payments",
        comodel_name="fees.payment.line",
        inverse_name="student_id",
        readonly=False
    )

    amount_sub_total = fields.Float(
        string='Sub Total', store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Float(
        string='Total', store=True, readonly=True, compute='_compute_amount')
    discount = fields.Float(
        string='Discount', store=True, readonly=True, compute='_compute_amount')
    # TODO: get default recivable account
    '''account_id = fields.Many2one('account.account',
								 domain=lambda self: [('user_type_id.id', '=', self.env.ref(
									 'account.data_account_type_receivable').id)],
								 help="Student recivable account")
	'''
    guardian_national_id_img = fields.Binary(string="National ID Image", )
    student_national_id_img = fields.Binary(string="National ID Image", )

    # foot_ball = fields.Boolean(string="Foot Ball", )
    # volley_ball = fields.Boolean(string="Volley Ball", )
    # basket_ball = fields.Boolean(string="Basket Ball", )
    # swimming = fields.Boolean(string="Swimming", )
    # table_tennis = fields.Boolean(string="table tennis", )
    # other_sport = fields.Char(string="Other", )

    # memorizing_holly_quran = fields.Boolean(
    #     string="memorizing the holly Quran", )
    # poetry = fields.Boolean(string="Poetry", )
    # stage = fields.Boolean(string="Stage", )
    # singing = fields.Boolean(string="singing", )
    # other_cultural = fields.Char(string="Other", )

    
    kin_emergency = fields.Char()
    kin_ph_emergency = fields.Integer()

    # blood_group = fields.Selection(
    #     string='Blood group',
    #     selection=[
    #         ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), 
    #         ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    #     ],default='B+'
    # )
    allergies_disea = fields.Char()
    chronic_dsease = fields.Char()
    other_dsease =  fields.Char()

    type_admission = fields.Selection(
        selection=[
            ('new_admission', 'New Admission'),
            ('transfer' , 'Transer from another University'),
            ('upgrading' , 'Upgrading'),
            ('degree_holder' , 'Degree holder')
        ],default='new_admission'
    )

    is_previouse_admitt = fields.Selection(
        selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ],default='no'
    )

    reasons = fields.Selection(
        selection=[
            ('resignation', 'Resignation'),
            ('acadimic_dismissal', 'Acadimic Dismissal'),
        ],default =''
    )

    other = fields.Char()

    sibling_in_nile = fields.Integer( )





    @api.one
    @api.depends('fees_ids.sub_total', 'fees_ids.discount')
    def _compute_amount(self):
        self.amount_sub_total = sum(
            line.sub_total for line in self.fees_ids)
        self.discount = sum(
            line.discount for line in self.fees_ids)
        self.amount_total = self.amount_sub_total  # - self.discount


    def create_move(self):
        return {
            'name': _('Fees Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'post.customer.check.action',
            'type': 'ir.actions.act_window',
            'target':'new',
            'context':{
                'default_name':self.check_number,
                'default_partner_id':self.line_id.partner_id.id,
                'default_amount': self.amount - self.paid_amount,
                'default_line_id':self.id,
                'default_description':self.description,
                'default_currency_id':self.currency_id.id,
                }

        }
