# -*- coding: utf-8 -*-
from odoo import fields, models, api


class VrGame(models.Model):
    _name = "vr.games"
    _description = "VR Game"

    name = fields.Char()
    code = fields.Char()
    description = fields.Text()
