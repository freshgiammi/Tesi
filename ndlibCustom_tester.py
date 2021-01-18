import networkx as nx
import ndlib.models.ModelConfig as mc
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
from ndlib.viz.mpl.DiffusionPrevalence import DiffusionPrevalence

from ndlibCustom.SEIR_ASModel import SEIR_ASModel
import numpy as np

# Network generation
g = nx.erdos_renyi_graph(1000, 0.1)
for i in list(g.edges()):
    g.edges[i]['weight'] = np.random.random_sample()

#CUSTOM SEIR_AS MODEL SIMULATION
print("Simulating...")

# Model selection
model = SEIR_ASModel(g)

# Model Configuration
cfg = mc.Configuration()
cfg.add_model_parameter('beta', 0.57) #Infection rate from I_A/S Neighbors
cfg.add_model_parameter('gamma', 0.15) #Recovery/Removal rate
cfg.add_model_parameter('alpha', 0.2) #Latent period
cfg.add_model_parameter('kappa', 0.25) #Symptomatic/Asymptomatic Ratio

#This parameter "smoothens" out the infection rate in the first iterations.
cfg.add_model_parameter('tp_rate', 1) #Infection rate does not depend on neighbour sample size

cfg.add_model_parameter("fraction_infected", 0.005) #Starting infected nodes
model.set_initial_status(cfg)

# Simulation execution
iteration = model.iteration_bunch(2,progress_bar=True)

