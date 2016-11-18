# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields, _


_logger = logging.getLogger(__name__)


class Estimate(models.Model):
    _name = 'bm.estimate'
    _description = 'Estimate'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('bm.project', string='Project')
    contract_id = fields.Many2one('project.project', string='Contract')
    spj_id = fields.Many2one('bm.spj', string='SPJ')
    partner_id = fields.Many2one(related='contract_id.partner_id')
    pricing_ids = fields.One2many('bm.estimate.lines', 'estimate_id', string='Pricings')
    currency_id = fields.Many2one(related='contract_id.currency_id')
    overheads = fields.Float(string='Overheads', default=0)
    amount = fields.Float(string='Estimated cost', default=0)
    amount_labor_cost = fields.Float(string='Total labor cost', default=0)
    amount_mech_cost = fields.Float(string='Total mech cost', default=0)
    comment = fields.Text(string='Comment')
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

    @api.v8
    @api.onchange('pricing_ids')
    def on_change_pricing_ids(self):
        amount = self.overheads
        amount_labor_cost = 0
        amount_mech_cost = 0
        for line in self.pricing_ids:
            amount += line.labor_vol*line.labor_cost + line.mech_vol*line.mech_cost
            amount_labor_cost += line.labor_vol*line.labor_cost
            amount_mech_cost += line.mech_vol*line.mech_cost
        self.amount = amount
        self.amount_labor_cost = amount_labor_cost
        self.amount_mech_cost = amount_mech_cost


class EstimateLines(models.Model):
    _name = 'bm.estimate.lines'
    _description = 'Estimates lines'

    estimate_id = fields.Many2one('bm.estimate')
    pricing_id = fields.Many2one('bm.pricing', string='Estimate', required=True)
    code = fields.Char(related='pricing_id.code', readonly=True)
    name = fields.Char(related='pricing_id.name', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', readonly=True)
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
