from abc import ABC, abstractmethod
from typing import Dict, List, Union
import pandas as pd
from src.solvers.solution import Solution

class BaseSolver(ABC):
    def __init__(
        self,
        K : int,
        M : int,
        N: int,
        p : float,
        data : Dict[int, pd.DataFrame]
    ) -> None:
        
        super().__init__()
        self.K = K
        self.M = M
        self.N = N
        self.p = p
        self.data = data

        self.solution : Solution = Solution(
            K,
            M,
            N,
            p
        )

    def popleft(self,df : pd.DataFrame) -> List[Union[int, float]]:
        """Remove first element (leftmost) of a dataframe, returning 
        the values of k, m, n, p_kmn, r_kmn and the new datafram

        Args:
            df (pd.DataFrame): dataframe containing as columns the keys
            "k", "m", "n", "p_kmn", "r_kmn"

        Returns:
            List[Union[int, float]]: k, m, n, p_kmn, r_kmn and the new datafram
        """        
        x = df.iloc[0]
        k = int(x.k)
        m = int(x.m)
        n = int(x.n)
        p_kmn = x['p_k,m,n']
        r_kmn = x['r_k,m,n']
        df = df.drop(index=x.name)

        return k,m,n, p_kmn, r_kmn, df
        

    @abstractmethod
    def solve(self, data):
        """Solves LP problems by different approaches

        Args:
            data (_type_): _description_
        """        
        ...
