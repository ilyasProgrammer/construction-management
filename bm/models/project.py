# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Project(models.Model):
    _name = 'bm.project'
    _inherit = 'project.project'
    _description = 'Проект'

    wbs_id = fields.Many2one('bm.wbs', string='Корень ИСР')
    external_spj_id = fields.One2many('bm.spj', 'project_external_id', string='Внешние ГПР')
    local_spj_id = fields.One2many('bm.spj', 'project_local_id', string='Внутренние ГПР')
    full_name = fields.Char(string='Название полное', required=True)
    name = fields.Char(string='Название краткое', required=True)
    address = fields.Char(string='Адрес')
    code = fields.Char(string='Шифр объекта')
    engineer_id = fields.Many2one('hr.employee', string='Инженер', required=True)
    foremen_ids = fields.Many2many('hr.employee', string='Прорабы', required=True)
    contracts_ids = fields.One2many('bm.contract', 'bm_project_id', string='Договоры')
    attachment_ids = fields.Many2many('ir.attachment', string='Вложения')
    state = fields.Selection([('tender', 'Тендер'),
                              ('in_work', 'В работе'),
                              ('done', 'Звершен'),
                              ('frozen', 'Заморожен'),
                              ('archived', 'Архив'),
                              ], 'Статус', readonly=True, default='tender')
