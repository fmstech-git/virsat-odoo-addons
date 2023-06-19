# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime

class VrGameResult(models.Model):
    _name = "vr.game.result"
    _inherit = ['mail.thread']
    _description = "VR Game Result"
    _order = 'id desc'

    name = fields.Char(string="PIN", tracking=True)
    company_id = fields.Many2one('res.company', compute='get_company', store=True)
    company_code = fields.Char(tracking=True)
    vr_trainee_id = fields.Many2one('vr.trainee', compute='get_vr_trainee', string="Trainee", store=True)
    device_id = fields.Char()
    app_version = fields.Char()
    experience = fields.Char()
    game_code = fields.Char(tracking=True)
    vr_game_id = fields.Many2one('vr.games', compute="get_vr_game", string="Game", store=True)
    level_code = fields.Char(tracking=True)
    game_level_id = fields.Many2one('vr.game.levels', compute="get_vr_game_level", string="Game Level", store=True)
    session_id = fields.Char()
    game_session_id = fields.Many2one('vr.game.sessions')
    session_start = fields.Datetime(compute="compute_session_start", store=True, tracking=True)
    session_start_str = fields.Char()
    session_end = fields.Datetime(compute="compute_session_end", store=True, tracking=True)
    session_end_str = fields.Char()
    domain = fields.Char()
    replay = fields.Char()
    violation = fields.Char(string="Challenge")
    selection = fields.Char()
    sub_selection = fields.Char()
    gaze_point = fields.Char()
    view_count = fields.Char()
    reaction_time_str = fields.Char(string="Reaction Time")
    view_time_str = fields.Char(string="View Time")
    vr_mail_id = fields.Many2one('virsat.vr.mails', string="VR Mail", tracking=True)
    attachment_id = fields.Many2one('ir.attachment')
    score = fields.Integer(compute="compute_score", store=True, tracking=True)
    score_str = fields.Char()
    remark = fields.Char(string='Status', tracking=True)

    @api.depends('score_str')
    def compute_score(self):
        for result in self:
            try:
                result.score = int(float(result.score_str))
            except:
                result.score = 0

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

    @api.depends('name', 'company_id')
    def get_vr_trainee(self):
        for result in self:
            if result.company_id:
                result.vr_trainee_id = self.env['vr.trainee'].search(
                    [('pin', '=', result.name), ('company_id', '=', result.company_id.id)]) or False

    @api.depends('game_code', 'company_id')
    def get_vr_game(self):
        for result in self:
            if result.company_id:
                result.vr_game_id = self.env['vr.games'].search(
                    [('code', '=', result.game_code), ('company_id', '=', result.company_id.id)]) or False

    @api.depends('level_code', 'company_id')
    def get_vr_game_level(self):
        for result in self:
            if result.game_code:
                result.game_level_id = self.env['vr.game.levels'].search(
                    [('code', '=', result.level_code), ('game_id', '=', result.vr_game_id.id)]) or False

    @api.depends('company_code')
    def get_company(self):
        for result in self:
            result.company_id = self.env['res.company'].search([('company_code', '=', result.company_code)]) or False
