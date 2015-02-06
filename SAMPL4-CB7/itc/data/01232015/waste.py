"""Buffer        7.497 mL
                           Water        3.200 mL
                         guest01        0.237 mL
                         guest02        0.214 mL
                         guest03        0.054 mL
                         guest04        0.141 mL
                         guest05        0.146 mL
                         guest06        0.111 mL
                            host        1.120 mL
"""
from pint import UnitRegistry
ureg = UnitRegistry()


molecular_weights = [
    209.12,
    123.62,
    153.65,
    189.13,
    187.11,
    151.63,
    1162.9632,  # host
]

weights = ureg.Quantity(molecular_weights, ureg.gram / ureg.mole)

quantities = [.237,
              .214,
              .054,
              .141,
              .146,
              .111,
              1.120]

volumes = ureg.Quantity(quantities, ureg.milliliter)

names = [
'p-Xylylenediamine',
'2,2-Dimethyl-1-propanamine',
'6-Amino-1-hexanol',
'Hexamethylenediamine',
'(1R, 2R)-(-)-1, 2-Diaminocyclohexane',
'trans-4-Aminocyclohexanol hydrochloride',
'Cucurbit[7]uril hydrate'
]


for name, vol, weight in zip(names, volumes, weights):
    print name, 
    print( (vol * weight * ureg.Quantity('1 millimole / liter')).to('milligram'))
