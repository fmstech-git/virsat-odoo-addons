# -*- coding: utf-8 -*-
from odoo import fields, models, api


class VrMails(models.Model):
    _name = "virsat.vr.mails"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "VIRSAT VR Mails"
    _order = 'id desc'

    name = fields.Char()
    company_code = fields.Char()
    company_id = fields.Many2one('res.company', compute='get_company', store=True)

    @api.depends('company_code')
    def get_company(self):
        for r in self:
            r.company_id = self.env['res.company'].search([('company_code', '=', r.company_code)]) or False

    def view_game_result(self):
        self.ensure_one()
        return {
            'name': 'VR Game Result',
            'type': 'ir.actions.act_window',
            'res_model': 'vr.game.result',
            'view_mode': 'tree,form',
            'domain': [('vr_mail_id', '=', self.id)],
        }