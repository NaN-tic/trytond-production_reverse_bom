# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import bom


def register():
    Pool.register(
        bom.Product,
        module='production_reverse_bom', type_='model')
    Pool.register(
        bom.OpenReverseBOMTree,
        module='production_reverse_bom', type_='wizard')
