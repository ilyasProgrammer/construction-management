# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Estimate(models.Model):
    _name = 'bm.estimate'
    _description = 'Смета'

    name = fields.Char(string='Название', required=True)
    project_id = fields.Many2one('project', string='Проект')
    contract_id = fields.Many2one('project', string='Договор')
    spj_id = fields.Many2one('bm.spj', string='ГПР')
    partner_id = fields.Many2one('res.partner', string='Заказчик', required=True)
    contractor_id = fields.Many2one('res.partner', string='Подрядчик', required=True)
    pricing_ids = fields.One2many('bm.estimate.lines', 'estimate_id', string='Расценки')
    attachment_ids = fields.Many2many('ir.attachment', string='Вложения')
    type = fields.Selection(related='contract_id.type')
    currency_id = fields.Many2one(related='contract_id.currency_id')
    overheads = fields.Float(string='Накладные расходы')
    comment = fields.Char(string='Комментарий')


class EstimateLines(models.Model):
    _name = 'bm.estimate.lines'
    _description = 'Строки расценок в смете'

    estimate_id = fields.Many2one('bm.estimate')
    pricing_id = fields.Many2one('bm.pricing', string='Расценка')
    labor = fields.Float(string='Трудозатраты')
    mech = fields.Float(string='Механические часы')
    est_cost = fields.Float(string='Сметная стоимость')
