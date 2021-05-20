# force-bdss-plugin-surfactant-example
Example plugin for example surfactant formulation use-case. Requires a ``force-bdss`` installation, including the ``force-bdss-plugin-gromacs``
wrapper.

Additional modules that can contribute to the ``force-wfmanager`` UI are also included,
but a local version of ``force-wfmanager`` is not required in order to complete the 
installation.

### Installation Instructions

To install ``force-bdss`` and the ``force-wfmanager``, please see the following 
[instructions](https://github.com/force-h2020/force-bdss/blob/master/doc/source/installation.rst).

To install the ``force-bdss-plugin-gromacs`` package, please see the following [instructions](https://github.com/force-h2020/force-bdss-plugin-gromacs/blob/master/README.md)

Afterwards, clone the git repository

    git clone https://github.com/force-h2020/force-bdss-plugin-surfactant-example.git

After downloading, enter the source directory and run:

    python -m ci install

This will allow install the plugin in the `force-py36` edm environment, allowing the contributed BDSS objects to be visible by both ``force-bdss``
 and ``force-wfmanager`` applications.

### Plugin Functionality

This plugin takes in user input for a simulated experiment to be run using Gromacs molecular dynamics engine.
The MCO parameters refer to concentrations of ``Surfactant`` and ``Salt`` chemical species. There are 3 different
parameter types:

- ``FixedMCOParameter``: A parameter defining a fixed concentration
- ``RangedMCOParameter``: A parameter defining a range of concentrations between a lower and upper bound
- ``ListedMCOParameter``: A parameter defining a list of concentrations that have been inputted by the user

A typical set up contains 4 sequential layers containing with the following models:

1) ``Fragment``:
A Gromacs simulation is comprised of multiple molecular fragments, representing a molecular species connected by
covalent bonds. These fragments may be single or multiple particles and may or may not be charged. Initally they must
be defined and imported using the ``force-bdss-plugin-gromacs`` wrapper.

2) ``Ingredient``:
An ``Ingredient`` object represents a set of ``Fragments`` that form a neutral molecular species and can be assigned 
real-world attributes such as concentration and price. There are 3 different ingredient roles: ``Surfactant``, ``Salt``
and ``Solvent``, for which at least one ``Ingredient`` must be assigned to in any simulation (note: at the moment, the plugin only 
supports one solvent ``Ingredient`` per simulation). Additionally, any non-solvent ``Ingredients`` must also be assigned
a concentration, which can be inputted as an ``MCOParameter``.

3) ``Simulation``:
Each different ``Simulation`` takes in a set of chemical ``Ingredients`` and MD parameters. A script to run
a Gromacs MD simulation is then generated and ran locally if desired, or can be piped into a ``HPCWriter``
for preparation to be submitter to a remote cluster.

4) ``Cost`` + ``Micelle``:
This layer calctlates the KPIs required for the surfactant formulation use case: material cost and micelle aggregation number.
The ``Micelle`` calculator is expected to perform post-processing operations on the simulation output in order to
estimate the average micelle aggregation number of the mixture. Similarly, the ``Cost`` calculator is able to generate 
an estimate of material costs, proportional to the price and concentration of each ingredient.

### ContributedUI Functionality

A simplified UI is supplied for non-technical users. This allows for selection
of a primary surfactant and (optional) secondary surfactant, as well as
both the range of surfactant and salt concentrations to investigate.

The UI will then create Gromacs scripts to run a range of MD simulations using NaCl as
the salt ingredient and water as a solvent.
