#! /usr/bin/env python
"""
Script for generation of input files for host to guest ITC titrations.
"""
from itctools.itctools import ureg, Quantity
from itctools.procedures import ITCProtocol, ITCExperimentSet, ITCExperiment, ITCHeuristicExperiment
from itctools.materials import Solvent, Compound, SimpleSolution
from itctools.labware import Labware, PipettingLocation


# Define solvents.
# TODO command line specification of density and name
water = Solvent('water', density=0.9970479 * ureg.gram / ureg.milliliter)
buffer = Solvent('buffer', density=1.014 * ureg.gram / ureg.milliliter)

# Define compounds.

#nguests = 6  # overnight from 5pm till 9am
nguests = 6 # number of guest compounds
# nguests = 7 # number of guest compounds # DEBUG (one source plate only)
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
guest_compound_Ka = Quantity([21024287.6408,
                              13556262.0311,
                              81495.6444611,
                              1788684.70709,
                              2153596.60855,
                              769185.744612,
                              29967627.9188,
                              594389946.514,
                              2372114592.34,
                              683472.220385,
                              164811515.64,
                              6869559660.36,
                              28356538311.4,
                              396415131.021],
                             ureg.liter / ureg.mole)  # see dGtoKa.py
guests = [
    Compound(
        name='guest%02d' %
        (guest_index +
         1),
        molecular_weight=guest_molecular_weights[guest_index] *
        ureg.gram / ureg.mole,
        purity=0.975) for guest_index in range(nguests)]


# Define troughs on the instrument.

water_trough = Labware(RackLabel='Water', RackType='Trough 100ml')
buffer_trough = Labware(RackLabel='Buffer', RackType='Trough 100ml')

# Define source labware.
#source_plate = Labware(RackLabel='SourcePlate', RackType='12WellVialHolder')
source_plate = Labware(RackLabel='SourcePlate', RackType='5x3 Vial Holder')

# Define source solutions on the deck.one
# TODO : Use actual compound and solvent masses.
# NOTE: Host solution is diluted by 10x.

host_solution = SimpleSolution(
    compound=host,
    compound_mass=8.7 *
    ureg.milligram,
    solvent=buffer,
    solvent_mass=10.4732 *
    ureg.gram,
    location=PipettingLocation(
        source_plate.RackLabel,
        source_plate.RackType,
        1))
guest_solutions = list()

#guest_compound_masses = Quantity([2.145, 1.268, 1.576, 1.940, 1.919, 1.555, 1.391, 1.535, 1.679, 2.447, 1.514, 1.946, 1.781, 2.089], milligrams)
guest_compound_masses = Quantity([2.210,
                                  1.400,
                                  1.705,
                                  1.945,
                                  1.975,
                                  1.635,
                                  ],
                                 ureg.milligram)

# try to prepare this:
#print('host')
#print (host.molecular_weight * host.purity * Quantity('1 millimole / liter') * Quantity('10 milliliter')).to(
#    'milligram')

#for g,guest in enumerate(guests, start=1):
#    print('guest %d' % g)
#    print (guest.molecular_weight * guest.purity * Quantity('1 millimole / liter') * Quantity('10 milliliter')).to('milligram')


guest_solvent_masses = Quantity([11.0478,
                                 11.6656,
                                 11.3653,
                                 10.8034,
                                 10.9705,
                                 10.8984,
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
                source_plate.RackLabel,
                source_plate.RackType,
                2 + guest_index)))

# Define ITC protocol.

# Protocol for 'control' titrations (water-water, buffer-buffer,
# titrations into buffer, etc.)
control_protocol = ITCProtocol(
    'control protocol',
    sample_prep_method='Plates Quick.setup',
    itc_method='ChoderaWaterWater.inj',
    analysis_method='Control')
# Protocol for 1:1 binding analyis
blank_protocol = ITCProtocol(
    '1:1 binding protocol',
    sample_prep_method='Chodera Load Cell Without Cleaning Cell After.setup',
    itc_method='ChoderaHostGuest.inj',
    analysis_method='Onesite')
binding_protocol = ITCProtocol(
    '1:1 binding protocol',
    sample_prep_method='Plates Quick.setup',
    itc_method='ChoderaHostGuest.inj',
    analysis_method='Onesite')
# Protocol for cleaning protocol
cleaning_protocol = ITCProtocol(
    'cleaning protocol',
    sample_prep_method='Plates Clean.setup',
    itc_method='water5inj.inj',
    analysis_method='Control')

# Define ITC Experiment.

# use specified protocol by default
itc_experiment_set = ITCExperimentSet(name='SAMPL4-CB7 host-guest experiments')
# Add available plates for experiments.
itc_experiment_set.addDestinationPlate(
    Labware(
        RackLabel='DestinationPlate',
        RackType='ITC Plate'))
itc_experiment_set.addDestinationPlate(
    Labware(
        RackLabel='DestinationPlate2',
        RackType='ITC Plate'))

nreplicates = 1  # number of replicates of each experiment

# Add cleaning experiment.
name = 'initial cleaning water titration'
itc_experiment_set.addExperiment(
    ITCExperiment(
        name=name,
        syringe_source=water_trough,
        cell_source=water_trough,
        protocol=cleaning_protocol))

# Add water control titrations.
for replicate in range(1):
    name = 'water into water %d' % (replicate + 1)
    itc_experiment_set.addExperiment(
        ITCExperiment(
            name=name,
            syringe_source=water_trough,
            cell_source=water_trough,
            protocol=control_protocol))

# Add buffer control titrations.
for replicate in range(1):
    name = 'buffer into buffer %d' % (replicate + 1)
    itc_experiment_set.addExperiment(
        ITCExperiment(
            name=name,
            syringe_source=buffer_trough,
            cell_source=buffer_trough,
            protocol=control_protocol))

# Host into buffer.
for replicate in range(1):
    name = 'host into buffer %d' % (replicate + 1)
    itc_experiment_set.addExperiment(
        ITCExperiment(
            name=name,
            syringe_source=host_solution,
            cell_source=buffer_trough,
            protocol=binding_protocol))

# Host/guests.
# scale cell concentration to fix necessary syringe concentrations
cell_scaling = 1.
for guest_index in range(nguests):

    # We need to store the experiments before adding them to the set
    host_guest_experiments = list()
    buff_guest_experiments = list()

    # Scaling factors per replicate
    factors = list()

    # Define host into guest experiments.
    for replicate in range(1):
        name = 'host into %s' % guests[guest_index].name
        experiment = ITCHeuristicExperiment(
            name=name,
            syringe_source=host_solution,
            cell_source=guest_solutions[guest_index],
            protocol=binding_protocol,
            cell_concentration=0.5 * (ureg.millimole / ureg.liter) * cell_scaling,
            buffer_source=buffer_trough)
        # optimize the syringe_concentration using heuristic equations and known binding constants
        # TODO extract m, v and V0 from protocol somehow?
        experiment.heuristic_syringe(
            guest_compound_Ka[guest_index],
            10,
            3. * ureg.microliter,
            202.8 * ureg.microliter)
        # rescale if syringe > stock. Store factor.
        factors.append(experiment.rescale())
        host_guest_experiments.append(experiment)

    # Define buffer into guest experiments.
    for replicate in range(1):
        name = 'buffer into %s' % guests[guest_index].name
        experiment = ITCHeuristicExperiment(
            name=name,
            syringe_source=buffer_trough,
            cell_source=guest_solutions[guest_index],
            protocol=blank_protocol,
            cell_concentration=0.5 *
            ureg.millimole /ureg.liter,
            buffer_source=buffer_trough)
        # rescale to match host into guest experiment concentrations.
        experiment.rescale(tfactor=factors[replicate])
        buff_guest_experiments.append(experiment)

    # Add buffer to guest experiment(s) to set
    for buff_guest_experiment in buff_guest_experiments:
        itc_experiment_set.addExperiment(buff_guest_experiment)

    # Add host to guest experiment(s) to set
    for host_guest_experiment in host_guest_experiments:
        itc_experiment_set.addExperiment(host_guest_experiment)


# Add cleaning experiment.
#name = 'final cleaning water titration'
#itc_experiment_set.addExperiment( ITCExperiment(name=name, syringe_source=water_trough, cell_source=water_trough, protocol=cleaning_protocol) )

# Water control titrations.
nfinal = 2
for replicate in range(nfinal):
    name = 'final water into water test %d' % (replicate + 1)
    itc_experiment_set.addExperiment(
        ITCExperiment(
            name=name,
            syringe_source=water_trough,
            cell_source=water_trough,
            protocol=control_protocol))

# Check that the experiment can be carried out using available solutions
# and plates.

itc_experiment_set.validate(print_volumes=False, omit_zeroes=True)

# For convenience, source concentrations
#for g, guest in enumerate(guest_solutions, start=1):
#    print("guest%02d" % g, (guest.concentration.to('millimolar')))

#print("host", host_solution.concentration.to('millimolar'))

# For information, experimental conditions
for experiment in itc_experiment_set.experiments:
    try:
        print('\033[92m')
        print(experiment.name)
        print('\033[0m')
        guest_mol = ((experiment.cell_concentration * 202.8 * Quantity('microliter')).to('millimole'))
        host_mol = ((experiment.syringe_concentration * 30 * Quantity('microliter')).to('millimole'))
	
	print(experiment.cell_source.name, experiment.syringe_source.name, 'Rm (h/g) final' )
        print(guest_mol, host_mol, host_mol/guest_mol)

    except (AttributeError, TypeError):
        pass

# Write Tecan EVO pipetting operations.
worklist_filename = 'host-guest-itc.gwl'
itc_experiment_set.writeTecanWorklist(worklist_filename)

# Write Auto iTC-200 experiment spreadsheet.
excel_filename = 'host-guest-itc.xlsx'
itc_experiment_set.writeAutoITCExcel(excel_filename)
