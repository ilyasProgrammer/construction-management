# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'project.project'
    _description = 'Договор'

    bm_project_id = fields.Many2one('bm.project', string='Проект')
    date = fields.Date(string='Дата', required=True)
    start = fields.Date(string='Дата начала работ')
    finish = fields.Date(string='Дата окончания работ')
    code = fields.Char(string='Номер', required=True)
    partner_id = fields.Many2one('res.partner', string='Заказчик', required=True)
    contractor_id = fields.Many2one('res.partner', string='Подрядчик', required=True)
    estimate_ids = fields.One2many('bm.estimate', 'contract_id', string='Сметы')
    rate = fields.Float(string='Курс')
    amount = fields.Float(string='Сумма')
    subject = fields.Char(string='Предмет договора')
    attachment_ids = fields.Many2many('ir.attachment', string='Вложения')
    type = fields.Selection([('revenue', 'Выручка'),
                             ('expense', 'Затраты'),
                             ], 'Статус', readonly=True, default='revenue')
    currency_id = fields.Many2one('res.currency', string='Валюта', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([('draft', 'Черновик'),
                              ('signed', 'Подписан'),
                              ('canceled', 'Отменен'),
                              ], 'Статус', readonly=True, default='draft')
    # tasks_ids - in parent model
