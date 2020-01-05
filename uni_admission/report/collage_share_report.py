from odoo import fields, api, models


class report_collage_share(models.AbstractModel):
    _name = 'report.collage_share.report'

    def get_data(self, start, end):
        collages = self.env['res.company'].search([('type', '=', 'faculty')])
        student_fees = self.env['student.fees']
        datas = []
        sum_total = sum_university_fees = sum_collage_fees = sum_residual_total = sum_residual_university_fees = sum_residual_collage_fees = 0
        for collage in collages:
            collage_fees = university_fees = total = 0
            residual_collage_fees = residual_university_fees = residual_total = 0

            payments = student_fees.search(
                [('paid', '=', True), ('faculty_id', '=', collage.id), ('payment_date', '>', start), ('payment_date', '<=', end)])
            for record in payments:
                collage_fees += record.sub_total if record.student_id.admission_type == "public" else 0.0
                university_fees += record.sub_total if record.student_id.admission_type == "private" else 0.0
                total += record.sub_total
            residual = payments = student_fees.search(
                [('paid', '=', False), ('faculty_id', '=', collage.id)])
            for record in residual:
                residual_collage_fees += record.sub_total if record.student_id.admission_type == "public" else 0.0
                residual_university_fees += record.sub_total if record.student_id.admission_type == "private" else 0.0
                residual_total += record.sub_total
            datas.append([collage.name, total, university_fees, collage_fees,
                          residual_total, residual_university_fees, residual_collage_fees])
            sum_total += total
            sum_university_fees += university_fees
            sum_collage_fees += collage_fees
            sum_residual_total += residual_total
            sum_residual_university_fees += residual_university_fees
            sum_residual_collage_fees += residual_collage_fees
        return datas, [sum_total, sum_university_fees, sum_collage_fees,
                       sum_residual_total, sum_residual_university_fees, sum_residual_collage_fees]

    @api.multi
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_id', []))
        start = data['form'].get('start')
        end = data['form'].get('end')

        datas, totals = self.get_data(start, end)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'start': start,
            'end': end,
            'datas': datas,
            'totals': totals,
        }

        return self.env['report'].render('uni_admission.collage_share_report', docargs)
