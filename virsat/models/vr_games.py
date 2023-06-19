# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime


class VrGame(models.Model):
    _name = "vr.games"
    _inherit = ['mail.thread']
    _description = "VR Game"

    name = fields.Char(string="Training Module")
    code = fields.Char(tracking=True, required=True)
    description = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    levels_count = fields.Integer(compute='compute_level_count')
    compute_status = fields.Selection([('percentage', 'Percentage'), ('score', 'Score')], default='percentage', tracking=True)
    compute_status_qty = fields.Float(string="Compute Quantity", default=100, tracking=True)

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
    game_id = fields.Many2one("vr.games", string="Training Module")

    _sql_constraints = [
        ('code_game_uniq', 'unique(code,game_id)', 'Level code must be unique per game.'),
    ]


class VrGameSessions(models.Model):
    _name = "vr.game.sessions"
    _inherit = ['mail.thread']
    _description = "VR Game Sessions"
    _order = 'id desc'

    name = fields.Char(string='PIN', tracking=True)
    company_id = fields.Many2one('res.company', compute='get_company', store=True)
    company_code = fields.Char(tracking=True)
    vr_trainee_id = fields.Many2one('vr.trainee', compute='get_vr_trainee', string="Trainee", store=True)
    session_start_str = fields.Char(string="Session Start")
    session_start = fields.Datetime(compute="compute_session_start", store=True, tracking=True)
    session_end_str = fields.Char(string="Session End")
    session_end = fields.Datetime(compute="compute_session_end", store=True, tracking=True)
    game_id = fields.Many2one('vr.games', string="Training Module", tracking=True)
    game_result_ids = fields.One2many('vr.game.result', 'game_session_id', readonly=True)
    vr_mail_id = fields.Many2one('virsat.vr.mails')
    status = fields.Selection([("passed", "Passed"), ('failed', 'Failed')], compute="compute_status", store=True, tracking=True)

    @api.depends('session_start_str')
    def compute_session_start(self):
        for result in self:
            try:
                result.session_start = datetime.strptime(result.session_start_str, '%Y/%m/%d %H:%M:%S')
            except:
                try:
                    result.session_start = datetime.strptime(result.session_start_str, '%Y/%m/%d %H:%M')
                except:
                    result.session_start = False

    @api.depends('session_end_str')
    def compute_session_end(self):
        for result in self:
            try:
                result.session_end = datetime.strptime(result.session_end_str, '%Y/%m/%d %H:%M:%S')
            except:
                try:
                    result.session_end = datetime.strptime(result.session_end_str, '%Y/%m/%d %H:%M')
                except:
                    result.session_end = False

    @api.depends('game_result_ids.remark')
    def compute_status(self):
        for res in self:
            # remark = res.game_result_ids.mapped('remark')
            # res.status = 'failed' if any(s in ('Incorrect', 'Failed') for s in remark) else 'passed'

            passing = res.game_id.compute_status_qty
            if res.game_id.compute_status == 'score':
                total_score = 0
                level_scores = {}
                for g in res.game_result_ids:
                    if g.level_code not in level_scores:
                        level_scores[g.level_code] = []
                    level_scores[g.level_code] += [g.score]
                for k, v in level_scores.items():
                    total_score += max(v)
                res.status = 'passed' if total_score >= passing else 'failed'
            else:
                unique_violation = res.game_result_ids.mapped('violation')
                correct = res.game_result_ids.filtered(lambda g: g.remark.lower() in ('passed', 'correct')).mapped('remark')
                res.status = 'passed' if (len(correct) / len(set(unique_violation))) * 100 >= passing else 'failed'

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
