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
        data: Dict[int, DataFrame]
    ) -> None:
        super().__init__(K, M, N, p, data)
        self.solution : LpProblem= LpProblem("UserScheduling", LpMaximize)

        self.set_problem(data)
        
    def set_problem(self, data):

        vars = []
        R = []
        P = []

        every_channel_allocated_constraint = []

        for n in data.keys():
            X_n = []
            for idx, row in data[n].iterrows():
                k = row['k']
                m = row['m']
                p_kmn = row['p_k,m,n']
                r_kmn = row['r_k,m,n']

                x = LpVariable(f"x_{int(k)},{int(m)},{int(n)}", 0, 1, None)
                
                X_n.append(x)
                vars.append(x)
                R.append(r_kmn)
                P.append(p_kmn)
            
            every_channel_allocated_constraint.append(
                lpSum(X_n) == 1
            )



        objective = lpSum([R[i] * vars[i] for i in range(len(vars))])
        constraint_power_budget = lpSum([P[i] * vars[i] for i in range(len(vars))])

        self.solution += objective, "objective"
        self.solution += constraint_power_budget <= self.p, "power_constraint"
        for constraint in every_channel_allocated_constraint:
            self.solution += constraint

    def solve(self, data = None):
        self.solution.solve()

    