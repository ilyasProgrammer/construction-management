# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Pricing(models.Model):
    _name = 'bm.pricing'
    _description = 'Pricing'

    name = fields.Char(string='Job', required=True)
    rationale = fields.Char(string='Rationale')
    code = fields.Char(string='Code', required=True)
    pricing_uom = fields.Many2one('product.uom', string='Unit of measure', required=True)
    labor_cost = fields.Float(string='Labor cost', required=True, help='Стоимость часа работ')
    mech_cost = fields.Float(string='Mech. cost', help='Стоимость машинного часа')
    labor_vol = fields.Float(string='Labor volume', help='Объем работ')
    mech_vol = fields.Float(string='Mech. volume', help='Объем машинных работ')
