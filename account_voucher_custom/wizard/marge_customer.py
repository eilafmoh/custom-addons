
from odoo import api,fields,models, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta



class marge_customers(models.Model):
	_name = "marge.customers"
	_description = "Marge customer checks and create batches"

	customer_check= fields.Many2many('customer.check',string='Customer Checks' ,required=True , domain=[('state','=','open')])
	partner_id= fields.Many2one('res.partner','Customer',domain=[('customer','=',True)],required=True)
	bank_name=fields.Char('Customer Bank Name',required=True)
	rack_number=fields.Integer('Rack Number',required=True)
	first_is_advance=fields.Boolean('First is advance ?')
	date=fields.Date('First check Date',required=True)
	check_number=fields.Integer('First Check Number',required=True)
	period=fields.Integer('Period On Monthes')


	def marge(self):
		marge_customers = self
		if len(marge_customers.customer_check)< 2:
			raise UserError(_('You must choose more than 1 customer check to process.'))

		lines_number = len(marge_customers.customer_check[0].check_lines)
		total_amount = 0
		paid_amount = 0
		for customer_check in marge_customers.customer_check:
			total_amount = total_amount + customer_check.total_amount
			paid_amount = paid_amount + customer_check.paid_amount

			if len(customer_check.check_lines) != lines_number :
				raise UserError(_('It seems that there is cheks not equal to other group'))
			for line in customer_check.check_lines:
				if line.related_lines:
					raise UserError(_('It seems that there is check already represent group'))

		if total_amount > 0 :
			customer_ch = self.env['customer.check']
			customer_check_line = self.env['customer.check.line']
			vals = {
				'name':"Rak/"+str(marge_customers.rack_number),
				'partner_id':marge_customers.partner_id.id,
				'total_amount':total_amount,
				'paid_amount':paid_amount,
				'customer_bank_name':marge_customers.bank_name,
				'rack':marge_customers.rack_number,
			}
			new_obj = customer_ch.create(vals)

			amounts = []
			check_lines = []
			for item in range(len(marge_customers.customer_check[0].check_lines)):
				amounts.append(0)
				check_lines.append([])


			for customer_check in marge_customers.customer_check:
				index =0
				for check in customer_check.check_lines:
					amounts[index] = amounts[index] + check.amount
					check_lines[index].append(check)
					index = index + 1

			check_number = marge_customers.check_number
			date = datetime.strptime(str(marge_customers.date) , '%Y-%m-%d')
			index = 0
			lines_ids=[]
			for line in amounts:
				vals = {
					'amount':line,
					'description':self.mapping(index +1),
					'check_number':check_number,
					'rack':marge_customers.rack_number,
					'due_date': date ,

					'account_id':marge_customers.bank_name,
					'date':datetime.now().strftime('%Y-%m-%d'),
					'line_id':new_obj.id,
				}
				new_line = customer_check_line.create(vals)

				for item in check_lines[index]:
					item.write({'check_line_id':new_line.id})


				check_number = check_number + 1
				date = date + relativedelta(months=marge_customers.period)
				index =  index + 1
			for item in check_lines[0]:
				item.line_id.write({'state':'marged','check_line_id':new_obj.id}) #,'name':"Rak/"+str(marge_customers.rack_number)})
			customer_ch.browse(new_obj.id).write({'state':'open'})
		return True



	def mapping(self,number):
		mapping = {
			'1':'الاول','2':'الثانى','3':'الثالث','4':'الرابع',
			'5':'الخامس','6':'السادس','7':'السابع','8':'الثامن',
			'9':'التاسع','10':'العاشر','11':'الحادى عشر','12':'الثانى عشر',
			'13':'الثالث عشر','14':'الرابع عشر','15':'الخامس عشر','16':'السادس عشر',
			'17':'السابع عشر','18':'الثامن عشر','19':'التاسع عشر','20':'العشرون',
			'21':'الحادى والعشرون','22':'الثانى والعشرون','23':'الثالث والعشرون','24':'الرابع والعشرون',
			'25':'الخامس والعشرون','26':'السادس والعشرون','27':'السابع والعشرون','28':'الثامن والعشرون',
			'29':'التاسع والعشرون','30':'الثلاثين','31':'الحادى والثلاثين','32':'الثانى والثلاثين',
			'33':'الثالث والثلاثين','34':'الرابع والثلاثين','35':'الخامس والثلاثين','36':'السادس والثلاثين',
			'37':'السابع والثلاثين','38':'الثامن والثلاثين','39':'التاسع والثلاثين','40':'الاربعين',
			'41':'الحادى و الاربعين ','42':'الثانى والاربعين ','43':'الثالث والاربعين','44':'الرابع والاربعين ',
			'45':'الخامس والاربعين ','46':'السادس والاربعين ','47':'السابع والاربعين ','48':'الثامن والاربعين ',
			'49':'التاسع والاربعين ','50':'الخمسين ','51':'الحادى والخمسين ','52':'الثانى والخمسين ',
			'53':'الثالث والخمسين ','54':'الرابع والخمسين ','55':'الخامس والخمسين ','56':'السادس والخمسين ',
			'57':'السابع والخمسين ','58':'الثامن والخمسين ',
			'59':'التاسع و الخمسين ','60':'الستين ','61':'الحادى والستين ','62':'الثانى والستين ',
			'63':'الثالث والستين ','64':'الرابع والستين ','65':'الخامس والستين ','66':'السادس والستين ',
			'67':'السابع والستين ','68':'الثامن والستين ','69':'التاسع والستين ','70':'السبعين ',
			'71':'الحادى والسبعين ','72':'الثانى والسبعين ','73':'الثالث والسبعين ','74':'الرابع والسبعين ',
			'75':'الخامس والسبعين ','76':'السادس والسبعين ','77':'السابع والسبعين ','78':'الثامن والسبعين ',
			'79':'التاسع والسبعين ','80':'الثمانون','81':'الحادى والثمانون','82':'الثانى والثمانون',
			'83':'الثالث والثمانون','84':'الرابع والثمانون','85':'الخامس والثمانون','86':'السادس والثمانون',
			'87':'السابع والثمانون','88':'الثامن والثمانون','89':'التاسع والثمانون','90':'التسعون',
			'91':'الحادى والتسعون','92':'الثانى والتسعون','93':'الثالث والتسعون ','94':'الرابع و التسعون ',
			'95':'الخامس والتسعون ','96':'السادس والتسعون ','97':'السابع والتسعون ',
			'98':'الثامن والتسعون ','99':'التاسع والتسعون ','100':'المئة'
		}

		return "القسط "+mapping[str(number)]



