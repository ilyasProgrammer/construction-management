# -*- coding: utf-8 -*-

from StringIO import StringIO
import base64
import datetime
import dateutil
import time
import logging
from telebot.apihelper import ApiException, _convert_markup
from telebot import types, TeleBot
from lxml import etree
from openerp import tools
from openerp import api, models, fields
import openerp.addons.auth_signup.res_users as res_users
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _
from openerp.addons.base.ir.ir_qweb import QWebContext

_logger = logging.getLogger(__name__)


class UpdatePrice(models.Model):
    _name = 'price'

    @api.model
    def action_update_price(self, id_or_xml_id=None):
        _logger.info('Start price updating')
        fields_list = ['turnover', 'sale_avg_price', 'sale_purchase_price', 'sale_num_invoiced',
                       'purchase_num_invoiced', 'sales_gap', 'purchase_gap', 'total_cost', 'sale_expected',
                       'normal_cost', 'total_margin', 'expected_margin', 'total_margin_rate', 'expected_margin_rate']
        prods = self.env['purchase.order.line'].search([])
        currency = self.env['res.currency'].browse(23)
        _logger.info('New exchange rate = %s' % currency.rate)
        for prod in prods:
            res_val = prod.product_id._product_margin([prod.product_id.id], [x for x in fields_list])
            prod.product_id.list_price = res_val[prod.product_id.id]['purchase_avg_price'] * currency.rate
            _logger.info('\n Product = %s \n purchase_avg_price = %s \n new list_price = %s' % (prod.product_id.name, res_val[prod.product_id.id]['purchase_avg_price'], prod.product_id.list_price))
