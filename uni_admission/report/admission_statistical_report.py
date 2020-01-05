from odoo import fields, api, models

# TODO: this report must become support certificate type and admission category


class admission_statistical(models.AbstractModel):
    _name = 'report.uni_admission.admission_statistical'

    def get_domain(self, domain, state, operater):
        domain.append(('state', operater, state))
        return domain

    @api.multi
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_id', []))
        year_id = data['form'].get('year_id')[0]
        admission_category_id = data['form'].get('admission_category_id')[
            0] if data['form'].get('admission_category_id') else False
        admission_type = data['form'].get('admission_type')
        admission = self.env['uni.admission']
        registration_details = []
        totals = {
            'number_of_candidates': 0,
            'complete_the_procedures': 0,
            'not_come': 0,
            'registered': 0,
            'not_registered': 0,
        }

        for collage in self.env['res.company'].search([('type', '=', 'faculty')]):
            line = {}
            line['not_registered_perc'] = line['not_come_perc'] = line['registered_perc'] = 0

            line['name'] = collage.name
            # passing domain by this way is work around for calling by reference
            line['number_of_candidates'] = admission.search_count([('year_id', '=', year_id),
                                                                   ('admission_type',
                                                                    '=', admission_type),
                                                                   ('faculty_id',
                                                                    '=', collage.id)
                                                                   ])
            totals['number_of_candidates'] += line['number_of_candidates']

            line['complete_the_procedures'] = admission.search_count(
                self.get_domain([('year_id', '=', year_id),
                                 ('admission_type', '=', admission_type),
                                 ('faculty_id', '=', collage.id)
                                 ], 'done', '='))
            totals['complete_the_procedures'] += line['complete_the_procedures']

            line['not_come'] = admission.search_count(
                self.get_domain([('year_id', '=', year_id),
                                 ('admission_type', '=', admission_type),
                                 ('faculty_id', '=', collage.id)
                                 ], 'form', '='))
            totals['not_come'] += line['not_come']

            line['registered'] = admission.search_count(
                self.get_domain([('year_id', '=', year_id),
                                 ('admission_type', '=', admission_type),
                                 ('faculty_id', '=', collage.id)
                                 ], 'done', '='))
            totals['registered'] += line['registered']

            line['not_registered'] = admission.search_count(
                self.get_domain([('year_id', '=', year_id),
                                 ('admission_type', '=', admission_type),
                                 ('faculty_id', '=', collage.id)
                                 ], 'done', '!='))
            totals['not_registered'] += line['not_registered']

            if line['number_of_candidates'] != 0:
                line['not_registered_perc'] = round((
                    line['not_registered'] / (line['number_of_candidates'] * 1.0)) * 100, 2)
                line['not_come_perc'] = round((
                    line['not_come'] / (line['number_of_candidates'] * 1.0)) * 100, 2)
                line['registered_perc'] = round((
                    line['registered'] / (line['number_of_candidates'] * 1.0)) * 100, 2)
            registration_details.append(line)
        if totals['number_of_candidates'] != 0:
            totals['registered_per'] = round((
                totals['registered'] / (totals['number_of_candidates'] * 1.0)) * 100.0, 2)
            totals['not_registered_per'] = round((
                totals['not_registered'] / (totals['number_of_candidates'] * 1.0)) * 100.0, 2)
            totals['not_come_per'] = round((
                totals['not_come'] / (totals['number_of_candidates'] * 1.0)) * 100.0, 2)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'registration_details': registration_details,
            'totals': totals,
        }

        return self.env['report'].render('uni_admission.admission_statistical_report', docargs)
