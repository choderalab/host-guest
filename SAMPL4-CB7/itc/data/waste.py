from itctools.itctools import ureg, Quantity
from itctools.materials import Solvent, Compound, SimpleSolution
from itctools.labware import Labware, PipettingLocation
import yaml


directories = "02042015  02112015  02252015  02262015  03042015".split()
buffer = Solvent('buffer', density=1.014 * ureg.gram / ureg.milliliter)

nguests = 14
solutions = dict()
masses = dict()
# Define source solutions on the deck.one

names = dict(host="Cucurbit[7]uril hydrate",
guest01="p-Xylylenediamine",
guest02="2,2-Dimethyl-1-propanamine",
guest03="6-Amino-1-hexanol",
guest04="Hexamethylenediamine",
guest05="(1R, 2R)-(-)-1, 2-Diaminocyclohexane",
guest06="trans-4-Aminocyclohexanol hydrochloride",
guest07="Cyclohexylamine",
guest08="Cycloheptylamine",
guest09="Cyclooctylamine",
guest10="1-(2-Aminoethyl)piperazine",
guest11="exo-2-Aminonorbornane",
guest12="1,7,7-TRIMETHYLBICYCLO[2.2.1]HEPTAN-2-AMINE HYDROCHLORIDE",
guest13="3-Noradamantanamine Hydrochloride",
guest14="3-Amino-1-adamantanol",)

host = Compound('host', molecular_weight=1162.9632 * ureg.gram / ureg.mole, purity=0.7133)
guest_molecular_weights = [
    209.12,
    123.62,
    153.65,
    189.13,
    187.11,
    151.63,
    135.64,
    149.66,
    163.69,
    238.59,
    147.65,
    189.73,
    173.68,
    203.71]

guests = [
    Compound(
        name='guest%02d' %
        (guest_index +
         1),
        molecular_weight=guest_molecular_weights[guest_index] *
        ureg.gram / ureg.mole,
        purity=0.975) for guest_index in range(nguests)]



host_solution = SimpleSolution(
    compound=host,
    compound_mass=33.490 *
    ureg.milligram,
    solvent=buffer,
    solvent_mass=10.1151 *
    ureg.gram,
    location=PipettingLocation(
        '',
        '',
        1))
guest_solutions = list()

# Dispensed by quantos
guest_compound_masses = Quantity([2.210,
                                  1.400,
                                  1.705,
                                  1.945,
                                  1.975,
                                  1.635,
                                  1.700,
                                  1.640,
                                  1.725,
                                  2.480,
                                  1.560,
                                  2.080,
                                  1.875,
                                  2.195,
                                 ],
                                 ureg.milligram)
# Dispensed by quantos
guest_solvent_masses = Quantity([11.0478,
                                 11.6656,
                                 11.3653,
                                 10.8034,
                                 10.9705,
                                 10.8984,
                                 13.0758,
                                 10.9321,
                                 10.7799,
                                 10.7802,
                                 11.1413,
                                 11.5536,
                                 11.0276,
                                 10.9729,
                                ],
                                ureg.gram)


for guest_index in range(nguests):
    guest_solutions.append(
        SimpleSolution(
            compound=guests[guest_index],
            compound_mass=guest_compound_masses[guest_index],
            solvent=buffer,
            solvent_mass=guest_solvent_masses[guest_index],
            location=PipettingLocation(
                '',
                '',
                2 + guest_index)))



def parse_waste(wastefile):
    with open(wastefile, 'r') as ifile:
        lines = (line.rstrip() for line in ifile) # All lines including the blank ones
        lines = [line for line in lines if line] # Non-blank lines
        ifile.close()

        for line in lines[1:]:
            solution,quant,unit = line.split()
            quant = float(quant)
            if solution in solutions:
                solutions[solution] += Quantity(quant, unit)
            else:
                solutions[solution]= Quantity(quant, unit)



for dir in directories:
    print dir
    parse_waste('%s/wastes.txt'%dir)

for solution in solutions:
    if solution[0:5] == "guest":
        index= int(solution[5:]) - 1
        use_this = guest_solutions[index]
    elif solution == "host":
        use_this = host_solution
    else:
        continue
    masses[solution] = solutions[solution] * use_this.compound_mass / use_this.solvent_mass * use_this.solvent.density



for comp in masses.keys():
    masses[names[comp]] = str(masses.pop(comp))

buffer_total = sum(solutions.values())
masses["sodium_phosphate"] = str(buffer.density * buffer_total)
with open('waste.yml', 'w') as outfile:
    outfile.write( yaml.dump(masses, default_flow_style=False ) )
