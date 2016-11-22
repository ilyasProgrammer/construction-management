# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Project(models.Model):
    _name = 'bm.project'
    _inherit = 'project.project'
    _description = 'Project'

    wbs_ids = fields.One2many('bm.wbs', 'bm_project_id', string='ИСР')
    external_spj_id = fields.One2many('bm.spj', 'project_id', string='Внешний ГПР')
    local_spj_id = fields.One2many('bm.spj', 'project_id', string='Внутренний ГПР')
    full_name = fields.Char(string='Полное имя', required=True)
    address = fields.Char(string='Адрес')
    code = fields.Char(string='Код объекта')
    engineer_id = fields.Many2one('hr.employee', string='Инженер', required=True)
    foremen_ids = fields.Many2many('hr.employee', string='Прораб', required=True)
    partner_id = fields.Many2one('res.partner', string='Заказчик', required=True)
    contractor_id = fields.Many2one('res.partner', string='Подрядчик', required=True)
    state = fields.Selection([('tender', 'Тендер'),
                              ('in_work', 'В работе'),
                              ('done', 'Звершен'),
                              ('frozen', 'Заморожен'),
                              ('archived', 'Архив'),
                              ], 'Статус', readonly=True, default='tender')
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'bm.project')],
                                     string='Вложения')
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Номер")

    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['domain'] = ['&', ('res_model', '=', 'bm.project'), ('res_id', 'in', self.ids)]
        return action

    @api.multi
    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'bm.project'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)
