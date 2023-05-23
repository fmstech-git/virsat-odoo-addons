# -*- coding: utf-8 -*-
from odoo import fields, models, api


class VrGame(models.Model):
    _name = "vr.games"
    _description = "VR Game"

    name = fields.Char()
    code = fields.Char()
    description = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    levels_count = fields.Integer(compute='compute_level_count')

    _sql_constraints = [
        ('code_company_uniq', 'unique(code,company_id)', 'Game code must be unique per company.'),
    ]

    def compute_level_count(self):
        for rec in self:
            rec.levels_count = len(self.env['vr.game.levels'].search([('game_id', '=', rec.id)]))

    def action_view_game_levels(self):
        return {
            'name': 'Game Levels',
            'type': 'ir.actions.act_window',
            'res_model': 'vr.game.levels',
            'view_mode': 'tree,form',
            'domain': [('game_id', '=', self.id)],
            'context': {'default_game_id': self.id},
        }


class VrGameLevels(models.Model):
    _name = "vr.game.levels"
    _description = "VR Game Levels"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    passing_score = fields.Integer(default=1)
    game_id = fields.Many2one("vr.games")

    _sql_constraints = [
        ('code_game_uniq', 'unique(code,game_id)', 'Level code must be unique per game.'),
    ]
