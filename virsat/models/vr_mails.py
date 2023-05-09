# -*- coding: utf-8 -*-
from odoo import fields, models, api


class VrMails(models.Model):
    _name = "virsat.vr.mails"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "VIRSAT VR Mails"
    _order = 'id desc'

    name = fields.Char()

    def view_game_result(self):
        self.ensure_one()
        return {
            'name': 'VR Game Result',
            'type': 'ir.actions.act_window',
            'res_model': 'vr.game.result',
            'view_mode': 'tree,form',
            'domain': [('vr_mail_id', '=', self.id)],
        }