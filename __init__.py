# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .bom import *


def register():
    Pool.register(
        Product,
        module='production_reverse_bom', type_='model')
    Pool.register(
        OpenReverseBOMTree,
        module='production_reverse_bom', type_='wizard')
