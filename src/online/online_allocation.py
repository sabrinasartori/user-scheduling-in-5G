from typing import Dict
import pandas as pd
import numpy as np

class OnlineAllocation:
    """Generates and solves online scheduling problem 
    """    
    def __init__(
        self, 
        K: int, 
        M: int, 
        N: int, 
        p: float, 
        p_max : int,
        r_max : int
    ) -> None:
        
        self.K = K
        self.M = M
        self.N = N
        self.p = p
        self.p_max = p_max
        self.r_max = r_max

    def __generate(
        self,
        k : int,
    )-> Dict[int, pd.DataFrame]:  
        """Generates pairs (k,m,n) for a given user k

        * p_k,m,n is uniformly distributed in the set {1, ..., p_max}

        * r_k,m,n is uniformly distributed in the set {1, ..., r_max}

        Args:
            k (int): user we are generating pairs

        Returns:
            Dict[int, pd.DataFrame]: Generated data points
        """        
        data : Dict[int, pd.DataFrame] = {}
        for n in range(self.N):
            index = 0
            data[n] = pd.DataFrame([])
            for m in range(self.M):
                p_kmn = np.random.randint(1, self.p_max+1)
                r_kmn = np.random.randint(1, self.r_max+1)

                pair = {
                    "k": [k],
                    "m": [m],
                    "n": [n],
                    "p_k,m,n": [p_kmn],
                    "r_k,m,n": [r_kmn]
                }
                
                index += 1
                data[n] = pd.concat([data[n], pd.DataFrame(pair, index= [index])])


        return data
    
    @staticmethod
    def get_e_average(p_max : int, r_max : int) -> float:
        """Computes the expected value of r/p given that
        p and r follows uniform distributions on {1, ..., p_max},
        {1, ..., r_max}

        Args:
            p_max (int): upper bound of uniform distribution 
            r_max (int): upper bound of uniform distribution

        Returns:
            float: 
        """        
        e = 0 
        for p_i in range(1,p_max +1):
            for r_i in range(1, r_max + 1):
                
                e+= r_i/p_i

        return e/(p_max*r_max)
    
    def generate_and_solve(
        self,
    ):
        """_summary_

        Returns:
            Data rate, power used and data generated
        """           

        allocated_channels = set()
        data_rate = 0
        total_power = 0

        data : Dict[int , pd.DataFrame] = {n : pd.DataFrame([]) for n in range(self.N)}
        e_avg = OnlineAllocation.get_e_average(self.p_max, self.r_max)

        for k in range(self.K):
            data_k = self.__generate(k)

            for n in range(self.N):
                data[n] = pd.concat([data[n], data_k[n]]) 

                if n in allocated_channels:
                    continue
                
                best_p, best_r = None, None
                for idx, row in data_k[n].iterrows():
                    p_i = row['p_k,m,n']
                    r_i = row['r_k,m,n']

                    if p_i + total_power > self.p:
                        continue

                    if best_p is None:
                        best_p = p_i
                        best_r = r_i

                        continue
                    
                    if OnlineAllocation.compare(best_p, best_r, p_i, r_i,):
                        best_p = p_i
                        best_r = r_i

                if best_p is None:
                    continue
                
                # We don't have choice if we are on the last user
                if k == self.K-1:
                    allocated_channels.add(n)
                    data_rate += best_r
                    total_power += best_p

                else:

                    if OnlineAllocation.should_allocate(best_p, best_r, e_avg,):
                        allocated_channels.add(n)
                        data_rate += best_r
                        total_power += best_p


        return data_rate, total_power, data

    @staticmethod
    def compare(
        p1 : int, 
        r1 : int, 
        p2 : int, 
        r2 : int, 
    ):
        """Returns true if (p2, r2) is better than (p1, r1)

        Args:
            p1 (int)
            r1 (int)
            p2 (int)
            r2 (int)
        
        Returns:
            bool: If (p2, r2) is better than (p1,r1)
        """    
        return r2/p2 > r1/p1
        
    @staticmethod
    def should_allocate(p: int, r: int, expected_e: float):
        """Returns true if p/r >= the expected value of r/p

        Args:
            p (int): power consumption
            r (int): data rate
            expected_e (float): expected value of r/p

        Returns:
            bool: if p/r >= the expected value of r/p
        """    
        return r/p >= expected_e
        


        