#external packages
import pandas as pd
import numpy as np
#other project files
import network as net


#simulation class to store the overall simulation
class Simulation():
    #create the simulation class
    def __init__(self) -> None:
        self.error_logging : bool = True
    
    #setup the network class
    def setup_transport_network(self) -> None:
        self.network : net.Network = net.Network(self)
        self.network.setup_network()

    #print an error message if we have error logging enabled
    def error_print(self,message : str) -> None:
        if self.error_logging:
            print("ERROR : ",message)
        
#convert a unique airport name tuple to a single string
def unique_airport_name_to_str(unique_name : tuple[str,str,str]) -> str:
    output_name : str = unique_name[0] + "," +  unique_name[1] + "," + unique_name[2]
    return output_name

#convert a unique road name tuple to a single string
def unique_road_name_to_str(unique_name : tuple[str,str,str,str,str,str]) -> str:
    start_name : str = unique_airport_name_to_str((unique_name[0],unique_name[1],unique_name[2]))
    end_name : str = unique_airport_name_to_str((unique_name[3],unique_name[4],unique_name[5]))
    output_name : str = start_name + " to " + end_name
    return output_name

if __name__ == "__main__":
    s = Simulation()
    s.setup_transport_network()