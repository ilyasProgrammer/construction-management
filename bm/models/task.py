# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Task(models.Model):
    _inherit = 'project.task'
    _description = 'Задание'

    code = fields.Char(string='Номер')
    date = fields.Datetime(string='Дата задания')
    start = fields.Date(string='Дата начала работ')
    finish = fields.Date(string='Дата окончания работ')
    foremen_id = fields.Many2one('hr.employee', string='Прораб', domain=lambda self: [('id', 'in', self.project_id.foremen_ids)])
    engineer_id = fields.Many2one('hr.employee', string='Инженер')
    estimate_ids = fields.One2many('project.task.lines', 'task_id', string='Расценки')
    # договор - это project_id в родной модели
    report_ids = fields.One2many('bm.report', 'task_id', string='Отчеты')
    state = fields.Selection([('draft', 'Черновик'),
                              ('wait_begin', 'Ожидает начала работ'),
                              ('in_work', 'В работе'),
                              ('wait_decision', 'Ожидает решения инженера'),
                              ('done', 'Завершено'),
                              ('canceled', 'Отменено'),
                              ], 'Статус', readonly=True, default='draft')


class TaskLines(models.Model):
    _name = 'project.task.lines'
    _description = 'Строка задания (расценка)'

    task_id = fields.Many2one('project.task')
    pricing_id = fields.Many2one('bm.pricing', string='Расценка')
    labor = fields.Float(string='Трудозатраты')
    mech = fields.Float(string='Механические часы')
    est_cost = fields.Float(string='Сметная стоимость')
