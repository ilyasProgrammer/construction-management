# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class ScheduleOfProductionJobs(models.Model):
    _name = 'bm.spj'
    _description = 'Schedule Of Production Jobs'

    name = fields.Char()
    project_id = fields.Many2one('bm.project', string='Проект')
    estimate_ids = fields.One2many('bm.estimate', 'spj_id', string='Сметы')
    currency_id = fields.Many2one('res.currency', string='Валюта', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    amount_labor = fields.Float(string='План трудозатраты')
    amount_mech = fields.Float(string='План мех. часы')
    amount_est_cost = fields.Float(string='План стоимость')
    type = fields.Selection([('external', 'Внешний'),
                             ('local', 'Внутренний'),
                             ], 'Тип', default='local')
    state = fields.Selection([('draft', 'Черновик'),
                              ('approved', 'Утвержден'),
                              ('current', 'Текущий'),
                              ('canceled', 'Отменен'),
                              ], 'Статус', readonly=True, default='draft')

    @api.model
    def create(self, vals):
        type = 'внутренний' if str(vals['type']) == 'local' else 'внешний'
        if vals.get('project_id', False):
            vals['name'] = "ГПР " + type  # + " от " + self.env['bm.project'].browse(vals['project_id']).name
        else:
            vals['name'] = "ГПР " + type
        result = super(ScheduleOfProductionJobs, self).create(vals)
        return result
