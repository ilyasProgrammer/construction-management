# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields, _


_logger = logging.getLogger(__name__)


class Estimate(models.Model):
    _name = 'bm.estimate'
    _description = 'Estimate'

    name = fields.Char(string='Название', required=True)
    sequence = fields.Integer()  # сметы включаются в договоры. Смета принадлежит только 1 договору. Это поле используется только в таблице смет договора.
    project_id = fields.Many2one('bm.project', string='Проект')
    contract_id = fields.Many2one('project.project', string='Договор')
    spj_id = fields.Many2one('bm.spj', string='ГПР')
    partner_id = fields.Many2one(related='contract_id.partner_id')
    pricing_ids = fields.One2many('bm.estimate.lines', 'estimate_id', string='Расценки')
    currency_id = fields.Many2one(related='contract_id.currency_id')
    overheads = fields.Float(string='Накладные расходы', default=0)
    total_overheads = fields.Float(string='Накладные расходы', compute='_compute_amount', store=True)
    pricing_amount = fields.Integer(string='Всего расценок', compute='_compute_amount', store=True)
    total_cost = fields.Float(string='Сметная стоимость', compute='_compute_amount', store=True)
    total_amount_labor = fields.Float(string='Количество чел-часов', compute='_compute_amount', store=True)
    total_amount_mech = fields.Float(string='Количество мех. часов', compute='_compute_amount', store=True)
    total_cost_labor = fields.Float(string='Стоимость труда', compute='_compute_amount', store=True)
    total_cost_mech = fields.Float(string='Стоимость машин', compute='_compute_amount', store=True)
    comment = fields.Text(string='Описание')
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'bm.estimate')],
                                     string='Attachments')
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")

    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['domain'] = ['&', ('res_model', '=', 'bm.estimate'), ('res_id', 'in', self.ids)]
        return action

    @api.multi
    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'bm.estimate'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    @api.multi
    @api.depends('pricing_ids', 'overheads')
    def _compute_amount(self):
        for rec in self:
            total_amount_labor = 0
            total_amount_mech = 0
            total_cost_labor = 0
            total_cost_mech = 0
            for l in rec.pricing_ids:
                total_amount_labor += l.labor_vol*l.amount
                total_amount_mech += l.mech_vol*l.amount
                total_cost_labor += l.labor_vol*l.amount*l.labor_cost
                total_cost_mech += l.mech_vol*l.amount*l.mech_cost
            rec.total_amount_labor = total_amount_labor
            rec.total_amount_mech = total_amount_mech
            rec.total_cost_labor = total_cost_labor
            rec.total_cost_mech = total_cost_mech
            rec.total_cost = total_cost_labor + total_cost_mech + rec.overheads
            rec.pricing_amount = len(rec.pricing_ids)
            rec.total_overheads = rec.overheads

    @api.model
    def default_get(self, fields):
        res = super(Estimate, self).default_get(fields)
        if self._context.get('spj_id', False):
            res['spj_id'] = self._context['spj_id']
        if self._context.get('project_id', False):
            res['project_id'] = self._context['project_id']
        if self._context.get('contract_id', False):
            res['contract_id'] = self._context['contract_id']
        if self._context.get('project_id', False):
            res['project_id'] = self._context['project_id']
        return res


class EstimateLines(models.Model):
    _name = 'bm.estimate.lines'
    _description = 'Estimates lines'

    estimate_id = fields.Many2one('bm.estimate')
    pricing_id = fields.Many2one('bm.pricing', string='Расценка', required=True)
    code = fields.Char(related='pricing_id.code', readonly=True)
    name = fields.Char(related='pricing_id.name', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', readonly=True)
    pricing_uom = fields.Many2one(related='pricing_id.pricing_uom', readonly=True)
    labor_cost = fields.Float(string='Labor', help='Стоимость часа работ')
    mech_cost = fields.Float(string='Mech.', help='Стоимость машинного часа')
    labor_vol = fields.Float(string='Labor vol', help='Объем работ')
    mech_vol = fields.Float(string='Mech. vol', help='Объем машинных работ')
    amount = fields.Float(string='Количество', required=True)
    amount_unit = fields.Float(string='На 1 ед. раб.', compute='_compute_amount', store=True)
    amount_total = fields.Float(string='Всего', compute='_compute_amount', store=True)
    uom = fields.Many2one(related='pricing_id.pricing_uom', readonly=True)

    @api.multi
    @api.depends('pricing_id', 'amount', 'labor_cost', 'mech_cost', 'labor_vol', 'mech_vol')
    def _compute_amount(self):
        for rec in self:
            rec.amount_unit = rec.labor_vol*rec.labor_cost + rec.mech_vol*rec.mech_cost
            rec.amount_total = rec.amount * rec.amount_unit

    @api.v8
    @api.onchange('pricing_id')
    def on_change_pricing_id(self):
        if not self.pricing_id:
            return {}
        self.labor_cost = self.pricing_id.labor_cost
        self.mech_cost = self.pricing_id.mech_cost
        self.labor_vol = self.pricing_id.labor_vol
        self.mech_vol = self.pricing_id.mech_vol
        self.uom = self.pricing_id.pricing_uom
