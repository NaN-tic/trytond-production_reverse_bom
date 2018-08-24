# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.wizard import Wizard, StateAction
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta


__all__ = ['Product', 'OpenReverseBOMTree']


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'
    output_products = fields.Function(fields.One2Many('product.product', None,
            'products'),
        'get_output_products')

    @classmethod
    def get_output_products(cls, products, name):
        pool = Pool()
        Input = pool.get('production.bom.input')
        inputs = Input.search([
                ('product', 'in', [x.id for x in products]),
                ])
        output_products = {}
        for product in products:
            output_products[product.id] = []

        for input_ in inputs:
            for product in input_.bom.output_products:
                output_products[input_.product.id].append(product.id)
        return output_products


class OpenReverseBOMTree(Wizard):
    'Open Reverse BOM Tree'
    __name__ = 'production.bom.reverse_tree.open'

    start = StateAction('production_reverse_bom.act_product_reverse_bom')

    def do_start(self, action):
        data = {'res_id': Transaction().context['active_ids']}
        return action, data
