from odoo import models, fields, api
from odoo.tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class import_wizard(models.TransientModel):
	_name = 'import.wizard'
	_description = 'emaar data migration'

	complex_id = fields.Many2one(
		'residential.complex', ondelete='cascade', required=True)

	def create_check(self, name, first_installment_date, partner_id, total, advance, paid_amount, payment_period, amount, first_check_amount):
		customer_check_id = self.env['customer.check'].create({
			'date': fields.date.today(),
			'total_amount': total,
			'advance': advance,
			'paid_amount': paid_amount,
			'partner_id': partner_id.id,
			'monthes': payment_period,
			'start_date': first_installment_date,
			'state': 'draft',
			'last_batch_number': payment_period,
			'name': name
		})

		line = self.env['customer.check.line']
		check_number = 1
		start_date = datetime.strptime(
			str(first_installment_date), '%Y-%m-%d')
		for month in range(0, customer_check_id.monthes):
			line.create({
				'line_id': customer_check_id.id,
				'check_number': check_number,
				'date': fields.date.today(),
				'due_date': start_date,
				'amount': amount,
			})
			start_date = start_date + relativedelta(months=1)
			check_number += 1
		#customer_check_id.check_description()
		return customer_check_id

	@api.multi
	def process_import(self):
		for record in self.env['emaar.migration'].search([]):
			print(record.id)
			land_id = self.env['realestate.complex'].search(
				[('realestate_num', '=', record.land_id), ('complex_id', '=', self.complex_id.id)], limit=1)
			if not land_id:
				land_id = self.env['realestate.complex'].create({
					'complex_id': self.complex_id.id,
					'realestate_num': record.land_id,
					'shape_area': record.area,
					'price_of_meter': (record.sale_amount / record.area if record.area else 1),
					'realestate_type': 'single',
					'state': 'scheduled',
				})

			if not record.customer_name:
				continue

			customer_id = self.env['res.partner'].create({
				'name': record.customer_name,
				'phone': record.phone if record.phone else "--",
				'email': "--",
				'working_comany': "--",
				'gender': 'male',
				'street': "--",
				'type_of_proof_of_personality': 'national_number',
				'place_of_relesed': "--",
				'date_of_relesed': fields.Date.today(),
				'identifcation_number': "--",
				'city': "--",
			})
			install = int(record.residual_amount /
                            record.install_amount if record.install_amount else 1)
			name = land_id.realestate_num+' / '+customer_id.name
			check_id = self.create_check(name, record.first_installment_date, customer_id, record.sale_amount, record.advance, record.paid_amount, install,
                                record.install_amount, 0.0)
			check_id.land_id = land_id.id

			reservation_request_id = self.env['reservation.request'].create({
				'exist': True,
				'partner_id': customer_id.id,
				'complex_id': self.complex_id.id,
				'land_id': land_id.id,
				'payment_type': 'installment',
				'other': int(record.residual_amount / record.install_amount if record.install_amount else 1),
				'custom_configuration': True,
				'transaction_type': 'implementation',
				'collection_date': record.collection_date,
				'custom_down_payment': record.paid_amount,
				'custom_monthly_installment': record.install_amount,
				'bank_name': 'وصل امانة',
				'phone': record.phone if record.phone else "--",
				'job': '--',
				'function': "--",
				'working_comany': "--",
				'gender': 'male',
				'type_of_proof_of_personality': 'national_number',
				'place_of_relesed': "--",
				'date_of_relesed': fields.Date.today(),
				'identifcation_number': "--",
				'country_id': "-----",
				'address': "--",
				'email': "--",
				'state': 'under_implementation',
				'customer_check_id': check_id.id,
				"check_number": record.installment_num - int(record.residual_amount / record.install_amount if record.install_amount else 1),
			})
			land_id.state = 'under_implementation'
			record.unlink()


class import_check_wizard(models.TransientModel):
	_name = 'check.wizard'
	_description = 'emaar check migration'

	def process_import_check(self):


		
		vendor_check = self.env['check.migration'].search([])


		vendor_check_id = self.env['oncreadit.check'].create({
				'date': fields.date.today(),
				'amount': sum(line.amount for line in vendor_check),
				'partner_id': self.env['res.partner'].create({'name' : vendor_check[0].vendor}).id,
				'state': 'draft',
			})

		line = self.env['oncreadit.check.line']

		for check in vendor_check:
			line.create({
				'line_id': vendor_check_id.id,
				'check_number': check.check_number,
				'date': fields.date.today(),
				'due_date': check.date,
				'amount':  check.amount,
				'description' : check.vendor,
				'journal_id' : check.bank
			})