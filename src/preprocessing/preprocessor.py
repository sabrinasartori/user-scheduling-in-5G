import pandas as pd
from typing import Dict
from copy import deepcopy
from tqdm import tqdm
import numpy as np 

class Preprocessor:
    def __init__(
        self,
        K : int,
        M : int,
        N: int,
        p : float,
        data : Dict[int, pd.DataFrame]
    ) -> None:
        
        self.K = K
        self.M = M
        self.N = N
        self.p = p
        self.data = data

    def remove_trivial_values(self) -> Dict[int, pd.DataFrame]:
        """Remove unfeasible triplets k,m,n such that

        ` p_k,m,n + \sum p_min,n > p `

        Returns:
            Dict[int, pd.DataFrame]: pre-processed dataset
        """        

        new_dataset = deepcopy(self.data)

        sum_min = 0
        for n in tqdm(range(self.N)):

            p_min_n = new_dataset[n]['p_k,m,n'].min()

            sum_min += p_min_n

        for n in range(self.N):
            p_min_n = new_dataset[n]['p_k,m,n'].min()

            for idx, row in new_dataset[n].iterrows():
                p_kmn = row['p_k,m,n']

                if p_kmn + sum_min - p_min_n > self.p:
                    new_dataset[n].drop(index=idx, inplace=True)
                
        return new_dataset

    def remove_ip_dominated(self, dataset) -> Dict[int, pd.DataFrame]:
        """remove ip dominated terms, i.e. terms that contain a higher power consumption
        and a lower data rate

        Returns:
            Dict[int, pd.DataFrame]: _description_
        """        
        new_dataset = {}
        for n in tqdm(range(self.N)):
            if len(dataset[n]) == 0:
                continue

            sorted_by_power = dataset[n].sort_values(
                by = "p_k,m,n"
            )

            r_max = -np.inf
            p_last : float = None
            idx_last : int = None
            removed_last : bool = False
            for i, (idx, row) in enumerate(sorted_by_power.iterrows()):
                
                r_kmn = row['r_k,m,n']
                p_kmn = row['p_k,m,n']

                if r_max >= r_kmn:
                    sorted_by_power = sorted_by_power.drop(index= idx)
                    removed_last = True
                    
                elif p_kmn == p_last:
                    if not removed_last:
                        sorted_by_power= sorted_by_power.drop(index = idx_last)

                        # print("removing element already removed")
            
                if r_kmn > r_max:
                    removed_last = False
                    r_max = r_kmn

                p_last = p_kmn
                idx_last = idx

            new_dataset[n] = sorted_by_power
        return new_dataset

    def remove_lp_dominated(self, df):
        lp_dominated=  set([])

        dataset = deepcopy(df)
        for n in tqdm(range(self.N)):

            if len(dataset[n]) <= 2:
                continue

            idx1 = 0
            idx2 = 1
            idx3 = 2

            while idx3 < len(dataset[n]):

                l1 = dataset[n].iloc[idx1]
                r1 = l1['r_k,m,n']
                p1 = l1['p_k,m,n']

            
                l2 = dataset[n].iloc[idx2]
                r2 = l2['r_k,m,n']
                p2 = l2['p_k,m,n']

                l3 = dataset[n].iloc[idx3]
                r3 = l3['r_k,m,n']
                p3 = l3['p_k,m,n']

                if (r3-r2) * (p2-p1) >= (r2- r1) * (p3 - p2):
                    lp_dominated.add(tuple((l2.k, l2.m, n)))

                    if idx1 == 0:
                        idx2 = idx3
                        idx3 +=1
                        
                        if idx3 >= len(dataset[n]):
                            continue
                        l = dataset[n].iloc[idx3]
                        while tuple((l.k, l.m, l.n)) in lp_dominated:
                            idx3+=1
                            if idx3 >= len(dataset[n]):
                                continue
                            l = dataset[n].iloc[idx3]

                    else:
                        idx2 = idx1
                        idx1 -= 1

                        l = dataset[n].iloc[idx1]
                        while tuple((l.k, l.m, l.n)) in lp_dominated:
                            idx1-=1
                            if idx1 < 0:
                                continue
                            l = dataset[n].iloc[idx1]

                else:
                    idx1 = idx2
                    idx2 =idx3
                    idx3+=1

                    if idx3 >= len(dataset[n]):
                        continue
                    l = dataset[n].iloc[idx3]
                    while tuple((l.k, l.m, l.n)) in lp_dominated:
                        idx3+=1
                        if idx3 >= len(dataset[n]):
                            continue
                        l = dataset[n].iloc[idx3]

        for (k,m,n) in lp_dominated:

            idx_drop = dataset[n].query(f"k == {k} & m == {m}").index
            dataset[n] = dataset[n].drop(index=idx_drop)

        return dataset