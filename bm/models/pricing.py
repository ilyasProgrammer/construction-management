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
    labor = fields.Float(string='Labor', required=True)
    mech = fields.Float(string='Mechanical hours')
    est_cost = fields.Float(string='Estimation cost')
