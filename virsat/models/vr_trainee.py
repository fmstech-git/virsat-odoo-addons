# -*- coding: utf-8 -*-
from odoo import fields, models, api
import random
from odoo.exceptions import ValidationError, Warning


class VrTrainee(models.Model):
    _name = "vr.trainee"
    _description = "VR Trainee"
    _rec_name = 'pin'
    _order = 'id desc'
    _check_company_auto = True

    pin = fields.Char(default="New", index=True, copy=False, string="PIN", required=True)
    active = fields.Boolean(default=True)
    name = fields.Char(string="Name", index=True, groups="virsat.group_view_vr_trainee_name", copy=False, required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    vr_game_result_ids = fields.One2many('vr.game.result', 'vr_trainee_id')
    game_sessions_count = fields.Integer(compute="compute_game_sessions_count")
    unit = fields.Char()
    designation = fields.Char()
    driver_for = fields.Char(string="Driver for (L.V/H.V)")
    location = fields.Char()
    language = fields.Selection([('arabic', 'ARABIC'), ('english', 'ENGLISH'), ('hindi', 'HINDI')])
    nationality = fields.Char()
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])
    dob = fields.Date(string="DOB")

    _sql_constraints = [
        ('name_company_uniq', 'unique(name,company_id)', 'Trainee Name already exist in your company.'),
        ('pin_company_uniq', 'unique(pin,company_id)', 'Pin must be unique in your company.'),
    ]

    def unlink(self):
        """Do not allow deletion if there's existing game result connected to the trainee"""
        if self.vr_game_result_ids:
            raise ValidationError("You can't delete trainee that has game history. Archive it instead.")
        res = super().unlink()
        return res

    @api.model
    def create(self, vals):
        """
        Inherit to get a unique pin number. Do not allow if maximum pin size exceeded or if trainee limit exceeded
        """

        # Do not allow if max pin size exceeded
        company = self.env['res.company'].browse(vals.get('company_id'))
        seq_max_size = company.vr_trainee_pin_max_size
        company_pin_records = len(self.search([('company_id', '=', company.id)]))
        reserved_pin_obj = self.env['vr.reserved.pin']
        reserved_pins = reserved_pin_obj.search([('company_id', '=', company.id)]) or []
        total_seq_max_size = seq_max_size - len(reserved_pins)

        if company_pin_records >= total_seq_max_size:
            raise ValidationError("Maximum PIN size exceeded. Please contact administrator.")

        # do not allow if trainee limit count exceeded
        trainee_limit = company.vr_trainee_limit
        if company_pin_records >= trainee_limit:
            raise ValidationError("Maximum trainee limit count exceeded. Please contact administrator.")

        seq_size = company.vr_trainee_pin_size
        pin = self.generate_pin(seq_size)
        exist = self.search([('pin', '=', pin), ('company_id', '=', company.id)]) or (reserved_pins and reserved_pins.filtered(lambda x: x.pin == pin))

        while exist:
            pin = self.generate_pin(seq_size)
            exist = self.search([('pin', '=', pin), ('company_id', '=', company.id)]) or (reserved_pins and reserved_pins.filtered(lambda x: x.pin == pin))

        vals['pin'] = pin

        return super(VrTrainee, self).create(vals)

    def generate_pin(self, length):
        """Generate a random PIN code of given length"""
        pin = ""
        for i in range(length):
            pin += str(random.randint(0, 9))

        return pin

    def compute_game_sessions_count(self):
        self.game_sessions_count = len(self.env['vr.game.sessions'].search([('vr_trainee_id', '=', self.id)]))

    def action_view_game_result(self):
        return {
            'name': 'Game Sessions',
            'type': 'ir.actions.act_window',
            'res_model': 'vr.game.sessions',
            'view_mode': 'tree',
            'domain': [('vr_trainee_id', '=', self.id), ('company_id', '=', self.company_id.id)],
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
