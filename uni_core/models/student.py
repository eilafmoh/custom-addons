from datetime import date, timedelta
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.uni_core.utils import get_default_faculty


class Student(models.Model):
    _name = 'uni.student'
    _description = 'Student'
    _inherits = {'res.users': 'user_id'}
    _inherit = ['mail.thread']
    _rec_name = 'university_id'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        index=True
    )

    name_en = fields.Char(
        string='Name (English)',
        compute='_compute_name_en',
        store=True,
        index=True
    )

    # Arabic
    first_name = fields.Char(string='First name', required=True)#, readonly=True)
    middle_name = fields.Char(string='Middle name',
                              required=True)#, readonly=True)
    last_name = fields.Char(string='Last name')#, readonly=True)
    fourth_name = fields.Char(string='Fourth name')#, readonly=True)

    # English
    first_name_en = fields.Char(string='First name (English)')#, readonly=True)
    middle_name_en = fields.Char(string='Middle name (English)')#, readonly=True)
    last_name_en = fields.Char(string='Last name (English)')#, readonly=True)
    fourth_name_en = fields.Char(string='Fourth name (English)')#, readonly=True)

    birth_date = fields.Date(string='Birth date')
    place_of_birth = fields.Char(string='Place of Birth')

    gender = fields.Selection(
        string='Gender',
        selection=[
            ('male', 'Male'),
            ('female', 'Female')
        ]
    )

    nationality_id = fields.Many2one(
        comodel_name='res.country',
        string='Nationality'
    )
    national_id = fields.Char(string="National ID", )

    religion = fields.Selection(string='Religion', selection=[
        ('islam', 'Islam'),
        ('christianity', 'Christianity'),
        ('other', 'Other')
    ])

    # Admisison info
    university_id = fields.Char(
        string='University ID',
        required=True,
        index=True,
        )#readonly=True,)

    index_id = fields.Char(
        string='Index Number',
        index=True,
        )

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        string='Faculty',
        required=True,
        )#readonly=True,)

    department_id = fields.Many2one(
        comodel_name='uni.faculty.department',
        domain="[('faculty_id', '=', faculty_id)]",
        string="Department",
        )#readonly=True)

    specialization_id = fields.Many2one(
        'uni.faculty.department.specialization',
        domain="[('department_id', '=', department_id)]",
        string='Specialization',
        )#readonly=True,)

    batch_id = fields.Many2one(
        'uni.faculty.department.batch',
        domain="[('department_id', '=', department_id)]",
        string='Batch',
        )#readonly=True)

    level_id = fields.Many2one(
        'uni.faculty.level',
        string='Year',
        )

    semester_id = fields.Many2one(
        'uni.faculty.semester',
        string='Semester',
        )

    blood_group = fields.Selection(
        string='Blood group',
        selection=[('',''),
            ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), 
            ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
        ]
    )
    blood_image = fields.Binary(string="Blood doc")
    medical_data = fields.Many2one(
        'uni.health_service.medical_data', string="Medical Data")
    address = fields.Char(string="Address")
    # number_of_brother = fields.Integer(string="Number non adult Brother", )
    # in_university = fields.Integer(string="In University", )
    # in_school = fields.Integer(string="In School", )
    # elementary_school = fields.Char(string='Elementary School', index=True)
    # secondary_school_type = fields.Selection(
    #     string="Elementary School Type",
    #     selection=[
    #         ('public', 'Public'),
    #         ('private', 'Private'),
    #     ],
    # )

    secondary_school = fields.Char(string='Secondary School', index=True)
    examination_date = fields.Date('Examination Date')
    certificate_date = fields.Date('Date of Certificate')
    result_secondary_school = fields.One2many('secendery.school.result' , 'std_result_id' , string='Result of Secondary School Certificate')

    # Related user
    user_id = fields.Many2one(
        comodel_name='res.users',
        ondelete="restrict",
        required=True,
        index=True
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'New Student'),
            ('registered', 'Registered'),
            ('frozen', 'Suspended'),
            ('graduate', 'Graduate'),
        ],
        default='draft',
    )

    guardian_name = fields.Char(string="Guardian Name")
    guardian_relation = fields.Char(string="Guardian Relation")
    guardian_phone = fields.Char(string="Guardian Phone")
    guardian_job = fields.Char(string="Guardian Job")
    guardian_address = fields.Char(string="Guardian Address")
    guardian_nationality_id = fields.Char(string="Guardian National ID", )
    guardian_education_level = fields.Selection(
        string="Guardian Education Level",
        selection=[
            ('uneducated', 'Uneducated'),
            ('khalawi', 'Quran education'),
            ('primary_intermediate',
             'Primary / intermediate / foundation education'),
            ('secendery', 'Secendary'),
            ('collectors', 'Collectors'),
            ('postgraduate_studies', 'Postgraduate studies'),
            ('other', 'Other'),
        ],
    )
    guardian_email = fields.Char(string='Guardian Email')
    
    mother_name = fields.Char(string="Mother Name")
    mother_job = fields.Char(string="Mother Job")
    mother_education_level = fields.Selection(
        string="Mother Education Level",
        selection=[
            ('uneducated', 'Uneducated'),
            ('khalawi', 'Quran education'),
            ('primary_intermediate',
             'Primary / intermediate / foundation education'),
            ('secendery', 'Secendary'),
            ('collectors', 'Collectors'),
            ('postgraduate_studies', 'Postgraduate studies'),
            ('other', 'Other'),
        ],
    )

    relative_name = fields.Char(string="Name")
    relative_phone = fields.Char(string="Phone")
    relative_address = fields.Char(string="Address")
    
    city = fields.Char(related='user_id.city', inherited=True)

    # overridden inherited fields to bypass access rights, in case you have
    # access to the user but not its corresponding partner
    image = fields.Char(related='user_id.image', inherited=True)
    std_img = fields.Binary(string="Student Image", )
    phone = fields.Char(related='user_id.phone' , string='Phone', inherited=True)
    mobile = fields.Char(string='Mobile')
    email = fields.Char(related='user_id.email', inherited=True)
    state_id = fields.Char(
        related='user_id.state_id',
        string="Province",
        inherited=True
    )

    martial_status = fields.Selection(
        string="Martial Status",
        selection=[
            ('single', 'Single'),
            ('married', 'Married'),
            ('divorsed', 'Divorsed'),
            ('widow', 'Widow'),
        ],
    )

    partner_id = fields.Many2one('res.partner','Related Partner')


    
    # number_of_exam_seat = fields.Selection(
    #     string="Number of Exam Seat",
    #     selection=[
    #         ('one', 'One'),
    #         ('two', 'Two'),
    #         ('more', 'More'),
    #     ],)

    _sql_constraints = [
        (
            'user_id_unique',
            'UNIQUE(user_id)',
            _('The related user ID must be unique')
        ),
        (
            'university_id_unique',
            'UNIQUE(university_id)',
            _('The university ID must be unique')
        ),
    ]

    @api.depends('first_name', 'middle_name', 'last_name', 'fourth_name')
    def _compute_name(self):
        for record in self:
            record.name = '%s %s %s %s' % (
                record.first_name,
                record.middle_name,
                record.last_name,
                record.fourth_name,
            )

    @api.depends('first_name_en', 'middle_name_en', 'last_name_en', 'fourth_name_en')
    def _compute_name_en(self):
        for record in self:
            record.name_en = '%s %s %s %s' % (
                record.fourth_name_en,
                record.last_name_en,
                record.middle_name_en,
                record.first_name_en,   
            )

    @api.model
    def create(self, values):
        # Create a related user to enable Students to login
        name_en = '%s %s %s %s' % (
            values['first_name_en'],
            values['middle_name_en'],
            values['last_name_en'],
            values['fourth_name_en'],
        )
        values['name'] = '%s %s %s %s' % (
            values['first_name'],
            values['middle_name'],
            values['last_name'],
            values['fourth_name'],
        )
        user = self.env['res.users'].create({
            'name': name_en,
            'login': values['university_id'],
            'password': values['university_id']
        })
        values['user_id'] = user.id
        user.partner_id.write({
            'customer' : True,
            'ref' : values['university_id']
            })
        values['partner_id'] = user.partner_id.id
        # TODO: This is workaround find a better way
        

        return super(Student, self).create(values)
        
    @api.multi
    @api.constrains("birth_date")
    def _check_birth_date(self):
        # 15 years ago today
        max_date = date.today() - timedelta(days=15*365)
        for r in self:
            if r.birth_date:
                if fields.Date.from_string(r.birth_date) > max_date:
                    raise ValidationError(
                        _("Student age can't be less than 15 years")
                    )

    @api.model
    def name_search(self, name, args=[], operator='ilike', limit=100):
        records = self.search(
            ['|', '|', ('university_id', operator, name),
             ('name', operator, name), ('name_en', operator, name)] + args,
            limit=limit
        )

        return records.name_get()

    def coll_name(self):
        return self.first_name+" "+self.middle_name+" "+self.last_name+" "+self.fourth_name



class result(models.Model):
    _name = 'secendery.school.result'
    _rec_name = 'subject_name'

    std_result_id = fields.Many2one('uni.student')
    subject_name = fields.Char('Subject Name')
    percentage = fields.Integer('Percentage')
