from src.solvers.base_solver import BaseSolver
import pandas as pd
from typing import Dict
from pulp import *
from src.solvers.pulp_solver import PuLPSolver
class BBSolver(BaseSolver):
    def __init__(
        self, 
        K: int, 
        M: int, 
        N: int, 
        p: float, 
        data: Dict[int, pd.DataFrame]
    ) -> None:
        super().__init__(K, M, N, p, data)
        self.best_rate = -1

    @staticmethod
    def is_integer_solution(solution : LpProblem)-> bool:
        """Verifies if a solution is integer, i.e. if all variables 
        are in {0,1}

        Args:
            solution (LpProblem): 

        Returns:
            bool: If the solution is integer
        """        
        for var in solution.variables():
            v = var.value()
            if int(v) != v:
                return False
        
        return True

    def solve(self, data = None):
        solver = PuLPSolver(
            self.K,
            self.M,
            self.N,
            self.p,
            self.data
        )
        self.solve_rec(
            solver,
            0,
            self.p,
            self.data
        )

        return self.best_rate

    def solve_rec(
        self,
        solver : PuLPSolver, 
        n0, 
        p, 
        data : Dict[int, pd.DataFrame]
    ):
        
        solver.solve()

        if n0 == self.N-1:
            data_rate =solver.solution.objective.value()
            if data_rate > self.best_rate:
                self.best_rate = data_rate

            return
        
        if solver.solution.status != 1:
            return
        
        data_rate = solver.solution.objective.value()
        if BBSolver.is_integer_solution(solver.solution):
            if data_rate > self.best_rate:
                self.best_rate = data_rate

            return
        
        if data_rate < self.best_rate + 1:
            return

        for idx, row in data[n0].iterrows():


            k = row['k']
            m = row['m']
            p_kmn = row['p_k,m,n']

            x_kmn = solver.get_variable(k,m,n0)
            solver.solution.addConstraint(x_kmn == 1)

            self.solve_rec(
                solver,
                n0+1,
                p,
                data
            )

            solver.solution.constraints.popitem(-1)