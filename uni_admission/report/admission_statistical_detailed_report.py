from odoo import fields, api, models


class admission_statistical_detailed(models.AbstractModel):
    _name = 'report.uni_admission.admission_statistical_detailed'

    @api.multi
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_id', []))

        faculty_id = data['form'].get('faculty_id')[0]
        department_id = data['form'].get('department_id')[0]
        specialization_id = data['form'].get('specialization_id')[
            0] if data['form'].get('specialization_id') else False
        level_id = data['form'].get(
            'level_id')[0] if data['form'].get('level_id') else False
        semester_id = data['form'].get('semester_id')[
            0] if data['form'].get('semester_id') else False
        admission_category_id = data['form'].get('admission_category_id')[
            0] if data['form'].get('admission_category_id') else False
        # TODO: must add admission type to domain
        admission_type = data['form'].get('admission_type')

        domain = [
            ('faculty_id', '=', faculty_id),
            ('department_id', '=', department_id),
        ]

        domain.append(('specialization_id', '=', specialization_id)
                      ) if specialization_id else False
        domain.append(('level_id', '=', level_id)
                      ) if level_id else False
        domain.append(('semester_id', '=', semester_id)
                      ) if semester_id else False
        domain.append(('category_id', '=', admission_category_id)
                      ) if admission_category_id else False
        details = []
        for student in self.env['uni.student'].search(domain):
            fees = self.env['student.fees'].search([
                ('student_id', '=', student.id),
                ('level_id', '=', student.level_id.id),
                ('semester_id', '=', student.semester_id.id)
            ])
            # TODO : must not be static
            details.append({
                'name': student.name,
                'faculty': student.faculty_id.name,
                'department': student.department_id.name,
                'specialization': student.specialization_id.name,
                'level': student.level_id.name,
                'university_id': student.university_id,
                'admission_type': student.admission_type,
                'category_id': student.category_id.name,
                'fees': fees.registration_fees + fees.study_fees if fees else 0,
                'paid': fees.registration_fees + fees.study_fees if fees.paid else 0,
                'status': "Registerd" if fees.paid else "Not Registerd"
            })
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'details': details,
        }
        return self.env['report'].render('uni_admission.admission_statistical_detailed_report', docargs)
