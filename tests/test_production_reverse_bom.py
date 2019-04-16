# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import doctest
from decimal import Decimal
import trytond.tests.test_tryton
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.modules.company.tests import create_company, set_company


class ProductionReverseBomTestCase(ModuleTestCase):
    'Test module'
    module = 'production_reverse_bom'

    @with_transaction()
    def test_production_reverse_bom(self):
        'Test get_output_products'
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        Bom = pool.get('production.bom')

        # Create Company
        company = create_company()
        with set_company(company):

            # Create Product
            unit, = Uom.search([
                    ('name', '=', 'Unit'),
                    ])
            template, = Template.create([{
                        'name': 'Product',
                        'default_uom': unit.id,
                        'type': 'goods',
                        'list_price': Decimal(30),
                        }])
            product, = Product.create([{
                        'template': template.id,
                        'cost_price': Decimal(20),
                        }])

            # Create Components
            template1, = Template.create([{
                        'name': 'Component 1',
                        'default_uom': unit.id,
                        'type': 'goods',
                        'list_price': Decimal(5),
                        }])
            component1, = Product.create([{
                        'template': template1.id,
                        'cost_price': Decimal(1),
                        }])
            meter, = Uom.search([
                    ('name', '=', 'Meter'),
                    ])
            template2, = Template.create([{
                        'name': 'Component 2',
                        'default_uom': meter.id,
                        'type': 'goods',
                        'list_price': Decimal(7),

                        }])
            component2, = Product.create([{
                        'template': template2.id,
                        'cost_price': Decimal(5),                        
                        }])

            # Create Bill of Material
            centimeter, = Uom.search([
                    ('name', '=', 'centimeter'),
                    ])
            bom, = Bom.create([{
                        'name': 'Product',
                        'inputs': [('create', [{
                                        'product': component1.id,
                                        'quantity': 5.0,
                                        'uom': unit.id,
                                        }, {
                                        'product': component2.id,
                                        'quantity': 150.0,
                                        'uom': centimeter.id,
                                        }])],
                        'outputs': [('create', [{
                                        'product': product.id,
                                        'quantity': 1.0,
                                        'uom': unit.id,
                                        }])],
                        }])

            output_products = Product.get_output_products([component1],
                'output_products')[component1.id]
            self.assertEqual(output_products, [product.id])
            output_products = Product.get_output_products([component2],
                'output_products')[component2.id]
            self.assertEqual(output_products, [product.id])


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ProductionReverseBomTestCase))
    return suite
