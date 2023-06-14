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


class VrGameSessions(models.Model):
    _name = "vr.game.sessions"
    _description = "VR Game Sessions"
    _order = 'id desc'

    name = fields.Char(string='PIN')
    company_id = fields.Many2one('res.company', compute='get_company', store=True)
    company_code = fields.Char()
    vr_trainee_id = fields.Many2one('vr.trainee', compute='get_vr_trainee', string="Trainee", store=True)
    session_start_str = fields.Char(string="Session Start")
    session_end_str = fields.Char(string="Session End")
    game_result_ids = fields.One2many('vr.game.result', 'game_session_id')
    vr_mail_id = fields.Many2one('virsat.vr.mails')
    status = fields.Selection([("passed", "Passed"), ('failed', 'Failed')], compute="compute_status", store=True)

    @api.depends('game_result_ids.remark')
    def compute_status(self):
        for res in self:
            remark = res.game_result_ids.mapped('remark')
            res.status = 'failed' if any(s in ('Incorrect', 'Failed') for s in remark) else 'passed'

    @api.depends('company_code')
    def get_company(self):
        for res in self:
            res.company_id = self.env['res.company'].search([('company_code', '=', res.company_code)]) or False

    @api.depends('name', 'company_id')
    def get_vr_trainee(self):
        for res in self:
            if res.company_id:
                res.vr_trainee_id = self.env['vr.trainee'].search(
                    [('pin', '=', res.name), ('company_id', '=', res.company_id.id)]) or False

    def action_view_result(self):
        return {
            'name': 'Game Result',
            'type': 'ir.actions.act_window',
            'res_model': 'vr.game.result.report',
            'view_mode': 'kanban,tree',
            'domain': [('game_session_id', '=', self.id)],
        }
