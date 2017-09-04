# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'project.project'
    _description = 'Contract'

    bm_project_id = fields.Many2one('bm.project', string='Проект')  # нужно для домена поля wbs_id в форме задания
