# -*- coding: utf-8 -*-
from odoo import fields, models, api
import random
from odoo.exceptions import AccessDenied


class VrTrainee(models.Model):
    _name = "vr.trainee"
    _description = "VR Trainee"
    _rec_name = 'pin'
    _order = 'id desc'
    # _check_company_auto = True

    pin = fields.Char(default="New", index=True, copy=False)
    name = fields.Char(string="Name", index=True, groups="virsat.group_view_vr_trainee_name")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    vr_game_result_ids = fields.One2many('vr.game.result', 'vr_trainee_id')

    @api.model
    def create(self, vals):
        """Inherit to get a unique pin number"""

        res = super(VrTrainee, self).create(vals)
        seq_max_size = self.env.company.vr_trainee_seq_max_size
        company_pin_records = len(self.search([('company_id', '=', self.env.company.id)]))
        reserved_pin_obj = self.env['vr.reserved.pin']
        reserved_pins = reserved_pin_obj.search([('company_id', '=', self.env.company.id)]) or []
        total_seq_max_size = seq_max_size - len(reserved_pins)

        if company_pin_records > total_seq_max_size:
            raise AccessDenied("Sorry! Maximum sequence size exceeded. Please contact administrator.")

        seq_size = self.env.company.vr_trainee_seq_size
        pin = self.generate_pin(seq_size)
        exist = self.search([('pin', '=', pin), ('company_id', '=', self.env.company.id)]) or (reserved_pins and reserved_pins.filtered(lambda x: x.pin == pin))

        while exist:
            pin = self.generate_pin(seq_size)
            exist = self.search([('pin', '=', pin), ('company_id', '=', self.env.company.id)]) or reserved_pins.filtered(lambda x: x.pin == pin)

        res.pin = pin

        return res

    def generate_pin(self, length):
        """Generate a random PIN code of given length"""
        pin = ""
        for i in range(length):
            pin += str(random.randint(0, 9))

        return pin

    def view_game_result(self):
        self.ensure_one()
        return {
            'name': 'Game Result',
            'type': 'ir.actions.act_window',
            'res_model': 'vr.game.result',
            'view_mode': 'tree,form',
            'domain': [('name', '=', self.pin)],
        }


class VrTraineeReservedPin(models.Model):
    _name = "vr.reserved.pin"
    _description = "VR Reserved Pin"
    _rec_name = 'pin'

    pin = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
