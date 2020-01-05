
from odoo import api, fields, models, _


class account_voucher(models.Model):
    _inherit = "account.voucher"

    on_credit_check_id = fields.Many2one(
        'oncreadit.check', 'On Credit Check', copy=False, readonly=True)

    def on_credit_check(self, cr, uid, ids, context=None):
        onc_check = self.pool.get('oncreadit.check')

        voucher_obj = self.browse(cr, uid, ids[0], context)
        if voucher_obj.state == 'draft':
            raise osv.except_osv(_('Incorrect state'),
                                 _('Please valiDate voucher first'))
        if voucher_obj.on_credit_check_id:
            onc_check_id = voucher_obj.on_credit_check_id.id
        else:
            vals = {
                'name': voucher_obj.number,
                'partner_id': voucher_obj.partner_id.id,
                'Date': voucher_obj.Date,
                'reference': voucher_obj.number,
                'amount': voucher_obj.amount,
                'account_id': voucher_obj.account_id.id,
                'journal_id': voucher_obj.journal_id.id,
                'voucher_id': voucher_obj.id,
                'state': 'draft',
            }
            onc_check_id = onc_check.create(cr, uid, vals, context=context)
            voucher_obj.write({
                'on_credit_check_id': onc_check_id
            })

        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(
            cr, uid, 'account_voucher_custom', 'on_credit_check_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(
            cr, uid, 'account_voucher_custom', 'on_credit_check_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('On Credit Checks'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'oncreadit.check',
            'res_id': onc_check_id,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'type': 'ir.actions.act_window',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}},
        }
