from .CustomDiffusionModel import CustomDiffusionModel
import numpy as np
import future

__author__ = ["Gianmarco Rengucci"]
__license__ = "BSD-2-Clause"


class SEIR_ASModel(CustomDiffusionModel):

    def __init__(self, graph, seed=None):

        super(self.__class__, self).__init__(graph, seed)

        self.name = "SEIR_AS"

        self.available_statuses = {
            "Susceptible": 0,
            "Exposed_A": 1,
            "Exposed_S": 2,
            "Infected_A": 3,
            "Infected_S": 4,
            "Removed": 5
        }
        self.parameters = {
            "model": {
                "alpha": {
                    "descr": "Latent period (1/duration)",
                    "range": [0, 1],
                    "optional": False},
                "beta": {
                    "descr": "Infection rate",
                    "range": [0, 1],
                    "optional": False},
                "gamma": {
                    "descr": "Recovery rate",
                    "range": [0, 1],
                    "optional": False
                },
                "kappa": {
                    "descr": "A/S ratio for Symptomatic individuals",
                    "range": [0, 1],
                    "optional": False
                },
                "schools": {
                    "descr": "Whether the nodes of the school layer are isolated or not",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1
                },
                "tp_rate": {
                    "descr": "Whether if the infection rate depends on the number of infected neighbors",
                    "range": [0, 1],
                    "optional": True,
                    "default": 1
                }
            },
            "nodes": {},
            "edges": {},
        }

    def iteration(self, node_status=True):
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}
        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            if node_status:
                return {"iteration": 0, "status": actual_status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        
        for u in self.graph.nodes:

            u_status = self.status[u]
            eventp = np.random.random_sample()
            neighbors = self.graph.neighbors(u)
            if self.graph.directed:
                neighbors = self.graph.predecessors(u)

            if u_status == 0:  # Susceptible
                infected_neighbors = [v for v in neighbors if self.status[v] == 3 or self.status[v] == 4]
                
                if self.params['model']['schools'] == 0:
                    #Remove nodes connected via school layer
                    for v in infected_neighbors:
                        if self.graph.edges[(u,v)]['type'] == "school":
                            infected_neighbors.pop(v)
                    
                triggered = 1 if len(infected_neighbors) > 0 else 0
                if self.params['model']['tp_rate'] == 1:
                    if eventp < 1 - (1 - self.params['model']['beta']) ** len(infected_neighbors):
                        #Toss a coin for A/S
                        eventp = np.random.random_sample()
                        if eventp < self.params['model']['kappa']:
                            actual_status[u] = 2  # Exposed_S
                        else:
                            actual_status[u] = 1  # Exposed_A                  
                else:
                    #Build edges weight list, use np.mean as multiplier constant for beta value
                    mean_infection_weight = np.mean([self.graph.edges[(u,v)]['weight'] for v in infected_neighbors]) if len(infected_neighbors) > 0 else 0
                    if eventp < self.params['model']['beta'] * triggered * mean_infection_weight:
                        #Toss a coin for A/S
                        eventp = np.random.random_sample()
                        if eventp < self.params['model']['kappa']:
                            actual_status[u] = 2  # Exposed_S
                        else:
                            actual_status[u] = 1  # Exposed_A                            

            elif u_status == 1:     # Exposed_A
                # apply prob. of infection, after (t - t_i) 
                if eventp < self.params['model']['alpha']:
                    actual_status[u] = 3  # Infected_A
                    
            elif u_status == 2:     # Exposed_S
                # apply prob. of infection, after (t - t_i) 
                if eventp < self.params['model']['alpha']:
                    actual_status[u] = 4  # Infected_A

            elif u_status == 3 or u_status == 4:     # Infected_A or Infected_S
                if eventp < self.params['model']['gamma']:
                    actual_status[u] = 5  # Removed

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
