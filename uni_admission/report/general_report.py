from odoo import fields, api, models


class general_report(models.AbstractModel):
    _name = 'report.uni_admission.general_report'

    def normlize_admission_type(self, admission_type):
        return ['public', 'private'] if admission_type == 'both' else [admission_type]

    def prepare_domain(self, faculty_ids, department_ids, specialization_ids, level_ids, admission_category_ids, admission_type):
        faculty_ids = [faculty.id for faculty in self.env['res.company'].search(
            [])] if not faculty_ids else faculty_ids
        department_ids = [
            department.id for department in self.env['uni.faculty.department'].search([('faculty_id', 'in', faculty_ids)])] if not department_ids else department_ids
        specialization_ids = [
            specialization.id for specialization in self.env['uni.faculty.department.specialization'].search([('faculty_id', 'in', faculty_ids), ('department_id', 'in', department_ids)])] if not specialization_ids else specialization_ids
        admission_category_ids = [category_id.id for category_id in self.env['uni.student_category'].search(
            [])]if not admission_category_ids else admission_category_ids
        level_ids = [
            level.id for level in self.env['uni.faculty.level'].search([])] if not level_ids else level_ids
        return [
            ('faculty_id', 'in', faculty_ids),
            #('department_id', 'in', department_ids),
            #('specialization_id','in', specialization_ids),
            #('category_id', 'in',admission_category_ids),
            #('level_id', 'in', level_ids),
            #('admission_type', 'in', admission_type)
        ]

    def get_data(self, faculty_ids, department_ids, specialization_ids, level_ids, admission_category_ids, admission_type):
        registration_details = []
        totals = {
            'all': 0.0,
            'registerd': 0.0,
            'unregisterd': 0.0,
        }
        i = 1
        student_obj = self.env['uni.student']
        faculty_ids = self.env['res.company'].search(
            [('type', '=', 'faculty')]) if not faculty_ids else self.env['res.company'].browse(faculty_ids)
        for faculty in faculty_ids:
            line = {}
            line['collage'] = faculty.name
            domain = self.prepare_domain([faculty.id], department_ids,
                                         specialization_ids, level_ids, admission_category_ids, admission_type)
            student_ids = [
                student.id for student in student_obj.search(domain)]
            if not student_ids:
                continue
            flag = True
            fees_domain = [
                ('faculty_id', '=', faculty.id),
                ('student_id', 'in', student_ids),
                ('department_id', 'in', department_ids),
                ('specialization_id', 'in', specialization_ids),
                ('level_id', 'in', level_ids),
                ('paid', '=', flag)
            ]
            registerd_student = self.env['student.fees'].search_count(
                fees_domain)
            flag = False
            unregisterd_student = len(student_ids) - registerd_student
            line['all'] = len(student_ids)
            line['registerd'] = registerd_student
            line['unregisterd'] = unregisterd_student
            line['registerd_percentage'] = (
                float(registerd_student) / len(student_ids)) * 100.0
            line['unregisterd_percentage'] = (
                float(unregisterd_student) / len(student_ids)) * 100.0
            registration_details.append(line)
            totals['all'] += len(student_ids)
            totals['registerd'] += registerd_student
            totals['unregisterd'] += unregisterd_student
        return registration_details, totals

    @api.multi
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_id', []))
        faculty_ids = data['form'].get('faculty_ids')
        department_ids = data['form'].get('department_ids')
        specialization_ids = data['form'].get('specialization_ids')
        level_ids = data['form'].get('level_ids')
        admission_category_ids = data['form'].get('admission_category_ids')
        admission_type = data['form'].get('admission_type')

        admission_type = self.normlize_admission_type(admission_type)
        registration_details, totals = self.get_data(faculty_ids, department_ids, specialization_ids,
                                                     level_ids, admission_category_ids, admission_type)

        totals['registerd_percentage'] = (
            float(totals['registerd']) / totals['all']) * 100.0
        totals['unregisterd_percentage'] = (
            float(totals['unregisterd']) / totals['all']) * 100.0
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'registration_details': registration_details,
            'totals': [totals],
        }

        return self.env['report'].render('uni_admission.general_report', docargs)
