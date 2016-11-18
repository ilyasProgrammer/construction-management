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

    code = fields.Char(string='Number')
    date = fields.Date(string='Task date')
    stage_id = fields.Many2one('project.task.type', 'Stage', select=True, copy=False, default=_get_stage)
    start = fields.Date(string='Start date')
    finish = fields.Date(string='Finish date')
    engineer_id = fields.Many2one('hr.employee', string='Engineer')
    pricing_ids = fields.One2many('project.pricing.lines', 'task_id', string='Pricings')
    report_ids = fields.One2many('bm.report', 'task_id', string='Reports')
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
    pricing_id = fields.Many2one('bm.pricing', string='Estimate')
    code = fields.Char(related='pricing_id.code', readonly=True)
    name = fields.Char(related='pricing_id.name', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', readonly=True)
    pricing_uom = fields.Many2one(related='pricing_id.pricing_uom', readonly=True)
    labor_cost = fields.Float(string='Labor', help='Стоимость часа работ')
    mech_cost = fields.Float(string='Mech.', help='Стоимость машинного часа')
    labor_vol = fields.Float(string='Labor vol', help='Объем работ')
    mech_vol = fields.Float(string='Mech. vol', help='Объем машинных работ')

    @api.v8
    @api.onchange('pricing_id')
    def on_change_pricing_id(self):
        if not self.pricing_id:
            return {}
        self.labor_cost = self.pricing_id.labor_cost
        self.mech_cost = self.pricing_id.mech_cost
        self.labor_vol = self.pricing_id.labor_vol
        self.mech_vol = self.pricing_id.mech_vol