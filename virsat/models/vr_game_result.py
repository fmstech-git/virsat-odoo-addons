# -*- coding: utf-8 -*-
from odoo import fields, models, api


class VrGameResult(models.Model):
    _name = "vr.game.result"
    _description = "VR Game Result"

    name = fields.Char(string="PIN")
    company_id = fields.Many2one('res.company', compute='get_company', store=True)
    vr_trainee_id = fields.Many2one('vr.trainee', compute='get_vr_trainee', string="Trainee", store=True)
    device_id = fields.Char()
    app_version = fields.Char()
    experience = fields.Char()
    game_code = fields.Char()
    vr_game_id = fields.Many2one('vr.games', compute="get_vr_game", string="Game", store=True)
    level_code = fields.Char()
    game_level_id = fields.Many2one('vr.game.levels', compute="get_vr_game_level", string="Game Level", store=True)
    session_start = fields.Datetime()
    session_end = fields.Datetime()
    domain = fields.Char()
    replay = fields.Char()
    violation = fields.Char()
    reaction_time = fields.Datetime()
    selection = fields.Char()
    sub_selection = fields.Char()
    # result = fields.Char()
    # score = fields.Integer()
    gaze_point = fields.Char()
    view_count = fields.Integer()
    view_time = fields.Datetime()
    vr_mail_id = fields.Many2one('virsat.vr.mails')
    attachment_id = fields.Many2one('ir.attachment')
    company_code = fields.Char()
    status = fields.Selection([("pass", "Passed"), ('fail', 'Failed')], store=True)

    # @api.depends('level_code', 'score', 'game_level_id.passing_score')
    # def compute_status(self):
    #     for r in self:
    #         passing_score = r.game_level_id.passing_score
    #         if passing_score and r.score >= passing_score:
    #             r.status = 'pass'
    #         else:
    #             r.status = 'fail'

    @api.depends('name')
    def get_vr_trainee(self):
        for r in self:
            if r.company_id:
                r.vr_trainee_id = self.env['vr.trainee'].search([('pin', '=', r.name), ('company_id', '=', r.company_id.id)]) or False

    @api.depends('game_code')
    def get_vr_game(self):
        for r in self:
            if r.company_id:
                r.vr_game_id = self.env['vr.games'].search([('code', '=', r.game_code), ('company_id', '=', r.company_id.id)]) or False

    @api.depends('level_code')
    def get_vr_game_level(self):
        for r in self:
            if r.game_code:
                r.game_level_id = self.env['vr.game.levels'].search([('code', '=', r.level_code), ('game_id', '=', r.vr_game_id.id)]) or False

    @api.depends('company_code')
    def get_company(self):
        for r in self:
            r.company_id = self.env['res.company'].search([('company_code', '=', r.company_code)]) or False
