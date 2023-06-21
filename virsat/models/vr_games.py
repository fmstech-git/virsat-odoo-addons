# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError


class VrGame(models.Model):
    _name = "vr.games"
    _inherit = ['mail.thread']
    _description = "VR Game"
    _order = 'name asc'

    name = fields.Char(string="Training Module")
    code = fields.Char(tracking=True, required=True)
    description = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    # levels_count = fields.Integer(compute='compute_level_count')
    challenges_count = fields.Integer(compute='compute_challenges_count')
    status_compute_type = fields.Selection([('percentage', 'Percentage'), ('score', 'Score')], default='percentage', tracking=True)
    status_compute_qty = fields.Float(string="Compute Quantity", default=100, tracking=True)

    # _sql_constraints = [
    #     ('code_company_uniq', 'unique(code,company_id)', 'Game code must be unique.'),
    # ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            code = vals.get('code')
            company_id = vals.get('company_id')
            if code or company_id:
                exist = self.search([('code', '=', code), ('company_id', '!=', company_id)])
                if exist:
                    raise ValidationError("Game code already exist in other company. Please use another code.")
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('code') or vals.get('company_id'):
            code = vals.get('code') or self.code
            company_id = vals.get('company_id') or self.company_id.id
            exist = self.search([('code', '=', code), ('company_id', '!=', company_id)])
            if exist:
                raise ValidationError("Game code already exist. Please use another code.")

        return super(VrGame, self).write(vals)

    def compute_challenges_count(self):
        for rec in self:
            rec.challenges_count = len(self.env['vr.game.challenges'].search([('game_id', '=', rec.id)]))

    def action_view_game_challenges(self):
        return {
            'name': 'Game Challenges',
            'type': 'ir.actions.act_window',
            'res_model': 'vr.game.challenges',
            'view_mode': 'tree',
            'domain': [('game_id', '=', self.id)],
            'context': {'default_game_id': self.id},
        }

    # def compute_level_count(self):
    #     for rec in self:
    #         rec.levels_count = len(self.env['vr.game.levels'].search([('game_id', '=', rec.id)]))
    #
    # def action_view_game_levels(self):
    #     return {
    #         'name': 'Game Levels',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'vr.game.levels',
    #         'view_mode': 'tree,form',
    #         'domain': [('game_id', '=', self.id)],
    #         'context': {'default_game_id': self.id},
    #     }


# class VrGameLevels(models.Model):
#     _name = "vr.game.levels"
#     _description = "VR Game Levels"
#
#     name = fields.Char(required=True)
#     code = fields.Char(required=True)
#     passing_score = fields.Integer(default=1)
#     game_id = fields.Many2one("vr.games", string="Training Module")
#
#     _sql_constraints = [
#         ('code_game_uniq', 'unique(code,game_id)', 'Level code must be unique per game.'),
#     ]


class VrGameChallenges(models.Model):
    _name = "vr.game.challenges"
    _description = "VR Game Challenges"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    game_id = fields.Many2one("vr.games", string="Training Module")
    game_code = fields.Char(related="game_id.code")

    _sql_constraints = [
        ('code_game_uniq', 'unique(code,game_id)', 'Challenge code must be unique per game.'),
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
    session_start_str = fields.Char()
    session_start = fields.Datetime(compute="compute_session_start", store=True, tracking=True)
    session_end_str = fields.Char()
    session_end = fields.Datetime(compute="compute_session_end", store=True, tracking=True)
    game_id = fields.Many2one('vr.games', string="Training Module", tracking=True)
    game_result_ids = fields.One2many('vr.game.result', 'game_session_id', readonly=True)
    vr_mail_id = fields.Many2one('virsat.vr.mails')
    status = fields.Selection([("passed", "Passed"), ('failed', 'Failed')], tracking=True, readonly=True)
    status_compute_type = fields.Selection([('percentage', 'Percentage'), ('score', 'Score')], default='percentage', tracking=True)
    status_compute_qty = fields.Float(tracking=True)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Hide not needed fields in filter and group by"""
        hide = {'message_partner_ids', 'message_needaction_counter',
                'company_id', 'session_start_str', 'message_main_attachment_id', 'has_message', 'message_needaction',
                'message_has_error', 'vr_mail_id', 'message_has_sms_error', 'message_attachment_count',
                'company_code', 'name', 'game_result_ids', 'message_ids', 'session_end_str',
                'message_follower_ids', 'message_has_error_counter', 'write_date', 'message_is_follower', 'create_date'}
        res = super().fields_get(allfields, attributes)

        for field in hide:
            if res.get(field):
                res[field]['searchable'] = False
                res[field]['sortable'] = False

        return res


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

    def compute_status(self):
        for res in self:
            # remark = res.game_result_ids.mapped('remark')
            # res.status = 'failed' if any(s in ('Incorrect', 'Failed') for s in remark) else 'passed'

            passing = res.game_id.status_compute_qty
            if res.game_id.status_compute_type == 'score':
                total_score = 0
                challenge_scores = {}
                for g in res.game_result_ids.filtered(lambda g: g.vr_game_id.id == res.game_id.id):
                    if g.challenge_code not in challenge_scores:
                        challenge_scores[g.challenge_code] = []
                    challenge_scores[g.challenge_code] += [g.score]
                for k, v in challenge_scores.items():
                    total_score += max(v)
                res.status = 'passed' if total_score >= passing else 'failed'
            else:
                challenges = self.env['vr.game.challenges'].search([('game_id', '=', res.game_id.id)]) if res.game_id else []
                correct = res.game_result_ids.filtered(lambda g: g.remark.lower() in ('passed', 'correct'))
                res.status = 'passed' if challenges and (len(correct) / len(challenges)) * 100 >= passing else 'failed'

    def action_recompute_status(self):
        self.ensure_one()
        self.compute_status()

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
            'view_mode': 'tree,kanban',
            'domain': [('game_session_id', '=', self.id)],
        }
