# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    def action_button_confirm(self):
        procurement_obj = self.env['procurement.order']
        procurement_group_obj = self.env['procurement.group']
        res = super(SaleOrder, self).action_button_confirm()
        for line in self.order_line:
            valid = self._validate_service_product_for_procurement(
                line.product_id)
            if valid:
                if not self.procurement_group_id:
                    vals = self._prepare_procurement_group(self)
                    group = procurement_group_obj.create(vals)
                    self.write({'procurement_group_id': group.id})
                vals = self._prepare_order_line_procurement(
                    self, line, group_id=self.procurement_group_id.id)
                vals['name'] = self.name + ' - ' + line.product_id.name
                procurement_obj.create(vals)
        return res

    def _validate_service_product_for_procurement(self, product):
        routes = product.route_ids.filtered(
            lambda r: r.name in ('Make To Order', 'Buy'))
        return product.type == 'service' and len(routes) == 2
