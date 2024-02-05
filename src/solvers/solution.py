from typing import List, Dict
class Solution:
    def __init__(
        self,
        K : int,
        M : int,
        N : int,
        p : float, 
    ) -> None:
        
        self.K = K
        self.M = M
        self.N = N
        self.p = p
        
        self.__data_rate = 0
        self.__remaining_power_budget = p
        self.__solution : Dict[int, List] = dict()
        self.__fractional_allocation : bool = False

    def get_solution(self):
        return self.__solution

    def set_triple(
        self,
        k : int,
        m : int,
        n : int,
        p_kmn : float,
        r_kmn : float
    )-> None:
        
        self.__solution[n] = [k, m, p_kmn, r_kmn, f"x_{k},{m},{n} = 1"]

    def set_fractional_allocation(
        self,
        k : int,
        m : int,
        n : int,
        p_kmn : float,
        r_kmn : float
    ):
        k_1, m_1, p_1, r_1, _ = self.__solution[n]

        if p_kmn == p_1:
            
            pass


        else:    
            Lambda = self.__remaining_power_budget/(p_kmn - p_1)

            self.__solution[n] = [
                [k_1, m_1, p_1, r_1, f"x_{k},{m},{n} = {1-Lambda}"], 
                [k, m, p_kmn, r_kmn, f"x_{k},{m},{n} = {Lambda}"]
            ]

            self.consume_power_budget((p_kmn - p_1)*Lambda)
            self.add_data_rate((r_kmn- r_1)*Lambda)

            self.__fractional_allocation = True

    def has_fractional_allocation(self):
        return self.__fractional_allocation



    def get_solution_at_channel(
        self,
        n
    )-> List[float]:
        
        return self.__solution[n]

    def get_remaining_power_budget(self):
        return self.__remaining_power_budget
    
    def get_data_rate(self):
        return self.__data_rate
    
    def consume_power_budget(self, value : float):
        if value > self.__remaining_power_budget:
            raise ValueError(f"You can only consume at most the power you have available. Tryed to consume {value} but have only {self.__remaining_power_budget} available")

        self.__remaining_power_budget -= value

    def add_data_rate(self, value : float):
        self.__data_rate+= value

    def reset_data_rate(self):
        self.__init__(
            self.K,
            self.M,
            self.N,
            self.p,
        )


        