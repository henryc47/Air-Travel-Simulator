import pandas as pd
import numpy as np
import os

#simulation class to store the overall simulation
class Simulation():
    #create the simulation class
    def __init__(self):
        pass


    #load all the airports from files in the airport folder
    def load_all_airports(self,airport_folder='airport_csvs'):
        self.create_airport_variables() #create the variables which store airport properties
        airport_filenames = get_filenames_in_folder(airport_folder) #get every file in the airports folder
        for airport_filename in airport_filenames: #load the airports from every file
            self.load_airports(airport_filename)
       
    
    #create the variables which store airport properties
    def create_airport_variables(self):
        self.airport_names : list[str] = [] #names of the airports
        self.airport_states : list[str] = [] #states of the airports
        self.airport_countries : list[str] = [] #countries of the airports
        self.airport_unique_names : list[tuple[str,str,str]] = [] #unique name of the airport, including name, state and country
        self.airport_name_indexs_dict : dict[tuple[str,str,str],int] = {} #dictionary allowing fast lookup of index by unique name
        self.airport_longitudes : list[float] = [] #longitudes of the airports
        self.airport_latitudes : list[float] = [] #latitudes of the airports

    #load all the airports in one particular file
    def load_airports(self,filename):
        df = pd.read_csv(filename)
        self.get_airport_names(df)

    #extract names,states,countries from a dataframe and store as appropriate
    def get_airport_names(self,df):
        print(df.keys())
        print("Name" in df)
        print("State" in df)
        new_airport_names = df["Name"]
        new_airport_states = df["State"]
        new_airport_countries = df["Country"]
        print(new_airport_names)
        print(new_airport_states)
        print(new_airport_countries)
    

def get_filenames_in_folder(foldername : str) -> list[str]:
    filenames : list[str] = []
    for filename in os.listdir(foldername):
        filename = os.path.join(foldername,filename)
        filenames.append(filename)
    
    return filenames