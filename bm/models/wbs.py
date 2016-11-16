# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class WBS(models.Model):
    _name = 'bm.wbs'
    _description = 'Иерархическая структура работ'

    code = fields.Char(string='Код')
    name = fields.Char(string='Имя', required=True)
    description = fields.Char(string='Описание', required=True)
    parent_id = fields.Many2one('bm.wbs', string='Родитель', required=True)
    children_ids = fields.One2many('bm.wbs', 'id', string='Потомки')
