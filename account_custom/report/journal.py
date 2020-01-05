# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class Journal(models.Model):
    _inherit = "account.move"


    def sum_debit(self):
        return sum(line.debit for line in self.line_ids)

    def sum_credit(self):
        return sum(line.credit for line in self.line_ids)
