# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Pricing(models.Model):
    _name = 'bm.pricing'
    _description = 'Расценка'

    rationale = fields.Char(string='Обоснование')
    code = fields.Char(string='Код', required=True)
    job = fields.Char(string='Работа', required=True)
    pricing_uom = fields.Many2one('product.uom', string='Единица измерения', required=True)
    labor = fields.Float(string='Трудозатраты', required=True)
    mech = fields.Float(string='Механические часы')
    est_cost = fields.Float(string='Сметная стоимость')
