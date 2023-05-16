# -*- coding: utf-8 -*-
from odoo import models


class VrGameResultXlsx(models.AbstractModel):
    _name = 'report.virsat.vr_game_result_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, game_result):
        row = 0
        sheet = workbook.add_worksheet("Game Result")
        for game in game_result:
            # bold = workbook.add_format({'bold': True})
            sheet.write(row, 0, game.trainee_id.pin)
            sheet.write(row, 1, game.game_id.name)
            row += 1
