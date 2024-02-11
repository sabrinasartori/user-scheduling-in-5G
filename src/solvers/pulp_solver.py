from typing import Dict
from pandas.core.api import DataFrame as DataFrame
from src.solvers.base_solver import BaseSolver
import pandas as pd
from pulp import *

class PuLPSolver(BaseSolver):
    def __init__(
        self, 
        K: int, 
        M: int, 
        N: int, 
        p: float, 
        data: Dict[int, DataFrame],
        ilp : bool = False,
        n0: int = 0,
    ) -> None:
        super().__init__(K, M, N, p, data)
        self.solution : LpProblem= LpProblem("UserScheduling", LpMaximize)
        self.n0 = n0
        self.ilp = ilp

        self.set_problem(data, n0)

    def get_variable(
        self,
        k : int,
        m : int,
        n : int
    ):
        if self.__variables.get(f"x_{int(k)},{int(m)},{int(n)}") is None:
            return None
        return self.__variables[f"x_{int(k)},{int(m)},{int(n)}"]
        
        
    def set_problem(
        self, 
        data, 
        n0 : int = 0,
    ):
        """Set variable problems on the PuLP 
        format

        Args:
            data : data points k,m,n, p_kmn, r_kmn
            n0 (int, optional): Suppose the problem is solved until the channel n0. Defaults to 0.
        """        

        vars = []
        self.__variables = {}
        R = []
        P = []

        every_channel_allocated_constraint = []

        for n in data.keys():
            if n < n0:
                continue
            X_n = []
            for idx, row in data[n].iterrows():
                k = row['k']
                m = row['m']
                p_kmn = row['p_k,m,n']
                r_kmn = row['r_k,m,n']

                if self.ilp:
                    x = LpVariable(f"x_{int(k)},{int(m)},{int(n)}", 0, 1, LpInteger)
                
                else:
                    x = LpVariable(f"x_{int(k)},{int(m)},{int(n)}", 0, 1, None)
                    
                self.__variables[f"x_{int(k)},{int(m)},{int(n)}"] = x
                
                X_n.append(x)
                vars.append(x)
                R.append(r_kmn)
                P.append(p_kmn)
            
            every_channel_allocated_constraint.append(
                lpSum(X_n) == 1
            )



        objective = lpSum([R[i] * vars[i] for i in range(n0, len(vars))])
        constraint_power_budget = lpSum([P[i] * vars[i] for i in range(n0, len(vars))])

        self.solution += objective, "objective"
        self.solution += constraint_power_budget <= self.p, "power_constraint"
        for constraint in every_channel_allocated_constraint:
            self.solution += constraint

    def solve(self, data = None):
        self.solution.solve(PULP_CBC_CMD(msg=0))

    def get_data_rate(self):
        return self.solution.objective.value()

    