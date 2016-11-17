# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Report(models.Model):
    _name = 'bm.report'
    _description = 'Job report'

    date = fields.Datetime(string='End date', help='Дата подтверждения завершения задания прорабом')
    foremen_id = fields.Many2one('hr.employee', string='Foreman', required=True)  # domain=lambda self: [('id', 'in', self.project_id.foremen_ids)]
    task_id = fields.Many2one('project.task')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    estimate_ids = fields.One2many('bm.report.lines', 'report_id', string='Estimates')
    state = fields.Selection([('draft', 'Черновик'),
                              ('sent', 'Отправлено'),
                              ('approved', 'Утверждено'),
                              ('done', 'Завершено'),
                              ], 'Статус', readonly=True, default='draft')
    

class ReportLines(models.Model):
    _name = 'bm.report.lines'
    _description = 'Report line (estimate)'

    report_id = fields.Many2one('bm.report')
    pricing_id = fields.Many2one('bm.pricing', string='Estimate')
    labor = fields.Float(string='Labor')
    mech = fields.Float(string='Mechanical hours')
    est_cost = fields.Float(string='Estimate cost')
