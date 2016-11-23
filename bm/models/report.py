# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields


_logger = logging.getLogger(__name__)


class Report(models.Model):
    _name = 'bm.report'
    _description = 'Job report'

    name = fields.Char(compute='_get_name', store=True)
    date = fields.Date(string='Дата завершения', default=fields.Date.context_today, help='Дата подтверждения завершения задания прорабом')
    foreman_id = fields.Many2one('hr.employee', string='Прораб', required=True)  # domain=lambda self: [('id', 'in', self.project_id.foremen_ids)]
    task_id = fields.Many2one('project.task', string='Задание')
    project_id = fields.Many2one(related='task_id.project_id.bm_project_id')
    amount_lines_ids = fields.One2many('bm.report.lines.amount', 'report_id')
    labor_lines_ids = fields.One2many('bm.report.lines.labor', 'report_id')
    mech_lines_ids = fields.One2many('bm.report.lines.mech', 'report_id')
    state = fields.Selection([('draft', 'Черновик'),
                              ('sent', 'Отправлено'),
                              ('approved', 'Утверждено'),
                              ('done', 'Завершено'),
                              ], 'Статус', readonly=True, default='draft')
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'bm.report')],
                                     string='Вложения')
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    comment = fields.Text(string='Комментарий')

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
            task = self.env['project.task'].browse(res['task_id'])
            brla = self.env['bm.report.lines.amount']
            brll = self.env['bm.report.lines.labor']
            brlm = self.env['bm.report.lines.mech']
            brla_lines = []
            brll_lines = []
            brlm_lines = []
            for l in task.pricing_ids:
                brla_line = brla.create({
                    'pricing_id': l.pricing_id.id,
                    'type': 'amount',
                    'plan_amount': l.amount,
                    'sequence': l.sequence,
                })
                brla_lines.append(brla_line.id)

                brll_line = brll.create({
                    'pricing_id': l.pricing_id.id,
                    'type': 'time',
                    'plan_labor': l.labor_vol,
                    'sequence': l.sequence,
                })
                brll_lines.append(brll_line.id)

                brlm_line = brlm.create({
                    'pricing_id': l.pricing_id.id,
                    'type': 'time',
                    'plan_mech': l.mech_vol,
                    'sequence': l.sequence,
                })
                brlm_lines.append(brlm_line.id)
            res['amount_lines_ids'] = brla_lines
            res['labor_lines_ids'] = brll_lines
            res['mech_lines_ids'] = brlm_lines
        if self._context.get('foreman_id', False):
            res['foreman_id'] = self._context['foreman_id']
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if len(employee):
            res['foreman_id'] = employee.id
        return res


class ReportLinesAmount(models.Model):
    _name = 'bm.report.lines.amount'
    _description = 'Report line (pricings amount)'

    report_id = fields.Many2one('bm.report')
    sequence = fields.Integer()
    type = fields.Selection([('amount', 'кол-во'), ('time', 'часы')], string='Тип')
    pricing_uom = fields.Many2one(related='pricing_id.pricing_uom', readonly=True)
    pricing_id = fields.Many2one('bm.pricing', string='Расценка', required=True)
    code = fields.Char(related='pricing_id.code', readonly=True)
    name = fields.Char(related='pricing_id.name', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', readonly=True)
    plan_amount = fields.Float(string='Количество работы по заданию')
    fact_amount = fields.Float()
    d1 = fields.Float(string='Д1')
    d2 = fields.Float(string='Д2')
    d3 = fields.Float(string='Д3')
    d4 = fields.Float(string='Д4')
    d5 = fields.Float(string='Д5')
    d6 = fields.Float(string='Д6')
    d7 = fields.Float(string='Д7')


class ReportLinesLabor(models.Model):
    _name = 'bm.report.lines.labor'
    _description = 'Report line (pricings labor)'

    report_id = fields.Many2one('bm.report')
    sequence = fields.Integer()
    type = fields.Selection([('amount', 'кол-во'), ('time', 'часы')], string='Тип')
    pricing_id = fields.Many2one('bm.pricing', string='Расценка', required=True)
    pricing_uom = fields.Many2one(related='pricing_id.pricing_uom', readonly=True)
    code = fields.Char(related='pricing_id.code', readonly=True)
    name = fields.Char(related='pricing_id.name', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', readonly=True)
    plan_labor = fields.Float(string='Количество труда по заданию')
    fact_labor = fields.Float()
    d1 = fields.Float(string='Д1')
    d2 = fields.Float(string='Д2')
    d3 = fields.Float(string='Д3')
    d4 = fields.Float(string='Д4')
    d5 = fields.Float(string='Д5')
    d6 = fields.Float(string='Д6')
    d7 = fields.Float(string='Д7')


class ReportLinesMech(models.Model):
    _name = 'bm.report.lines.mech'
    _description = 'Report line (pricings mech)'

    report_id = fields.Many2one('bm.report')
    sequence = fields.Integer()
    type = fields.Selection([('amount', 'кол-во'), ('time', 'часы')], string='Тип')
    pricing_id = fields.Many2one('bm.pricing', string='Расценка', required=True)
    pricing_uom = fields.Many2one(related='pricing_id.pricing_uom', readonly=True)
    code = fields.Char(related='pricing_id.code', readonly=True)
    name = fields.Char(related='pricing_id.name', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', readonly=True)
    plan_mech = fields.Float(string='Количество маш. часов по заданию')
    fact_mech = fields.Float()
    d1 = fields.Float(string='Д1')
    d2 = fields.Float(string='Д2')
    d3 = fields.Float(string='Д3')
    d4 = fields.Float(string='Д4')
    d5 = fields.Float(string='Д5')
    d6 = fields.Float(string='Д6')
    d7 = fields.Float(string='Д7')













    # @api.v8
    # @api.onchange('pricing_id')
    # def on_change_pricing_id(self):
    #     if not self.pricing_id:
    #         return {}
    #     # self.labor_cost = self.pricing_id.labor_cost
    #     # self.mech_cost = self.pricing_id.mech_cost
    #     self.labor_vol = self.pricing_id.labor_vol
    #     self.mech_vol = self.pricing_id.mech_vol
    #
