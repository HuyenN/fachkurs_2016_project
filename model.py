import modeldata
import molecules as mol
import translation


class Output:
    """
    class for handling the simulation results of the different species types
    """

    def __init__(self, model):
        self.meta = {}
        self.model = model
        self.timecourses = {state: SimulationResult(model.states[state]) for state in model.states}

    def add_timepoint(self, species):
        """
        add a simulation time point for one species
        @param species: mol.BioMolecule
        @return: None
        """
        if isinstance(self.model.states[species], mol.Polymer):
            pass  # TODO: implement a useful method for Polymers
        elif isinstance(self.model.states[species], mol.BioMoleculeCount):
            self.timecourses[species].add_timepoint(self.model.states[species].count, self.model.timestep)


class SimulationResult:
    """
    handles and stores a simulation result for one species
    """

    def __init__(self, species):
        self.name = species.name
        self.value = []
        self.time = []

    def add_timepoint(self, time, value):
        self.value.append(value)
        self.time.append(time)


class Model:
    """
    Initializes the states and processes for the model and lets the processes update their corresponding states.
    """

    def __init__(self):
        self.states = {} #dictionary
        self.processes = {}
        self.timestep = 0
        self.mrnas = {}  # all selfs should be initialized in the constructor
        self.ribosomes = {}
        self.volume = 1
        self.db = modeldata.ModelData()

        # ribosomes
        self.__initialize_ribosomes()
        # mRNAs
        self.__initialize_mRNA()

        self.__initialize_states()
        self.__initialize_processes()
        self.results = Output(self)  #

    def __initialize_ribosomes(self):
        self.ribosomes = {'Ribosomes': mol.Ribosome('Ribos', 'Ribosomes', 10)} 
        #dictionary with key:'Ribosome' and value: ribosome from type Ribosome(mid,name,count(so 10 ribosomes))

    def __initialize_mRNA(self):
        # I think to have a function for each molecule state generation is more intuitive and less error prone
        for i, mrna in enumerate(self.db.get_states(mol.MRNA)):
            mid, name, sequence = mrna
            self.mrnas[mid] = mol.MRNA(mid, name, sequence) 
            #mrna=[("MRNA_geneid_i", geneid/key, mrnasequence),(...]
            #for i, item in enumerate(L) <=> for i in range(len(L)):
                                                #item = L[i]
            #mrnas is a dictionary ??wie zugriff mit mid, ist doch leeres dictionary??

    def __initialize_states(self):
        """
        initialize the different states
        """

        self.states.update(self.ribosomes)
        self.states.update(self.mrnas)

    def __initialize_processes(self):
        trsl = translation.Translation(1, "Translation")
        trsl.set_states(self.mrnas.keys(), self.ribosomes.keys())
        self.processes = {"Translation": trsl}

    def step(self):
        """
        Do one update step for each process.

        """
        for p in self.processes:
            self.processes[p].update(self)

        for state in self.states:
            self.results.add_timepoint(state)

        self.timestep += 1

    def simulate(self, steps, log=True):
        """
        Simulate the model for some time.

        """
        for s in range(steps):
            self.step()
            if log:  # This could be an entry point for further logging
                # print count of each protein to the screen
                print('\r{}'.format([len(self.states[x]) for x in self.states.keys() if "Protein" in x]), end='')


if __name__ == "__main__":
    c = Model()
    c.simulate(100, log=True)
