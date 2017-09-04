# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class WBS(models.Model):
    _name = 'bm.wbs'
    _inherit = 'product.category'
    _description = 'The hierarchical structure of work'

    code = fields.Char(string='Код')
    name = fields.Char(string='Название', required=True)
    description = fields.Text(string='Описание', required=True)
    parent_id = fields.Many2one('bm.wbs', 'Родитель', select=True, ondelete='cascade')
    bm_project_id = fields.Many2one('bm.project', string='Проект')
