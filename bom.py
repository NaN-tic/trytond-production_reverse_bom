# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateAction
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.modules.production.bom import OpenBOMTree


__all__ = ['BOMTree', 'OpenReverseBOMTreeTree', 'OpenReverseBOMTree',
    'OpenBOMTreeFromReverse']
__metaclass__ = PoolMeta


class BOMTree:
    __name__ = 'production.bom.tree'

    @classmethod
    def reverse_boms(cls, product):
        Input = Pool().get('production.bom.input')

        boms = set([i.bom for i in Input.search([
                        ('product', '=', product.id),
                        ])])
        result = []
        processed = set()
        latter = set()
        for bom in boms:
            for product in bom.output_products:
                latter.add(product)
            result.append(bom.id)
        # Search for nesteed boms. Do it at the end for a better sorting
        for product in latter:
            nested = cls.reverse_boms(product)
            processed |= set(nested)
            result.extend(nested)
        return result


class OpenReverseBOMTreeTree(ModelView):
    'Open Reverse BOM Tree Tree'
    __name__ = 'production.bom.reverse_tree.open.tree'

    bom_tree = fields.One2Many('production.bom.tree', None, 'BOM Tree',
        readonly=True)


class OpenReverseBOMTree(Wizard):
    'Open Reverse BOM Tree'
    __name__ = 'production.bom.reverse_tree.open'

    start = StateAction('production_reverse_bom.act_reverse_bom_list')

    def do_start(self, action):
        pool = Pool()
        Product = pool.get('product.product')
        BomTree = pool.get('production.bom.tree')
        product = Product(Transaction().context['active_id'])
        data = {}
        data['res_id'] = BomTree.reverse_boms(product)
        return action, data


class OpenBOMTreeFromReverse(OpenBOMTree):
    'Open BOM Tree From Bom'
    __name__ = 'production.bom.tree.from_reverse'

    def _execute(self, state_name):
        pool = Pool()
        Bom = pool.get('production.bom')
        if Transaction().context.get('active_model') != 'production.bom':
            return super(OpenBOMTreeFromReverse, self)._execute(state_name)
        bom = Bom(Transaction().context['active_id'])
        product_id = None
        if bom.outputs:
            product_id = bom.outputs[0].product.id
        with Transaction().set_context(active_id=product_id,
                active_model='product.product'):
            return super(OpenBOMTreeFromReverse, self)._execute(state_name)
