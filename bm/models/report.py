# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Report(models.Model):
    _name = 'bm.report'
    _description = 'Job report'

    name = fields.Char(compute='_get_name', store=True)
    date = fields.Datetime(string='Дата завершения', default=fields.Date.context_today, help='Дата подтверждения завершения задания прорабом')
    foreman_id = fields.Many2one('hr.employee', string='Прораб', required=True)  # domain=lambda self: [('id', 'in', self.project_id.foremen_ids)]
    task_id = fields.Many2one('project.task', string='Задание')
    lines_ids = fields.One2many('bm.report.lines', 'report_id')
    state = fields.Selection([('draft', 'Черновик'),
                              ('sent', 'Отправлено'),
                              ('approved', 'Утверждено'),
                              ('done', 'Завершено'),
                              ], 'Статус', readonly=True, default='draft')
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'bm.report')],
                                     string='Вложения')
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

    @api.multi
    @api.depends('task_id')
    def _get_name(self):
        for record in self:
            record.name = "Отчет по заданию " + str(record.task_id.code)

    @api.model
    def default_get(self, fields):
        res = super(Report, self).default_get(fields)
        if self._context.get('task_id', False):
            res['task_id'] = self._context['task_id']
        if self._context.get('foreman_id', False):
            res['foreman_id'] = self._context['foreman_id']
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if len(employee):
            res['foreman_id'] = employee.id
        return res


class ReportLines(models.Model):
    _name = 'bm.report.lines'
    _description = 'Report line (pricings)'

    report_id = fields.Many2one('bm.report')
    pricing_id = fields.Many2one('bm.pricing', string='Расценка', required=True)
    code = fields.Char(related='pricing_id.code', readonly=True)
    name = fields.Char(related='pricing_id.name', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', readonly=True)
    amount = fields.Float(string='Количество')
    pricing_uom = fields.Many2one(related='pricing_id.pricing_uom', readonly=True)
    labor_cost = fields.Float(string='Labor', help='Стоимость часа работ')
    mech_cost = fields.Float(string='Mech.', help='Стоимость машинного часа')
    labor_vol = fields.Float(string='Labor vol', help='Объем работ')
    mech_vol = fields.Float(string='Mech. vol', help='Объем машинных работ')

    @api.v8
    @api.onchange('pricing_id')
    def on_change_pricing_id(self):
        if not self.pricing_id:
            return {}
        self.labor_cost = self.pricing_id.labor_cost
        self.mech_cost = self.pricing_id.mech_cost
        self.labor_vol = self.pricing_id.labor_vol
        self.mech_vol = self.pricing_id.mech_vol

