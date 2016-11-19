# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'project.project'
    _description = 'Contract'

    bm_project_id = fields.Many2one('bm.project', string='Проект')
    foremen_ids = fields.Many2many('hr.employee', string='Прорабы')
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    start = fields.Date(string='Старт')
    finish = fields.Date(string='Финиш')
    code = fields.Char(string='Код', required=True)
    partner_id = fields.Many2one('res.partner', string='Заказчик', required=True)
    contractor_id = fields.Many2one('res.partner', string='Подрядчик', required=True)
    estimate_ids = fields.One2many('bm.estimate', 'contract_id', string='Сметы')
    rate = fields.Float(string='Курс', required=True)
    amount = fields.Float(string='Сумма')
    subject = fields.Text(string='Предмет')
    type = fields.Selection([('revenue', 'Выручка'),
                             ('expense', 'Затраты'),
                             ], 'Статус', default='revenue')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([('draft', 'Черновик'),
                              ('signed', 'Подписан'),
                              ('canceled', 'Отменен'),
                              ], 'Статус', readonly=True, default='draft')
    hide_rate = fields.Boolean(compute='_compute_vision', store=True, default=True)
    # tasks_ids - in parent model

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
