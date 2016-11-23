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
    date = fields.Date(string='Дата задания', default=fields.Date.context_today)
    stage_id = fields.Many2one('project.task.type', 'Stage', select=True, copy=False, default=_get_stage)
    start = fields.Date(string='Старт', default=fields.Date.context_today)
    finish = fields.Date(string='Финиш')
    engineer_id = fields.Many2one('hr.employee', string='Инженер')
    pricing_ids = fields.One2many('project.pricing.lines', 'task_id', string='Расценки')
    report_ids = fields.One2many('bm.report', 'task_id', string='Отчеты')
    total_reports_amount = fields.Integer(string='Отчетов всего', compute='_compute_counts', store=True)
    # договор - это project_id в родной модели

    @api.model
    def create(self, vals):
        vals['name'] = 'Task from ' + vals['date'] + ' number ' + vals['code']
        result = super(Task, self).create(vals)
        return result

    @api.multi
    @api.depends('report_ids')
    def _compute_counts(self):
        for rec in self:
            rec.total_reports_amount = len(rec.report_ids)
        all_proj = self.env['project.project'].search([])
        for rec in all_proj:
            rec.total_tasks_amount = len(rec.task_ids)
            rec.total_reports_amount = len(self.env['bm.report'].search([('task_id', 'in', rec.task_ids.ids)]))
        all_bm_proj = self.env['bm.project'].search([])
        for proj in all_bm_proj:
            if len(proj.contracts_ids):
                proj_tasks = self.env['project.task'].search([('project_id', 'in', proj.contracts_ids.ids)])
                proj.total_tasks_amount = len(proj_tasks)
                proj_reports = self.env['bm.report'].search([('task_id', 'in', proj_tasks.ids)])
                proj.total_reports_amount = len(proj_reports)


class PricingLines(models.Model):
    _name = 'project.pricing.lines'
    _description = 'Task line (estimate)'

    task_id = fields.Many2one('project.task')
    sequence = fields.Integer()
    bm_project_id = fields.Many2one(related='task_id.project_id.bm_project_id')
    wbs_id = fields.Many2one('bm.wbs', string='WBS')
    pricing_id = fields.Many2one('bm.pricing', string='Расценка')
    code = fields.Char(related='pricing_id.code', string='Код', readonly=True)
    name = fields.Char(related='pricing_id.name', string='Имя', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', string='Основание', readonly=True)
    pricing_uom = fields.Many2one(related='pricing_id.pricing_uom', string='Ед. изм.', readonly=True)
    # plan_amount = fields.Float(string='План. колич.', required=True)
    # plan_labor = fields.Float(string='План. труд.', required=True)
    # plan_mech = fields.Float(string='План. маш.', required=True)
    amount = fields.Float(string='Кол-во', required=True)
    labor_cost = fields.Float(string='Цена часа работы', help='Стоимость часа работ')
    mech_cost = fields.Float(string='Цена машинного часа', help='Стоимость машинного часа')
    labor_vol = fields.Float(string='Количество работы', help='Объем работ')
    mech_vol = fields.Float(string='Количество машинных часов', help='Объем машинных работ')
    comment = fields.Text(string='Комментарий')

    @api.v8
    @api.onchange('pricing_id')
    def on_change_pricing_id(self):
        if not self.pricing_id:
            return {}
        self.labor_cost = self.pricing_id.labor_cost
        self.mech_cost = self.pricing_id.mech_cost
        self.labor_vol = self.pricing_id.labor_vol
        self.mech_vol = self.pricing_id.mech_vol