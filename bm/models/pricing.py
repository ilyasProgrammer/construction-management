# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Pricing(models.Model):
    _name = 'bm.pricing'
    _description = 'Pricing'

    name = fields.Char(string='Работа', required=True)
    rationale = fields.Char(string='Обоснование')
    code = fields.Char(string='Код', required=True)
    pricing_uom = fields.Many2one('product.uom', string='Ед. изм.', required=True)
    labor_cost = fields.Float(string='Стоимость чел. часа', required=True, help='Стоимость часа работ')
    mech_cost = fields.Float(string='Стоимость маш. часа', help='Стоимость машинного часа')
    labor_vol = fields.Float(string='Кол-во чел. часов', help='Объем работ')
    mech_vol = fields.Float(string='Кол-во мех. часов', help='Объем машинных работ')
