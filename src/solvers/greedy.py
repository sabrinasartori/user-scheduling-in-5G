from typing import Dict
from pandas.core.api import DataFrame as DataFrame
from src.solvers.base_solver import BaseSolver
import pandas as pd

class GreedySolver(BaseSolver):
    
    def __init__(
        self, 
        K: int, 
        M: int, 
        N: int, 
        p: float, 
        data: Dict[int, DataFrame]
    ) -> None:
        super().__init__(K, M, N, p, data)




    def solve(self, data):
        
        for n in range(self.N):
            p_kmn = data[n]\
                .iloc[0]\
                ['p_k,m,n']
            
            r_kmn = data[n]\
                .iloc[0]\
                ['r_k,m,n']
            
            k = data[n]\
                .iloc[0]\
                ['k']
            
            m = data[n]\
                .iloc[0]\
                ['m']
            
            self.solution.consume_power_budget(p_kmn) 
            self.solution.add_data_rate(r_kmn)
            
            self.solution.set_triple(k,m,n,p_kmn, r_kmn)


        all_pairs = []
        for n in range(self.N):
            data[n]['inc_eff'] = \
                (data[n]['r_k,m,n'] - data[n].shift(1)['r_k,m,n'])/(data[n]['p_k,m,n'] - data[n].shift(1)['p_k,m,n'])
            all_pairs.append(data[n].dropna())

        all_pairs = pd.concat(all_pairs).reset_index(drop=True)

        sorted_by_eff = all_pairs.sort_values(by = "inc_eff", ascending=False)
        
        # greedy iteration

        best_k, best_m, best_n, best_p_kmn, best_r_kmn, sorted_by_eff = \
            self.popleft(sorted_by_eff.dropna())

        k,m, p_kmn, r_kmn, name = self.solution.get_solution_at_channel(best_n)

        while best_p_kmn - p_kmn <= self.solution.get_remaining_power_budget():

            self.solution.set_triple(
                int(best_k), 
                int(best_m),
                best_n,
                best_p_kmn,
                best_r_kmn
            )
            
            self.solution.consume_power_budget(best_p_kmn - p_kmn)

            self.solution.add_data_rate(best_r_kmn - r_kmn)
            
            if len(sorted_by_eff) > 0:
                best_k, best_m, best_n, best_p_kmn, best_r_kmn, sorted_by_eff = \
                    self.popleft(sorted_by_eff)
                
                k,m, p_kmn, r_kmn, name = self.solution.get_solution_at_channel(best_n)
            
            else: 
                break

        p_remaining = self.solution.get_remaining_power_budget()
        if p_remaining == 0:
            return 
        
        else :
            self.solution.set_fractional_allocation(
                int(best_k), 
                int(best_m),
                best_n,
                best_p_kmn,
                best_r_kmn
            )
            
