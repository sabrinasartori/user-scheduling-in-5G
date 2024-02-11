from typing import Dict
import pandas as pd
from tqdm import tqdm
class Parser:
    """Reads and parse raw files in the given format (K, M, N)
    """    
    def __init__(
        self, 
        filename: str
    ) -> None:
        
        self.filename = filename

    def read(self):
        """Reads dataset from the provided filename

        Returns:
            Dict: Information about the dataset
        """        
        
        self.M : int = None
        self.N : int = None
        self.K : int = None
        self.p : float = None

        self.data : Dict[int, pd.DataFrame] = {}

        with open(self.filename, 'r') as file:
            n,k = 0,0
            for idx, line in tqdm(enumerate(file)):
                numbers = [float(valor) for valor in line.split()]

                if idx >= 4:

                    if k == self.K:
                        k = 0

                        n+=1
                        if n == self.N:
                            n = 0


                    for m in range(self.M):
                        key = tuple([k,m])

                        if self.data[n].get(key) is None:
                            self.data[n][key] = [numbers[m]]
                        
                        else:
                            self.data[n][key].append(numbers[m])
                    k+=1

                elif idx == 0:
                    self.N = int(numbers[0])

                elif idx == 1:  
                    self.M = int(numbers[0])

                elif idx == 2:
                    self.K = int(numbers[0])
                
                else: #if idx == 3
                    self.p = numbers[0]
                    for i in range(self.N):
                        self.data[i] = {}


            self.data = self.__convert_to_dataset()

            return self.__dict__

    def __convert_to_dataset(self):

        for n, v in self.data.items():

            self.data[n] = pd.Series(v)\
                .reset_index()\
                .rename(columns={
                    "level_0": "k",
                    "level_1" : "m",
                })
            self.data[n]['n'] = n
            
            self.data[n]['p_k,m,n'] = self\
                .data[n][0]\
                .apply(lambda x: x[0])
            
            self.data[n]['r_k,m,n'] = self\
                .data[n][0]\
                .apply(lambda x: x[1])
            
            self.data[n] = self.data[n]\
                .drop(columns=0)
            
                        
        return self.data