import openmm as mm
import openmm.app as app
import openmm.unit as unit
import os

class Disordered_Life:
    def __init__(self, experiment_name, runtime, sampling, temperature):
        self.experiment_name = experiment_name
        self.runtime = int(runtime)
        self.sampling = int(sampling)
        self.temperature = temperature
        
    def execute(self):
        self.rerun()
                
    def rerun(self):
        ### LOAD SYSTEM ###
        system_xml = f'{self.experiment_name}.xml'
        with open(system_xml, 'r') as f:
            system = mm.XmlSerializer.deserialize(f.read())
        previous_xml = f'{self.experiment_name}_prev.xml'
        with open(previous_xml, 'r') as f:
            previous = mm.XmlSerializer.deserialize(f.read())
        top = app.PDBFile(f'{self.experiment_name}.pdb').getTopology()

        ### REMOVE RESTRAINTS
        for index, force in enumerate(system.getForces()):
            if isinstance(force, mm.CustomExternalForce):
                print(f'Removing external force {index}')
                system.removeForce(index)
                break
        
        ### INPUTS
        temperature = self.temperature *unit.kelvin
        friction_coeff = 1/unit.picosecond
        timestep = 10*unit.femtosecond
        
        ### COMPUTING ###
        properties = {'Precision': 'single'}
        platform_name = 'CUDA'
        platform = mm.Platform.getPlatformByName(platform_name)
        
        ### SETUP SIMULATION ###
        integrator = mm.LangevinMiddleIntegrator(temperature, friction_coeff, timestep)
        simulation = app.Simulation(top, system, integrator, platform, properties)
        simulation.context.setState(previous)

        ### REPORTERS ###
        dcd_reporter = app.DCDReporter(f'{self.experiment_name}.dcd', self.sampling, enforcePeriodicBox=True)
        state_data_reporter = app.StateDataReporter(f'{self.experiment_name}.csv', self.sampling, step=True, time=True, potentialEnergy=True,
                                                    kineticEnergy=True, totalEnergy=True, temperature=True, speed=True)
        simulation.reporters.append(dcd_reporter)
        simulation.reporters.append(state_data_reporter)
        
        ### RUN SIMULATION ###
        if os.path.isfile(f'{self.experiment_name}.check'):
            simulation.loadCheckpoint(f'{self.experiment_name}.check')
        if self.runtime == 0:
            simulation.runForClockTime(22)
        else:
            simulation.step(self.runtime)

        simulation.saveCheckpoint(f'{self.experiment_name}.check')
        state = simulation.context.getState(getPositions=True, getVelocities=True, getForces=True,enforcePeriodicBox=True)
        with open(f'{self.experiment_name}_prev.xml', 'w') as f:
            f.write(mm.XmlSerializer.serialize(state))

if __name__ == '__main__':
    exp = Disordered_Life('O62011', runtime = 0, sampling = 1e4, temperature = 293)
    exp.execute()