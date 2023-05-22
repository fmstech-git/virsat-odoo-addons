# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class Virsat(http.Controller):
    @http.route('/virsat/statistics', type='json', auth='user')
    def get_statistics(self):
        cids = request.httprequest.cookies.get('cids', str(request.env.user.company_id.id))
        allowed_company_ids = [int(cid) for cid in cids.split(',')]

        games = request.env['vr.games'].with_context(allowed_company_ids=allowed_company_ids).search([])
        trainees = request.env['vr.trainee'].with_context(allowed_company_ids=allowed_company_ids).search([])
        game_result = request.env['vr.game.result'].with_context(allowed_company_ids=allowed_company_ids).search([])
        game_result_stats = {'Passed': 0, 'Failed': 0}
        for g in game_result:
            game_result_stats['Passed'] += 1 if g.status == 'passed' else 0
            game_result_stats['Failed'] += 1 if g.status == 'failed' else 0

        return {
            "games": len(games),
            "trainees": len(trainees),
            "sessions": len(game_result),
            "sessions_stats": game_result_stats,
        }