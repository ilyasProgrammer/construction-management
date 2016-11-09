# -*- coding: utf-8 -*-

from openerp import tools
import logging
from openerp import api, models, fields

_logger = logging.getLogger(__name__)


class UpdatePrice(models.Model):
    _name = 'price'

    fields_list = ['turnover', 'sale_avg_price', 'sale_purchase_price', 'sale_num_invoiced',
                   'purchase_num_invoiced', 'sales_gap', 'purchase_gap', 'total_cost', 'sale_expected',
                   'normal_cost', 'total_margin', 'expected_margin', 'total_margin_rate', 'expected_margin_rate']

    @api.model
    def action_update_price(self):
        ppl = self.env['product.pricelist'].search([])
        pricelist = ppl[1]  # TODO NEED to get pricelist somehow
        if self._context.get('active_model', False) == 'account.invoice':
            _logger.info('Start price updating on purchase invoice change')
            invoice = self.env['account.invoice'].browse(self._context['active_id'])
            prods = [r.product_id for r in invoice.invoice_line]
        else:
            _logger.info('Start price updating on exchange rate alteration')
            prods = [r.product_id for r in self.env['purchase.order.line'].search([])]
        product_uom_obj = self.env['product.uom']
        currency = self.env['res.currency'].browse(23)  # must be UAH
        _logger.info('New exchange rate = %s' % currency.rate)
        for product in prods:
            price_uom_id = product.uom_id.id
            res_val = product._product_margin([product.id], self.fields_list)
            base = res_val[product.id]['purchase_avg_price'] * currency.rate
            res = pricelist._price_rule_get_multi(pricelist, [(product, 1.0, False)])
            rule = self.env['product.pricelist.item'].browse(res[product.id][1])
            price = base * (1.0 + (rule.price_discount or 0.0))
            if rule.price_round:
                price = tools.float_round(price, precision_rounding=rule.price_round)
            convert_to_price_uom = (lambda price: product_uom_obj._compute_price(product.uom_id.id, price, price_uom_id))
            if rule.price_surcharge:
                price_surcharge = convert_to_price_uom(rule.price_surcharge)
                price += price_surcharge
            product.list_price = price
            _logger.info('\n Product = %s \n purchase_avg_price = %s \n new list_price = %s' % (product.name, res_val[product.id]['purchase_avg_price'], product.list_price))
