# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, Button
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta


__all__ = ['BOMTree', 'OpenReverseBOMTreeTree', 'OpenReverseBOMTree']
__metaclass__ = PoolMeta


class BOMTree:
    __name__ = 'production.bom.tree'

    @classmethod
    def reverse_tree(cls, product):
        Input = Pool().get('production.bom.input')

        result = []
        boms = list(set([i.bom for i in Input.search([
                            ('product', '=', product.id),
                            ])]))
        processed = set()
        latter = set()
        for bom in boms:
            for product in bom.output_products:
                childs = cls.tree(product, 1.0, product.default_uom)
                values = {
                    'product': product.id,
                    'quantity': 1.0,
                    'uom': product.default_uom.id,
                    'unit_digits': product.default_uom.digits,
                    'childs': childs,
                }
                result.append(values)
                processed.add(product.id)
                latter.add(product)
        # Search for nesteed boms. Do it at the end for a better sorting
        for product in latter:
            for parent_bom in cls.reverse_tree(product):
                if parent_bom['product'] not in processed:
                    result.append(parent_bom)
                    processed.add(parent_bom['product'])
        return result


class OpenReverseBOMTreeTree(ModelView):
    'Open Reverse BOM Tree Tree'
    __name__ = 'production.bom.reverse_tree.open.tree'

    bom_tree = fields.One2Many('production.bom.tree', None, 'BOM Tree',
        readonly=True)

    @classmethod
    def reverse_tree(cls, product):
        pool = Pool()
        Tree = pool.get('production.bom.tree')
        return {
            'bom_tree': Tree.reverse_tree(product),
            }


class OpenReverseBOMTree(Wizard):
    'Open Reverse BOM Tree'
    __name__ = 'production.bom.reverse_tree.open'
    start_state = 'tree'

    tree = StateView('production.bom.reverse_tree.open.tree',
        'production.bom_tree_open_tree_view_form', [
            Button('Close', 'end', 'tryton-close'),
            ])

    def default_tree(self, fields):
        pool = Pool()
        Product = Pool().get('product.product')
        BomTree = pool.get('production.bom.reverse_tree.open.tree')
        product = Product(Transaction().context['active_id'])
        return BomTree.reverse_tree(product)
