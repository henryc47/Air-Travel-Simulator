#external packages
import pandas as pd
import numpy as np
import os
import tqdm
#other project files
import geography as geo


#simulation class to store the overall simulation
class Simulation():
    #create the simulation class
    def __init__(self):
        self.error_logging = True

    #load all the airports from files in the airport folder
    def load_all_airports(self,airport_folder='airport_csvs'):
        self.create_airport_variables() #create the variables which store airport properties
        airport_filepaths = get_filepaths_in_folder(airport_folder) #get every file in the airports folder
        for airport_filepaths in tqdm.tqdm(airport_filepaths,desc="Loading Airport Data",disable=self.error_logging==False): #load the airports from every file
            self.load_airports(airport_filepaths)
        self.store_coordinates_np()
        self.store_economics_np()

    #calculate statistics relating to the airports which will remain constant over our simulation run
    def calculate_airport_statistics(self):
        self.calculate_great_circle_distances()
        self.calculate_distance_metric()
        self.calculate_economic_data()
        self.km_per_mil = 100#annual passenger (thousand)km per million dollars GDP, typically about 5'000km per pax per 50k so 100'000 is normal, this will be broke into categories later
        self.constant_km = 50#extra km's added onto each trip

    #calculate travel demand between all origin destination pairs
    def calculate_travel_demand(self):
        num_airports = len(self.airport_gdps_np)
        all_total_demand_to_others = []
        for i in tqdm.tqdm(range(num_airports),desc="Calculating Origin-Destination Travel Demand Between City Pairs",disable=self.error_logging==False): #calculate origin-destination travel demand
            relative_demand_to_others = self.airport_gdps_np*self.distance_metric_array[i,:]
            relative_demand_to_others[i] = 0 #remove demand to self
            total_relative_demand = np.sum(relative_demand_to_others)
            demand_fraction_to_others = relative_demand_to_others/total_relative_demand #calculate the fraction of demand from a origin going to each destination
            distance_adjusted_demand_fraction_to_others = np.divide(demand_fraction_to_others,self.great_circle_distance_array[i,:]+self.constant_km)
            distance_adjusted_demand_fraction_to_others[i] = 0 #remove demand to self
            total_demand = self.km_per_mil*self.airport_gdps_np[i]#total annual long distance passenger demand, in pax-km
            total_demand_to_others = distance_adjusted_demand_fraction_to_others*total_demand #total demand to each city, k pax/year
            all_total_demand_to_others.append(total_demand_to_others)
        
        self.all_demand_pairs_np = np.row_stack(all_total_demand_to_others)

    def calculate_great_circle_distances(self):
        self.great_circle_distance_array = geo.get_great_circle_distance_array_degrees(self.airport_latitudes_np,self.airport_longitudes_np,self.error_logging)
    
    #metric defining how willingness to travel (total km*pax to destination given all else equal) scales with distance, at the moment just using a reciprocal metric (so km traveled declines linerally with total km)
    def calculate_distance_metric(self):
        self.distance_metric_array =  np.reciprocal((self.great_circle_distance_array+50))

    #calculate all economic parameters relating to aircraft catchment area
    def calculate_economic_data(self):
        self.calculate_gdp()

    #calculate the total GDP of an airports catchment area
    def calculate_gdp(self):
        self.airport_gdps_np = np.multiply(self.airport_gdp_per_heads_np,self.airport_populations_np)

    #create the variables which store airport properties
    def create_airport_variables(self):
        self.airport_names : list[str] = [] #names of the airports
        self.airport_states : list[str] = [] #states of the airports
        self.airport_countries : list[str] = [] #countries of the airports
        self.airport_unique_names : list[tuple[str,str,str]] = [] #unique name of the airport, including name, state and country
        self.airport_name_indices_dict : dict[tuple[str,str,str],int] = {} #dictionary allowing fast lookup of index by unique name
        self.airport_longitudes : list[float] = [] #longitudes of the airports
        self.airport_latitudes : list[float] = [] #latitudes of the airports
        self.airport_populations : list[float] = [] #population (k) in airports catchment region
        self.airport_gdp_per_heads : list[float] = [] #gdp per head ($k USD) in airports catchment region
    
    #store the coordinates of airports in a numpy array
    def store_coordinates_np(self):
        self.airport_longitudes_np = np.array(self.airport_longitudes,dtype=float)#longitude stored as a 1D numpy array
        self.airport_latitudes_np = np.array(self.airport_latitudes,dtype=float)#latitude stored as a 1D numpy array

    #store economic statistics about airport catchment area in a numpy array
    def store_economics_np(self):
        self.airport_populations_np = np.array(self.airport_populations)
        self.airport_gdp_per_heads_np = np.array(self.airport_gdp_per_heads)

    #load all the airports in one particular file
    def load_airports(self,filename):
        df = pd.read_csv(filename)
        self.get_airport_names(df)
        self.get_airport_coordinates(df)
        self.get_airport_economics(df)

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
    
    #import economic data about the airport's catchment zone
    def get_airport_economics(self,df):
        num_airports = len(df)
        for i in range(num_airports):
            airport_population = float(df.loc[i,"Population (k)"])
            airport_gdp_per_captia = float(df.loc[i,"GDP/head ($k)"])
            self.airport_populations.append(airport_population)
            self.airport_gdp_per_heads.append(airport_gdp_per_captia)      

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
        print(self.airport_names[index],",",self.airport_states[index],",",self.airport_countries[index]," Lat = ",self.airport_latitudes_np[index]," Long = ",self.airport_longitudes_np[index],
              " GDP per captia = ",self.airport_gdp_per_heads_np[index]," Population = ",self.airport_populations_np[index]," GDP = ",self.airport_gdps_np[index])
    
def display_matrix_data(data):
    shape = data.shape
    for i in range(shape[0]):
        for j in range(shape[1]):
            print(int(data[i,j]),end=" ")
        print()

#get the path to all files in a folder
def get_filepaths_in_folder(foldername : str) -> list[str]:
    filenames : list[str] = []
    for filename in os.listdir(foldername):
        filename = os.path.join(foldername,filename)
        filenames.append(filename)
    
    return filenames

#convert pandas object to string, converting null to empty string
def convert_object_to_str(object) -> str:
    if pd.isnull(object):
         output : str = ""
    else:
        output : str = str(object)
    
    return output   

if __name__ == "__main__":
    s = Simulation()
    s.load_all_airports()
    s.calculate_airport_statistics()
    s.calculate_travel_demand()
    s.display_all_airport_data()
    display_matrix_data(s.all_demand_pairs_np)