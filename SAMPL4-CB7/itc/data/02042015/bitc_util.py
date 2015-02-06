#!/usr/bin/python
"""
A module implementing Bayesian analysis of isothermal titration calorimetry (ITC) experiments

Written by John D. Chodera <jchodera@gmail.com>, Pande lab, Stanford, 2008.

Copyright (c) 2008 Stanford University.  All Rights Reserved.

All code in this repository is released under the GNU General Public License.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.

NOTES
* Throughout, quantities with associated units employ the pint Quantity class to store quantities
in references units.  Multiplication or division by desired units should ALWAYS be used to
store or extract quantities in the desired units.

"""
import os

from os.path import basename, splitext
import numpy
import logging
from bitc.units import ureg, Quantity
import pymc
from bitc.report import Report, analyze
from bitc.parser import optparser
from bitc.experiments import Injection, Experiment
from bitc.instruments import known_instruments, Instrument
from bitc.models import RescalingStep, known_models
import sys

def compute_normal_statistics(x_t):

    # Compute mean.
    x = x_t.mean()

    # Compute stddev.
    dx = x_t.std()

    # Compute 95% confidence interval.
    ci = 0.95
    N = x_t.size
    x_sorted = numpy.sort(x_t)
    low_index = round((0.5-ci/2.0)*N)
    high_index = round((0.5+ci/2.0)*N)
    xlow = x_sorted[low_index]
    xhigh = x_sorted[high_index]

    return [x, dx, xlow, xhigh]


validated = optparser()

# Process the arguments
working_directory = validated['<workdir>']

if not os.path.exists(working_directory):
    os.mkdir(working_directory)

os.chdir(working_directory)

# Set the logfile
if validated['--log']:
    logfile = '%(--log)s' % validated
else:
    logfile = None

# Level of verbosity in log
if validated['-v'] == 3:
    loglevel = logging.DEBUG
elif validated['-v'] == 2:
    loglevel = logging.INFO
elif validated['-v'] == 1:
    loglevel = logging.WARNING
else:
    loglevel = logging.ERROR

# Set up the logger
logging.basicConfig(format='%(levelname)s::%(module)s:L%(lineno)s\n%(message)s', level=loglevel, filename=logfile)

# Files for procesysing
filename = validated['<datafile>']  # .itc file to process

if not validated['--name']:
    # Name of the experiment, and output files
    experiment_name, file_extension = splitext(basename(filename))
else:
    experiment_name = validated['--name']

# If this is a file, it will attempt to read it like an origin file and override heats in experiment.
integrated_heats_file = validated['--heats']  # file with integrated heats

if validated['mcmc']:
    # MCMC settings
    nfit = validated['--nfit']      # number of iterations for maximum a posteriori fit
    niters = validated['--niters']  # number of iterations
    nburn = validated['--nburn']    # number of burn-in iterations
    nthin = validated['--nthin']    # thinning period
    Model = known_models[validated['--model']]  # Model type for mcmc

if validated['--instrument']:
    # Use an instrument from the brochure
    instrument = known_instruments[validated['--instrument']]()
else:
    # Read instrument properties from the .itc file
    instrument = Instrument(itcfile=filename)

logging.debug("Received this input from the user:")
logging.debug(str(validated))
logging.debug("Current state:")
logging.debug(str(locals()))

# TODO update code below this point

# Close all figure windows.
import pylab
pylab.close('all')
logging.info("Reading ITC data from %s" % filename)

experiment = Experiment(filename, experiment_name)
logging.debug(str(experiment))
#  TODO work on a markdown version for generating reports. Perhaps use sphinx
analyze(experiment_name, experiment)
# Write Origin-style integrated heats.
filename = experiment_name + '-integrated.txt'
experiment.write_integrated_heats(filename)

# Override the heats if file specified.
if integrated_heats_file:
    experiment.read_integrated_heats(integrated_heats_file)

# MCMC inference
if not validated['mcmc']:
    sys.exit(0)

# Construct a Model from Experiment object.
import traceback
try:
    model = Model(experiment, instrument)
except Exception as e:
    logging.error(str(e))
    logging.error(traceback.format_exc())
    raise Exception("MCMC model could not me constructed!\n" + str(e))

# First fit the model.
# TODO This should be incorporated in the model. Perhaps as a model.getSampler() method?
logging.info("Fitting model...")
map = pymc.MAP(model)
map.fit(iterlim=nfit) # 20000
logging.info(map)

logging.info("Sampling...")
model.mcmc.sample(iter=niters, burn=nburn, thin=nthin, progress_bar=True)
#pymc.Matplot.plot(mcmc)

# Plot individual terms.
if experiment.cell_concentration > Quantity('0.0 molar'):
    pymc.Matplot.plot(model.mcmc.trace('P0')[:] , '%s-P0' % experiment_name)
if experiment.syringe_concentration > Quantity('0.0 molar'):
    pymc.Matplot.plot(model.mcmc.trace('Ls')[:] , '%s-Ls' % experiment_name)
pymc.Matplot.plot(model.mcmc.trace('DeltaG')[:] , '%s-DeltaG' % experiment_name)
pymc.Matplot.plot(model.mcmc.trace('DeltaH')[:] , '%s-DeltaH' % experiment_name)
pymc.Matplot.plot(model.mcmc.trace('DeltaH_0')[:] , '%s-DeltaH_0' % experiment_name)
pymc.Matplot.plot(numpy.exp(model.mcmc.trace('log_sigma')[:]), '%s-sigma' % experiment_name)

#  TODO: Plot fits to enthalpogram.
#experiment.plot(model=model, filename='%s-enthalpogram.png' %  experiment_name) # todo fix this

# Compute confidence intervals in thermodynamic parameters.
outfile = open('%s.confidence-intervals.out' % experiment_name, 'a+')
outfile.write('%s\n' % experiment_name)
[x, dx, xlow, xhigh] = compute_normal_statistics(model.mcmc.trace('DeltaG')[:] )
outfile.write('DG:     %8.2f +- %8.2f kcal/mol     [%8.2f, %8.2f] \n' % (x, dx, xlow, xhigh))
[x, dx, xlow, xhigh] = compute_normal_statistics(model.mcmc.trace('DeltaH')[:] )
outfile.write('DH:     %8.2f +- %8.2f kcal/mol     [%8.2f, %8.2f] \n' % (x, dx, xlow, xhigh))
[x, dx, xlow, xhigh] = compute_normal_statistics(model.mcmc.trace('DeltaH_0')[:] )
outfile.write('DH0:    %8.2f +- %8.2f ucal         [%8.2f, %8.2f] \n' % (x, dx, xlow, xhigh))
[x, dx, xlow, xhigh] = compute_normal_statistics(model.mcmc.trace('Ls')[:] )
outfile.write('Ls:     %8.2f +- %8.2f uM           [%8.2f, %8.2f] \n' % (x, dx, xlow, xhigh))
[x, dx, xlow, xhigh] = compute_normal_statistics(model.mcmc.trace('P0')[:] )
outfile.write('P0:     %8.2f +- %8.2f uM           [%8.2f, %8.2f] \n' % (x, dx, xlow, xhigh))
[x, dx, xlow, xhigh] = compute_normal_statistics(numpy.exp(model.mcmc.trace('log_sigma')[:]) )
outfile.write('sigma:  %8.5f +- %8.5f ucal/s^(1/2) [%8.5f, %8.5f] \n' % (x, dx, xlow, xhigh))
outfile.write('\n')
outfile.close()
