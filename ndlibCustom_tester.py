import networkx as nx
import ndlib.models.ModelConfig as mc
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
from ndlib.viz.mpl.DiffusionPrevalence import DiffusionPrevalence

from ndlibCustom.SEIR_ASModel import SEIR_ASModel

# Network generation
g = nx.erdos_renyi_graph(1000, 0.1)

# Model selection
model = SEIR_ASModel(g)

# Model Configuration
cfg = mc.Configuration()
cfg.add_model_parameter('beta', 0.57)
cfg.add_model_parameter('gamma', 0.15)
cfg.add_model_parameter('alpha', 0.2)
cfg.add_model_parameter('kappa', 0.25)
cfg.add_model_parameter("fraction_infected", 0.05)
model.set_initial_status(cfg)

# Simulation execution
iterations = model.iteration_bunch(30,progress_bar=True)
trends = model.build_trends(iterations)

print(model.get_info())

viz = DiffusionTrend(model, trends)
p = viz.plot()

viz2 = DiffusionPrevalence(model, trends)
p2 = viz2.plot()
