import openmm as mm
import openmm.app as app
import openmm.unit as unit

### LOAD SYSTEM ###
system_xml = 'Q9TXM1.xml'
with open(system_xml, 'r') as f:
    system = mm.XmlSerializer.deserialize(f.read())
previous_xml = 'Q9TXM1_prev.xml'
with open(previous_xml, 'r') as f:
    previous = mm.XmlSerializer.deserialize(f.read())
top = app.PDBFile('Q9TXM1.pdb').getTopology()

### INPUTS
temperature = 300 *unit.kelvin
friction_coeff = 1/unit.picosecond
timestep = 10*unit.femtosecond
sampling = int(1e5)

### COMPUTING ###
properties = {'Precision': 'single'}
platform_name = 'CUDA'
platform = mm.Platform.getPlatformByName(platform_name)

### SETUP SIMULATION ###
integrator = mm.LangevinMiddleIntegrator(temperature, friction_coeff, timestep)
simulation = app.Simulation(top, system, integrator, platform, properties)
simulation.context.setState(previous)

### REPORTERS ###
dcd_reporter = app.DCDReporter('Q9TXM1.dcd', sampling, enforcePeriodicBox=True,append=True)
state_data_reporter = app.StateDataReporter('Q9TXM1.csv', sampling, step=True, time=True, potentialEnergy=True,
                                            kineticEnergy=True, totalEnergy=True, temperature=True, speed=True,append=True)
simulation.reporters.append(dcd_reporter)
simulation.reporters.append(state_data_reporter)

### RUN SIMULATION ###
simulation.runForClockTime(2)
simulation.saveState('Q9TXM1_prev.xml')
