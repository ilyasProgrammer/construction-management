# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Project(models.Model):
    _name = 'bm.project'
    _inherit = 'project.project'
    _description = 'Project'

    wbs_id = fields.Many2one('bm.wbs', string='WBS Root')
    external_spj_id = fields.One2many('bm.spj', 'project_external_id', string='External SPJ')
    local_spj_id = fields.One2many('bm.spj', 'project_local_id', string='Local SPJ')
    full_name = fields.Char(string='Full name', required=True)
    address = fields.Char(string='Address')
    code = fields.Char(string='Object code')
    engineer_id = fields.Many2one('hr.employee', string='Engineer', required=True)
    foremen_ids = fields.Many2many('hr.employee', string='Foremen', required=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    partner_id = fields.Boolean()  # mask
    state = fields.Selection([('tender', 'Тендер'),
                              ('in_work', 'В работе'),
                              ('done', 'Звершен'),
                              ('frozen', 'Заморожен'),
                              ('archived', 'Архив'),
                              ], 'Статус', readonly=True, default='tender')
