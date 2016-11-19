# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Task(models.Model):
    _inherit = 'project.task'
    _description = 'Task'

    @api.model
    def _get_stage(self):
        stage_id = self.env['project.task.type'].search([('name','=','Draft')])[0]
        return stage_id

    code = fields.Char(string='Номер задания', required=True)
    date = fields.Date(string='Дата', default=fields.Date.context_today)
    stage_id = fields.Many2one('project.task.type', 'Stage', select=True, copy=False, default=_get_stage)
    start = fields.Date(string='Старт', default=fields.Date.context_today)
    finish = fields.Date(string='Финиш')
    engineer_id = fields.Many2one('hr.employee', string='Инженер')
    pricing_ids = fields.One2many('project.pricing.lines', 'task_id', string='Расценки')
    report_ids = fields.One2many('bm.report', 'task_id', string='Отчеты')
    # договор - это project_id в родной модели

    @api.model
    def create(self, vals):
        vals['name'] = "Задание " + str(vals['code']) + " от " + str(vals['date'])
        result = super(Task, self).create(vals)
        return result


class PricingLines(models.Model):
    _name = 'project.pricing.lines'
    _description = 'Task line (estimate)'

    task_id = fields.Many2one('project.task')
    pricing_id = fields.Many2one('bm.pricing', string='Расценка')
    code = fields.Char(related='pricing_id.code', string='Код', readonly=True)
    name = fields.Char(related='pricing_id.name', string='Имя', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', string='Основание', readonly=True)
    pricing_uom = fields.Many2one(related='pricing_id.pricing_uom', string='Ед. изм.', readonly=True)
    labor_cost = fields.Float(string='Цена часа работы', help='Стоимость часа работ')
    mech_cost = fields.Float(string='Цена машинного часа', help='Стоимость машинного часа')
    labor_vol = fields.Float(string='Количество работы', help='Объем работ')
    mech_vol = fields.Float(string='Количество машинных часов', help='Объем машинных работ')

    @api.v8
    @api.onchange('pricing_id')
    def on_change_pricing_id(self):
        if not self.pricing_id:
            return {}
        self.labor_cost = self.pricing_id.labor_cost
        self.mech_cost = self.pricing_id.mech_cost
        self.labor_vol = self.pricing_id.labor_vol
        self.mech_vol = self.pricing_id.mech_vol