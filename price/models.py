# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields

_logger = logging.getLogger(__name__)


class UpdatePrice(models.Model):
    _name = 'price'

    fields_list = ['turnover', 'sale_avg_price', 'sale_purchase_price', 'sale_num_invoiced',
                   'purchase_num_invoiced', 'sales_gap', 'purchase_gap', 'total_cost', 'sale_expected',
                   'normal_cost', 'total_margin', 'expected_margin', 'total_margin_rate', 'expected_margin_rate']

    @api.model
    def action_update_price(self, id_or_xml_id=None):
        _logger.info('Start price updating')
        pols = self.env['purchase.order.line'].search([])
        currency = self.env['res.currency'].browse(23)  # must be UAH
        _logger.info('New exchange rate = %s' % currency.rate)
        for pol in pols:
            prod = pol.product_id
            res_val = prod._product_margin([prod.id], self.fields_list)
            prod.list_price = res_val[prod.id]['purchase_avg_price'] * currency.rate
            _logger.info('\n Product = %s \n purchase_avg_price = %s \n new list_price = %s' % (prod.name, res_val[prod.id]['purchase_avg_price'], prod.list_price))

    @api.model
    def action_update_price_on_invoice(self, id_or_xml_id=None):
        _logger.info('Start price updating on purchase invoice change')
        invoice = self.env['account.invoice'].browse(self._context['active_id'])
        prods = [r.product_id for r in invoice.invoice_line]
        currency = self.env['res.currency'].browse(23)  # must be UAH
        _logger.info('New exchange rate = %s' % currency.rate)
        for prod in prods:
            res_val = prod._product_margin([prod.id], self.fields_list)
            prod.list_price = res_val[prod.id]['purchase_avg_price'] * currency.rate
            _logger.info('\n Product = %s \n purchase_avg_price = %s \n new list_price = %s' % (prod.name, res_val[prod.id]['purchase_avg_price'], prod.list_price))
