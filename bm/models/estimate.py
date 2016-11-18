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
    overheads = fields.Float(string='Overheads')
    comment = fields.Char(string='Comment')
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


class EstimateLines(models.Model):
    _name = 'bm.estimate.lines'
    _description = 'Estimates lines'

    estimate_id = fields.Many2one('bm.estimate')
    pricing_id = fields.Many2one('bm.pricing', string='Estimate', required=True)
    code = fields.Char(related='pricing_id.code', readonly=True)
    name = fields.Char(related='pricing_id.name', readonly=True)
    rationale = fields.Char(related='pricing_id.rationale', readonly=True)
    pricing_uom = fields.Many2one(related='pricing_id.pricing_uom', readonly=True)
    labor = fields.Float(string='Labor')
    mech = fields.Float(string='Mech.')
    est_cost = fields.Float(string='Est. cost')

    @api.v8
    @api.onchange('pricing_id')
    def on_change_pricing_id(self):
        if not self.pricing_id:
            return {}
        self.labor = self.pricing_id.labor
        self.mech = self.pricing_id.mech
        self.est_cost = self.pricing_id.est_cost
