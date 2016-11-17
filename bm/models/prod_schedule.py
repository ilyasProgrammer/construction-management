# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class ScheduleOfProductionJobs(models.Model):
    _name = 'bm.spj'
    _description = 'Schedule Of Production Jobs'

    project_local_id = fields.Many2one('bm.project')  # привязка может быть только по одному из этих полей
    project_external_id = fields.Many2one('bm.project')
    estimate_ids = fields.One2many('bm.estimate', 'spj_id', string='Estimates')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    amount_labor = fields.Float(string='Plan labor')
    amount_mech = fields.Float(string='Plan mechanical hours')
    amount_est_cost = fields.Float(string='Plan estimation cost')
    type = fields.Selection([('external', 'Внешний'),
                             ('local', 'Внутренний'),
                             ], 'Статус', readonly=True, default='local')
    state = fields.Selection([('draft', 'Черновик'),
                              ('approved', 'Утвержден'),
                              ('current', 'Текущий'),
                              ('canceled', 'Отменен'),
                              ], 'Статус', readonly=True, default='draft')
