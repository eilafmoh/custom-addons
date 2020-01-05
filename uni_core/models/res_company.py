from odoo import api, fields, models , _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class res_company(models.Model):
    _inherit = 'res.company'
    _description = 'Company'

    name = fields.Char(related='partner_id.name', string='Faculty Name', required=True, store=True, readonly=False)

    code = fields.Char(string='Faculty Code', required=True, translate=True)

    last_std_no = fields.Integer('Last Student No.', required=True)

class account_voucher(models.Model):
    _inherit = 'account.voucher'
    _description = 'Account Voucher'

    company_id = fields.Many2one('res.company', 'Faculty',
        store=True, readonly=True, states={'draft': [('readonly', False)]},
        related='journal_id.company_id', default=lambda self: self._get_company())

    level_id = fields.Many2one('uni.faculty.level' , string="Year")
    semester_id = fields.Many2one('uni.faculty.semester',string="Semester")

    fees_line_id = fields.Many2one(comodel='student.fees',string='Line')
    
class product_template(models.Model):
    _inherit = "product.template"

    company_id = fields.Many2one(
        'res.company', 'Faculty',
        default=lambda self: self.env['res.company']._company_default_get('product.template'), index=1)

class purchase_order(models.Model):
    _inherit = "purchase.order"


    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    company_id = fields.Many2one('res.company', 'Faculty', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.user.company_id.id)


    
class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    company_id = fields.Many2one('res.company', related='order_id.company_id', string='Faculty', store=True, readonly=True)


class account_move(models.Model):
    _inherit = "account.move"

    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Faculty', store=True, readonly=True)

class stock_warehouse(models.Model):
    _inherit = "stock.warehouse"

    company_id = fields.Many2one(
        'res.company', 'Faculty', default=lambda self: self.env['res.company']._company_default_get('stock.inventory'),
        index=True, readonly=True, required=True,
        help='The company is automatically set from your user preferences.')

class stock_picking(models.Model):
    _inherit = "stock.picking"

    company_id = fields.Many2one(
        'res.company', 'Faculty',
        default=lambda self: self.env['res.company']._company_default_get('stock.picking'),
        index=True, required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

class crossover_budget(models.Model):
    _inherit = "crossovered.budget"

    company_id = fields.Many2one('res.company', 'Faculty', required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.budget.post'))

class account_invoice(models.Model):
    _inherit = "account.invoice"

    company_id = fields.Many2one('res.company', 'Faculty',
        store=True, readonly=True, states={'draft': [('readonly', False)]},
        related='journal_id.company_id', default=lambda self: self.env.user.company_id)

    level_id = fields.Many2one('uni.faculty.level' , string="Year")
    semester_id = fields.Many2one('uni.faculty.semester',string="Semester")

class account_budget(models.Model):
    _inherit = "crossovered.budget"

    @api.multi
    def unlink(self):
        for budget in self:
            if budget.state != 'draft':
                raise ValidationError(_('The budget must be in dratf state to be deleted.'))
            else:
                return super(account_budget, self).unlink()