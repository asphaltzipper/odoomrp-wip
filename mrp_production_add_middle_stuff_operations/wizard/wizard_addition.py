
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api


class WizProductionProductLine(models.TransientModel):
    _inherit = 'wiz.production.product.line'

    def _def_production_id(self):
        if 'active_model' in self.env.context:
            if self.env.context['active_model'] == 'mrp.production':
                return self.env.context.get('active_id')
            elif self.env.context['active_model'] == (
                    'mrp.production.workcenter.line'):
                mpwl_obj = self.env['mrp.production.workcenter.line']
                active_id = self.env.context.get('active_id', False)
                if active_id:
                    mpwl = mpwl_obj.browse(active_id)
                    return mpwl.production_id.id
        return False

    def _def_work_order_id(self):
        if 'active_model' in self.env.context and (
                self.env.context['active_model'] ==
                'mrp.production.workcenter.line'):
            return self.env.context.get('active_id', False)
        return False

    work_order = fields.Many2one('mrp.production.workcenter.line',
                                 'Work Order',
                                 default=_def_work_order_id)
    production_id = fields.Many2one(
        'mrp.production', 'Production Order', select=True,
        default=_def_production_id)

    @api.multi
    def add_product(self):
        res = super(WizProductionProductLine, self).add_product()
        st_move_obj = self.env['stock.move']
        mppl_obj = self.env['mrp.production.product.line']
        # LF stock.move
        move = st_move_obj.search([('raw_material_production_id', '=',
                                    self.production_id.id),
                                   ('product_id', '=', self.product_id.id),
                                   ('product_qty', '=', self.product_qty),
                                   ('state', '=', 'draft')], order='id DESC')
        # LF mrp.production.product.line
        mppl = mppl_obj.search([('production_id', '=', self.production_id.id),
                                ('product_id', '=', self.product_id.id),
                                ('product_qty', '=', self.product_qty)],
                               order='id DESC')
        if move and mppl:
            move[0].work_order = self.work_order.id
            mppl[0].work_order = self.work_order.id
        return res
