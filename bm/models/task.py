# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Task(models.Model):
    _inherit = 'project.task'
    _description = 'Task'

    code = fields.Char(string='Number')
    date = fields.Datetime(string='Task date')
    start = fields.Date(string='Start date')
    finish = fields.Date(string='Finish date')
    engineer_id = fields.Many2one('hr.employee', string='Engineer')
    estimate_ids = fields.One2many('project.task.lines', 'task_id', string='Estimates')
    # договор - это project_id в родной модели
    report_ids = fields.One2many('bm.report', 'task_id', string='Reports')


class TaskLines(models.Model):
    _name = 'project.task.lines'
    _description = 'Task line (estimate)'

    task_id = fields.Many2one('project.task')
    pricing_id = fields.Many2one('bm.pricing', string='Estimate')
    labor = fields.Float(string='Labor')
    mech = fields.Float(string='Mechanical hours')
    est_cost = fields.Float(string='Estimation cost')
