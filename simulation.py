import pandas as pd
import numpy as np
import os

#simulation class to store the overall simulation
class Simulation():
    #create the simulation class
    def __init__(self):
        self.error_logging = True


    #load all the airports from files in the airport folder
    def load_all_airports(self,airport_folder='airport_csvs'):
        self.create_airport_variables() #create the variables which store airport properties
        airport_filepaths = get_filepaths_in_folder(airport_folder) #get every file in the airports folder
        for airport_filepaths in airport_filepaths: #load the airports from every file
            self.load_airports(airport_filepaths)
       
    
    #create the variables which store airport properties
    def create_airport_variables(self):
        self.airport_names : list[str] = [] #names of the airports
        self.airport_states : list[str] = [] #states of the airports
        self.airport_countries : list[str] = [] #countries of the airports
        self.airport_unique_names : list[tuple[str,str,str]] = [] #unique name of the airport, including name, state and country
        self.airport_name_indices_dict : dict[tuple[str,str,str],int] = {} #dictionary allowing fast lookup of index by unique name
        self.airport_longitudes : list[float] = [] #longitudes of the airports
        self.airport_latitudes : list[float] = [] #latitudes of the airports

    #load all the airports in one particular file
    def load_airports(self,filename):
        df = pd.read_csv(filename)
        self.get_airport_names(df)
        self.get_airport_coordinates(df)

    #extract coordinates of airports in a dataframe and store as appropriate
    def get_airport_coordinates(self,df):
        num_airports = len(df)
        for i in range(num_airports):
            location : str = convert_object_to_str(df.loc[i,"Location"])
            coordinates = location.split(',')
            latitude = coordinates[0]
            longitude = coordinates[1]
            self.airport_longitudes.append(longitude)
            self.airport_latitudes.append(latitude)

    #extract names,states,countries of airports in a dataframe and store as appropriate
    def get_airport_names(self,df):
        num_airports = len(df)
        for i in range(num_airports):
            name : str = convert_object_to_str(df.loc[i,"Name"])
            state : str = convert_object_to_str(df.loc[i,"State"])
            country : str = convert_object_to_str(df.loc[i,"Country"])
            unique_name : tuple[str,str,str] = (name,state,country)
            self.airport_names.append(name)
            self.airport_states.append(state)
            self.airport_countries.append(country)
            self.airport_unique_names.append(unique_name)
            index : int = len(self.airport_names)-1
            self.airport_name_indices_dict[unique_name] = index
    
    #get the index of an airport from it's unique name
    def get_airport_index(self,unique_name) -> tuple[bool,int]:
        index = -1
        found_airport = False
        if unique_name in self.airport_name_indices_dict:
            index = self.airport_name_indices_dict[unique_name]
            found_airport = True
        else:
            if self.error_logging:
                print(unique_name, " not found in the dictionary")
        return found_airport,index

    #display an airport with unique combination of name,state and country, using each component individually
    def display_airport_unique_name_components(self,name,state,country):
        unique_name : tuple[str,str,str] = (name,state,country)
        self.display_unique_name(unique_name)

    #display an airport with unique combination of name,state and country, using a tuple to represent the combination
    def display_unique_name(self,unique_name):
        found_airport,index = self.get_airport_index(unique_name)
        if found_airport:
            self.display_airport_data(index)

    #display the data for all airports
    def display_all_airport_data(self):
        num_airports = len(self.airport_names)
        for i in range(num_airports):
            self.display_airport_data(i)
    
    #display the data for a specific airport given by index
    def display_airport_data(self,index):
        print(self.airport_names[index],",",self.airport_states[index],",",self.airport_countries[index]," Lat = ",self.airport_latitudes[index]," Long = ",self.airport_longitudes[index])
        
    
#get the path to all files in a folder
def get_filepaths_in_folder(foldername : str) -> list[str]:
    filenames : list[str] = []
    for filename in os.listdir(foldername):
        filename = os.path.join(foldername,filename)
        filenames.append(filename)
    
    return filenames

#convert pandas object to string
def convert_object_to_str(object) -> str:
    if pd.isnull(object):
         output : str = ""
    else:
        output : str = str(object)
    
    return output
        

if __name__ == "__main__":
    s = Simulation()
    s.load_all_airports()
    s.display_all_airport_data()