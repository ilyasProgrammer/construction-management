# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Report(models.Model):
    _name = 'bm.report'
    _description = 'Job report'

    date = fields.Datetime(string='End date', help='Дата подтверждения завершения задания прорабом')
    foremen_id = fields.Many2one('hr.employee', string='Foreman', required=True)  # domain=lambda self: [('id', 'in', self.project_id.foremen_ids)]
    task_id = fields.Many2one('project.task')
    estimate_ids = fields.One2many('bm.report.lines', 'report_id', string='Estimates')
    state = fields.Selection([('draft', 'Черновик'),
                              ('sent', 'Отправлено'),
                              ('approved', 'Утверждено'),
                              ('done', 'Завершено'),
                              ], 'Статус', readonly=True, default='draft')
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'bm.report')],
                                     string='Attachments')
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")

    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['domain'] = ['&', ('res_model', '=', 'bm.report'), ('res_id', 'in', self.ids)]
        return action

    @api.multi
    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'bm.report'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)


class ReportLines(models.Model):
    _name = 'bm.report.lines'
    _description = 'Report line (estimate)'

    report_id = fields.Many2one('bm.report')
    pricing_id = fields.Many2one('bm.pricing', string='Estimate')
    labor = fields.Float(string='Labor')
    mech = fields.Float(string='Mechanical hours')
    est_cost = fields.Float(string='Estimate cost')
