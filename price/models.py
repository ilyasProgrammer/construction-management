# -*- coding: utf-8 -*-

import logging
from openerp import api, models, fields
from operator import itemgetter
from openerp.exceptions import ValidationError
import time

_logger = logging.getLogger(__name__)


class UpdatePrice(models.Model):
    _name = 'price'

    @api.model
    def action_update_price(self):
        if self._context.get('active_model', False) == 'account.invoice':
            _logger.info('Start price updating on purchase invoice change')
            invoice = self.env['account.invoice'].browse(self._context['active_id'])
            prods = [r.product_id for r in invoice.invoice_line]
        else:
            _logger.info('Start price updating on exchange rate alteration')
            # prods = [r.product_id for r in self.env['purchase.order.line'].search([])]
            active_id = self._context.get('active_id', False)
            if active_id:
                prods = self.env['product.product'].search([('standard_price', '!=', 0), ('currency_id', '=', active_id)])
            else:
                prods = self.env['product.product'].search([('standard_price', '!=', 0)])
        for product in prods:
            if not self.product_valid(product):
                continue
            currency = product.currency_id
            rates = [(r.name, r.rate) for r in self.env['res.currency.rate'].search([('currency_id', '=', currency.id)])]
            rates.sort(key=itemgetter(0))  # sort by date
            new_rate_date = rates[1][0]
            t = time.strptime(new_rate_date, '%Y-%m-%d %H:%M:%S')
            n = time.strptime(fields.Datetime.now(), '%Y-%m-%d %H:%M:%S')
            if (t.tm_yday, t.tm_year) != (n.tm_yday, n.tm_year):
                _logger.info('Currency %s have no new rate for today.' % currency.name)
                continue
            new_rate = rates[1][1]
            old_rate = rates[0][1]
            _logger.info('\n currency = %s \n old_rate = %s \n new_rate = %s' % (currency.name, old_rate, new_rate))
            standard_price = (product.standard_price/old_rate)*new_rate
            product.standard_price = standard_price
            seller_info = product.seller_ids.filtered(lambda reg: reg.use_price_list is True)[0]
            price_list = seller_info.name.property_product_pricelist
            mult = price_list.version_id.items_id.price_discount
            surcharge = price_list.version_id.items_id.price_surcharge
            list_price = product.standard_price * (1+mult) + surcharge
            product.list_price = list_price
            _logger.info('\n Product = %s \n new_cost_price = %s \n new_sale_price = %s' % (product.name, standard_price, list_price))

    def product_valid(self, product):
        error_msg = ''
        if not product.currency_id:
            error_msg += 'Product must have currency. Product = %s \n' % product.id
        if not product.standard_price:
            error_msg += 'Cost price must be > 0. Product = %s \n' % product.id
        if len(product.seller_ids) < 1:
            error_msg += 'Must be at least one supplier for product %s \n' % product.id
        if len(product.seller_ids.name.property_product_pricelist) < 1:
            error_msg += 'Supplier %s have no price list. \n' % product.seller_ids.name
        if len(product.seller_ids.filtered(lambda reg: reg.use_price_list is True)) < 1:
            error_msg = 'No supplier with use_price_list flag set in product %s \n' % product.id
        rates = [(r.name, r.rate) for r in self.env['res.currency.rate'].search([('currency_id', '=', product.currency_id.id)])]
        if len(rates) < 2:
            error_msg += 'Currency %s has less than 2 rates \n' % product.currency_id.name
        if error_msg:
            _logger.error(error_msg)
            return False
        return True
            # raise ValidationError(error_msg)


class Product(models.Model):
    _inherit = 'product.template'

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'EUR')]), string='Currency', required=True)


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    use_price_list = fields.Boolean(default=True)



#
# eur rub
# 10  100 10-1
#         20-1
# 100/10*20
