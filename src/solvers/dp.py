from src.solvers.base_solver import BaseSolver
from pandas.core.api import DataFrame as DataFrame
from src.solvers.base_solver import BaseSolver, DPMethods
import pandas as pd
from typing import Dict
from enum import Enum



class DPSolver(BaseSolver):
    def __init__(
        self, 
        K: int, 
        M: int, 
        N: int, 
        p: float, 
        data: Dict[int, DataFrame]
    ) -> None:
        super().__init__(K, M, N, p, data)

    def solve(
        self, 
        data,
        method : DPMethods,
        U : int = None
    ):
        self.solution.reset_data_rate()

        if method == DPMethods.MAXIMIZE_R:
            return self.DP1()
        
        if method == DPMethods.MINIMIZE_P:
            if U is None:
                raise TypeError("When using method MINIMIZE_P you must set an upper bound U")
            return self.DP2(U)
        
    def DP1(self):
        """Implementation that solves the ILP with 
        the method that maximizes R
        """        

        R = dict()
        

        for idx, row in self.data[0].iterrows():
            
            k, m= row['k'], row['m']
            r_kmn, p_kmn = row['r_k,m,n'], row['p_k,m,n']
            
            if p_kmn <= self.p: 

                R[tuple((0, p_kmn))] = r_kmn

        
        for n in range(1,self.N):
            R_1 = {}
            for idx, row in self.data[n].iterrows():
                
                r_kmn = row['r_k,m,n']
                p_kmn = row['p_k,m,n']

                for (n,p), r in R.items(): 

                    if p + p_kmn > self.p:
                        continue

                    key = tuple((n-1, p + p_kmn))

                    if R_1.get(key) is not None:
                        R_1[key] = max(r + r_kmn, R_1[key])
                    
                    else:
                        R_1[key] = r + r_kmn
            R = R_1       

        self.solution.add_data_rate( max(R.values()))
    
    def DP2(self, U : int):
        """Implementation of the greedy algorithm that minimizes P

        Args:
            U (int): maximum data rate
        """        
        P = {}

        for idx, row in self.data[0].iterrows():
            
            r_kmn, p_kmn = row['r_k,m,n'], row['p_k,m,n']

            key = tuple((0, r_kmn))
            if r_kmn <= U:
                P[key] = p_kmn

        for n in range(1,self.N):
            P_1 = {}
            for idx, row in self.data[n].iterrows():
            
                r_kmn = row['r_k,m,n']
                p_kmn = row['p_k,m,n']

                for key, p in P.items():

                    r = key[1]

                    if r + r_kmn <= U:
                        t = tuple((n, r + r_kmn))
                        
                        # if there exists another n, (r+r_kmn) key

                        if P_1.get(t) is not None:
                            P_1[t] = min(p + p_kmn, P_1[t])
                        else:
                            P_1[t] = p + p_kmn
            P = P_1
        
        # return maximal r
        r_max = -1
        for key, p in P.items():
            if key[0] != self.N-1:
                continue

            r = key[1]
            if r> r_max and p <= self.p:
                r_max = r 
            
        self.solution.add_data_rate(r_max)

