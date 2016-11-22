# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'project.project'
    _description = 'Contract'

    bm_project_id = fields.Many2one('bm.project', string='Проект')
    foremen_ids = fields.Many2many('hr.employee', string='Прорабы')
    date = fields.Date(string='Дата', required=True, default=fields.Date.context_today)
    start = fields.Date(string='Старт')
    finish = fields.Date(string='Финиш')
    code = fields.Char(string='Код', required=True)
    partner_id = fields.Many2one('res.partner', string='Заказчик', required=True)
    contractor_id = fields.Many2one('res.partner', string='Подрядчик', required=True)
    estimate_ids = fields.One2many('bm.estimate', 'contract_id', string='Сметы')
    rate = fields.Float(string='Курс', required=True)
    amount = fields.Float(string='Сумма')
    subject = fields.Text(string='Предмет')
    total_tasks_amount = fields.Integer(compute='_compute_amount', store=True)
    total_reports_amount = fields.Integer(compute='_compute_amount', store=True)
    total_estimates_amount = fields.Integer(compute='_compute_amount', store=True)
    type = fields.Selection([('revenue', 'Выручка'),
                             ('expense', 'Затраты'),
                             ], 'Статус', default='revenue')
    currency_id = fields.Many2one('res.currency', string='Валюта', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([('draft', 'Черновик'),
                              ('signed', 'Подписан'),
                              ('canceled', 'Отменен'),
                              ], 'Статус', readonly=True, default='draft')
    hide_rate = fields.Boolean(compute='_compute_vision', store=True, default=True)
    # tasks_ids - in parent model

    @api.multi
    @api.depends('task_ids', 'estimate_ids')
    def _compute_amount(self):
        for rec in self:
            rec.total_tasks_amount = len(rec.task_ids)
            rec.total_reports_amount = len(self.env['bm.report'].search([('task_id', 'in', rec.task_ids.ids)]))
            rec.total_estimates_amount = len(self.env['bm.estimate'].search([('contract_id', '=', rec.id)]))
        all_proj = self.env['bm.project'].search([])
        for proj in all_proj:
            if len(proj.contracts_ids):
                proj_tasks = self.env['project.task'].search([('project_id', 'in', proj.contracts_ids.ids)])
                proj.total_tasks_amount = len(proj_tasks)
                proj_reports = self.env['bm.report'].search([('task_id', 'in', proj_tasks.ids)])
                proj.total_reports_amount = len(proj_reports)

    @api.multi
    @api.depends('currency_id')
    def _compute_vision(self):
        for rec in self:
            basic_currency = self.env.user.company_id.currency_id
            if rec.currency_id == basic_currency:
                rec.hide_rate = True
                rec.rate = 1
            else:
                rec.hide_rate = False


class Project(models.Model):
    _inherit = 'bm.project'

    contracts_ids = fields.One2many('project.project', 'bm_project_id', string='Договоры')
    total_tasks_amount = fields.Integer(compute='_compute_amount', store=True)
    total_reports_amount = fields.Integer(compute='_compute_amount', store=True)

    @api.multi
    @api.depends('contracts_ids', 'contracts_ids.task_ids', 'contracts_ids.task_ids.report_ids')
    def _compute_amount(self):
        for proj in self:
            if len(proj.contracts_ids):
                proj_tasks = self.env['project.task'].search([('project_id', 'in', proj.contracts_ids.ids)])
                proj.total_tasks_amount = len(proj_tasks)
                proj_reports = self.env['bm.report'].search([('task_id', 'in', proj_tasks.ids)])
                proj.total_reports_amount = len(proj_reports)


class Estimate(models.Model):
    _inherit = 'bm.estimate'

    type = fields.Selection(related='contract_id.type', string='Тип')
    partner_id = fields.Many2one(related='contract_id.partner_id', string='Заказчик')
    contractor_id = fields.Many2one(related='contract_id.contractor_id', string='Подрядчик')


class Task(models.Model):
    _inherit = 'project.task'

    bm_project_id = fields.Many2one(related='project_id.bm_project_id', string='Проект')
    foreman_id = fields.Many2one('hr.employee', string='Прораб')  # domain=lambda self: [('id', 'in', self.project_id.foremen_ids)]


class Report(models.Model):
    _inherit = 'bm.report'

    bm_project_id = fields.Many2one(related='task_id.bm_project_id', string='Проект')
