# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Report(models.Model):
    _name = 'bm.report'
    _description = 'Отчет о работе'

    date = fields.Datetime(string='Дата завершения', help='Дата подтверждения завершения задания прорабом')
    foremen_id = fields.Many2one('hr.employee', string='Прораб', required=True, domain=lambda self: [('id', 'in', self.project_id.foremen_ids)])
    task_id = fields.Many2one('project.task')
    bm_project_id = fields.Many2one(related='task_id.bm_project_id', string='Проект')
    attachment_ids = fields.Many2many('ir.attachment', string='Вложения')
    estimate_ids = fields.One2many('bm.report.lines', 'report_id', string='Расценки')
    state = fields.Selection([('draft', 'Черновик'),
                              ('sent', 'Отправлено'),
                              ('approved', 'Утверждено'),
                              ('done', 'Завершено'),
                              ], 'Статус', readonly=True, default='draft')
    

class ReportLines(models.Model):
    _name = 'bm.report.lines'
    _description = 'Строка отчета (расценка)'

    report_id = fields.Many2one('bm.report')
    pricing_id = fields.Many2one('bm.pricing', string='Расценка')
    labor = fields.Float(string='Трудозатраты')
    mech = fields.Float(string='Механические часы')
    est_cost = fields.Float(string='Сметная стоимость')
