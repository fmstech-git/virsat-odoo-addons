# -*- coding: utf-8 -*-
from odoo import fields, models, api
import random
from odoo.exceptions import ValidationError


class VrTrainee(models.Model):
    _name = "vr.trainee"
    _description = "VR Trainee"
    _rec_name = 'pin'
    _order = 'id desc'
    _check_company_auto = True

    pin = fields.Char(default="New", index=True, copy=False, string="PIN", required=True)
    name = fields.Char(string="Name", index=True, groups="virsat.group_view_vr_trainee_name", copy=False, required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    vr_game_result_ids = fields.One2many('vr.game.result', 'vr_trainee_id')

    _sql_constraints = [
        ('name_company_uniq', 'unique(name,company_id)', 'Trainee Name already exist in your company.'),
        ('pin_company_uniq', 'unique(pin,company_id)', 'Pin must be unique in your company.'),
    ]

    @api.model
    def create(self, vals):
        """Inherit to get a unique pin number"""

        seq_max_size = self.env.company.vr_trainee_pin_max_size
        company_pin_records = len(self.search([('company_id', '=', self.env.company.id)]))
        reserved_pin_obj = self.env['vr.reserved.pin']
        reserved_pins = reserved_pin_obj.search([('company_id', '=', self.env.company.id)]) or []
        total_seq_max_size = seq_max_size - len(reserved_pins)

        if company_pin_records >= total_seq_max_size:
            raise ValidationError("Sorry! Maximum PIN size exceeded. Please contact administrator.")

        seq_size = self.env.company.vr_trainee_pin_size
        pin = self.generate_pin(seq_size)
        exist = self.search([('pin', '=', pin), ('company_id', '=', self.env.company.id)]) or (reserved_pins and reserved_pins.filtered(lambda x: x.pin == pin))

        while exist:
            pin = self.generate_pin(seq_size)
            exist = self.search([('pin', '=', pin), ('company_id', '=', self.env.company.id)]) or (reserved_pins and reserved_pins.filtered(lambda x: x.pin == pin))

        vals['pin'] = pin

        return super(VrTrainee, self).create(vals)

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
            'res_model': 'vr.game.result.report',
            'view_mode': 'kanban,tree',
            'domain': [('trainee_id', '=', self.id)],
        }


class VrTraineeReservedPin(models.Model):
    _name = "vr.reserved.pin"
    _description = "VR Reserved Pin"
    _rec_name = 'pin'

    pin = fields.Char(string="PIN")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('pin_company_uniq', 'unique(pin,company_id)', 'PIN must be unique per company.'),
    ]

    @api.model
    def create(self, vals):
        res = super(VrTraineeReservedPin, self).create(vals)
        vr_trainee = self.env['vr.trainee'].with_company(res.company_id.id).search([('pin', '=', res.pin)])
        print(vr_trainee)

        if vr_trainee:
            raise ValidationError("Sorry! PIN already assigned to %s under company %s." % (vr_trainee.name, res.company_id.name))

        return res
