# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class WBS(models.Model):
    _name = 'bm.wbs'
    _inherit = 'product.category'
    _description = 'The hierarchical structure of work'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description', required=True)
    parent_id = fields.Many2one('bm.wbs', 'Parent Category', select=True, ondelete='cascade')
