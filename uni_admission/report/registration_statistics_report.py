from odoo import fields, api, models


class registration_statistics_report(models.AbstractModel):
    _name = 'report.uni_admission.registration_statistics_report'

    def get_faculty(self):
        faculties = self.env['res.company'].search([('type', '=', 'faculty')])
        return faculties

    def get_levels(self):
        levels = self.env['uni.faculty.level'].search([])
        return levels

    def get_students_of_faculty(self, level_id, faculty_id):
        student_ids = [stu.id for stu in self.env['uni.student'].search(
            [('faculty_id', '=', faculty_id.id), ])]
        fees = self.env['student.fees']
        flag = True
        domain = [('student_id', 'in', student_ids), ('paid', '=', flag)]
        counts = []
        counts.append(fees.search_count(domain))
        flag = False
        counts.append(fees.search_count(domain))
        return counts

    def get_students_counts(self, level_id, faculty_id):
        student_ids = [stu.id for stu in self.env['uni.student'].search(
            [('faculty_id', '=', faculty_id.id), ('level_id', '=', level_id.id)])]
        fees = self.env['student.fees']
        flag = True
        domain = [('student_id', 'in', student_ids),
                  ('level_id', '=', level_id.id), ('paid', '=', flag)]
        counts = []
        counts.append(fees.search_count(domain))
        flag = False
        counts.append(fees.search_count(domain))
        return counts

    '''def get_un_registered_students(self, level_id, faculty_id):
        students = self.env['uni.student'].search(
            [('faculty_id', '=', faculty_id.id), ('level_id', '=', level_id.id)])
	'''

    @api.multi
    def render_html(self, docids, data=None):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self,
            'docs': self,

        }

        return self.env['report'].render('uni_admission.registration_statistics_report', docargs)
