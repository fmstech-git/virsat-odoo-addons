# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VrGameResultReport(models.Model):
    _name = "vr.game.result.report"
    _description = "VR Game Result Report"
    _auto = False
    _rec_name = 'pin'
    _order = 'id desc'

    trainee_id = fields.Many2one('vr.trainee', readonly=True, string="Trainee PIN")
    pin = fields.Char(string="PIN", readonly=True)
    trainee_name = fields.Char(readonly=True, groups="virsat.group_view_vr_trainee_name")
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    game_session_id = fields.Many2one('vr.game.sessions', readonly=True)
    game_id = fields.Many2one('vr.games', string="Training Module", readonly=True)
    # game_level_id = fields.Many2one('vr.game.levels', string="Level", readonly=True)
    session_start = fields.Datetime(readonly=True)
    session_end = fields.Datetime(readonly=True)
    score = fields.Integer(readonly=True)
    # violation = fields.Char(string="Challenge")
    challenge_id = fields.Many2one('vr.game.challenges', readonly=True)
    challenge_code = fields.Char(readonly=True)
    selection = fields.Char(readonly=True)
    # passing_score = fields.Integer()
    # status = fields.Selection([("passed", "Passed"), ('failed', 'Failed')], readonly=True)
    remark = fields.Char(string="Remark", readonly=True)
    language = fields.Char(readonly=True)
    status = fields.Selection([("passed", "Passed"), ('failed', 'Failed')], readonly=True)

    _depends = {
        'vr.game.result': ['name'],
        'vr.trainee': ['name'],
    }

    @property
    def _table_query(self):
        return '%s %s %s' % (self._select(), self._from(), self._where())

    @api.model
    def _select(self):
        return '''
            SELECT
                line.id,
                trainee.name as trainee_name,
                line.vr_trainee_id as trainee_id,
                line.name as pin,
                line.company_id,
                line.game_session_id,
                line.vr_game_id as game_id,
                line.session_start,
                line.session_end,
                line.score,
                line.game_challenge_id as challenge_id,
                line.challenge_code,
                line.selection,
                line.domain as language,
                session.status,
                line.remark
        '''

    @api.model
    def _from(self):
        return '''
            FROM vr_game_result line
            LEFT JOIN vr_trainee trainee ON trainee.id = line.vr_trainee_id
            LEFT JOIN vr_game_sessions session ON session.id = line.game_session_id
            LEFT JOIN vr_game_challenges challenge ON challenge.id = line.game_challenge_id and challenge.game_id = line.vr_game_id
        '''

    @api.model
    def _where(self):
        return '''
            WHERE line.name IS NOT NULL
        '''
