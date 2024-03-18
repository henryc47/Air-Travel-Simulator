#external packages
import pandas as pd
import numpy as np
import tqdm

#other project files
import geography as geo
import simulation as sim
import utility

#network class to store the transport network
class Network():
    
    #create the network class
    def __init__(self,parent : sim.Simulation) -> None:
        self.error_logging = parent.error_logging #take the error logging from the parent simulation
    
    #load up all the network data
    def setup_network(self) -> None:
        self.load_all_airports()
        self.load_all_ferries()
        self.load_all_roads()
        self.calculate_airport_statistics()
        self.calculate_travel_demand()

    #load all the airports from files in the airport folder
    def load_all_airports(self,airport_folder='airport_csvs'):
        self.create_airport_variables() #create the variables which store airport properties
        airport_filepaths = utility.get_filepaths_in_folder(airport_folder) #get every file in the airports folder
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
            relative_demand_to_others = self.airport_gdps_np*self.road_distance_metric_array[i,:]
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
        self.road_distance_metric_array =  np.reciprocal((self.great_circle_distance_array+50))

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
        self.airport_longitudes : list[float] = [] #longitudes of the airports
        self.airport_latitudes : list[float] = [] #latitudes of the airports
        self.airport_populations : list[float] = [] #population (k) in airports catchment region
        self.airport_gdp_per_heads : list[float] = [] #gdp per head ($k USD) in airports catchment region
        self.airport_name_indices_dict : dict[tuple[str,str,str],int] = {} #dictionary allowing fast lookup of index by unique name
    
    #store the coordinates of airports in a numpy array
    def store_coordinates_np(self):
        self.airport_longitudes_np = np.array(self.airport_longitudes,dtype=float)#longitude stored as a 1D numpy array
        self.airport_latitudes_np = np.array(self.airport_latitudes,dtype=float)#latitude stored as a 1D numpy array

    #store economic statistics about airport catchment area in a numpy array
    def store_economics_np(self):
        self.airport_populations_np = np.array(self.airport_populations)
        self.airport_gdp_per_heads_np = np.array(self.airport_gdp_per_heads)

    #load all the airports in one particular file
    def load_airports(self,filepath):
        df = pd.read_csv(filepath)
        self.get_airport_names(df)
        self.get_airport_coordinates(df)
        self.get_airport_economics(df)

    #extract coordinates of airports in a dataframe and store as appropriate
    def get_airport_coordinates(self,df : pd.DataFrame):
        num_airports = len(df)
        for i in range(num_airports):
            location : str = utility.convert_object_to_str(df.loc[i,"Location"])
            coordinates : list[str] = location.split(',')
            latitude : float = float(coordinates[0])
            longitude : float = float(coordinates[1])
            self.airport_longitudes.append(longitude)
            self.airport_latitudes.append(latitude)

    #extract names,states,countries of airports in a dataframe and store as appropriate
    def get_airport_names(self,df):
        num_airports = len(df)
        for i in range(num_airports):
            name : str = utility.convert_object_to_str(df.loc[i,"Name"])
            state : str = utility.convert_object_to_str(df.loc[i,"State"])
            country : str = utility.convert_object_to_str(df.loc[i,"Country"])
            unique_name : tuple[str,str,str] = (name,state,country)
            self.airport_names.append(name)
            self.airport_states.append(state)
            self.airport_countries.append(country)
            self.airport_unique_names.append(unique_name)
            index : int = len(self.airport_names)-1
            self.airport_name_indices_dict[unique_name] = index
    
    #import economic data about the airport's catchment zone
    def get_airport_economics(self,df : pd.DataFrame):
        num_airports = len(df)
        for i in range(num_airports):
            airport_population = float(df.loc[i,"Population (k)"])
            airport_gdp_per_captia = float(df.loc[i,"GDP/head ($k)"])
            self.airport_populations.append(airport_population)
            self.airport_gdp_per_heads.append(airport_gdp_per_captia)      

    #get the index of an airport from it's unique name
    def get_airport_index(self,unique_name : str) -> tuple[bool,int]:
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
    def display_airport_unique_name_components(self,name : str,state : str,country : str):
        unique_name : tuple[str,str,str] = (name,state,country)
        self.display_unique_name(unique_name)

    #display an airport with unique combination of name,state and country, using a tuple to represent the combination
    def display_unique_name(self,unique_name : str) -> None:
        found_airport,index = self.get_airport_index(unique_name)
        if found_airport:
            self.display_airport_data(index)

    #display the data for all airports
    def display_all_airport_data(self) -> None:
        num_airports = len(self.airport_names)
        for i in range(num_airports):
            self.display_airport_data(i)
    
    #display the data for a specific airport given by index
    def display_airport_data(self,index : int):
        print(self.airport_names[index],",",self.airport_states[index],",",self.airport_countries[index]," Lat = ",self.airport_latitudes_np[index]," Long = ",self.airport_longitudes_np[index],
              " GDP per captia = ",self.airport_gdp_per_heads_np[index]," Population = ",self.airport_populations_np[index]," GDP = ",self.airport_gdps_np[index])

    #load all ferries from files in the ferries folder
    def load_all_ferries(self,ferry_folder='ferry_csvs') -> None:
        self.create_ferry_variables() #create the variables which store ferry properties
        ferry_filepaths = utility.get_filepaths_in_folder(ferry_folder) #get every file in the ferry folder
        for ferry_filepath in tqdm.tqdm(ferry_filepaths,desc="Loading Ferry Data",disable=self.error_logging==False): #load the ferries from every file
            self.load_ferries(ferry_filepath)     

    #create the variables which store ferry properties
    def create_ferry_variables(self) -> None:
        self.ferry_names : list[str] = []
        self.ferry_id_by_name_dict : dict[str,int] = {}
        self.ferry_transport_time : list[float] = [] #transport time hours
        self.ferry_load_time_car : list[float] = [] #loading/unloading time for cars and buses
        self.ferry_load_time_pax : list[float] = [] #loading/unloading time for non-vehicle passengers
        self.ferry_car_cost : list[float] = [] #cost ($) for a car to use the ferry
        self.ferry_pax_cost : list[float] = [] #cost ($) for single passengers (non-vehicle and bus) to use the ferry
        self.ferry_frequency : list[int] = [] #ferry trips per week

    #load all the ferries in a CSV file
    def load_ferries(self,ferry_filepath : str) -> None:
        df = pd.read_csv(ferry_filepath)
        num_ferries = len(df)
        for i in range(num_ferries):
            name : str = utility.convert_object_to_str(df.loc[i,"Ferry Name"])
            transport_time : float = float(df.loc[i,"Transport Time"])
            load_time_car : float = float(df.loc[i,"Car Load + Unload Time"])
            load_time_pax : float = float(df.loc[i,"Pax Load Time"])
            cost_car : float = float(df.loc[i,"Car Cost"])
            pax_cost : float = float(df.loc[i,"Pax Cost"])
            frequency : float = float(df.loc[i,"Frequency"])
            self.ferry_names.append(name)
            self.ferry_transport_time.append(transport_time)
            self.ferry_load_time_car.append(load_time_car)
            self.ferry_load_time_pax.append(load_time_pax)
            self.ferry_car_cost.append(cost_car)
            self.ferry_pax_cost.append(pax_cost)
            self.ferry_frequency.append(frequency)
            index = len(self.ferry_names)-1
            #check if ferry is unique
            if name in self.ferry_id_by_name_dict:
                error_message = "Ferry name = " + name + " has already been used, ferry names must be unique"
                self.error_print(error_message) 
            else:
                self.ferry_id_by_name_dict[name] = index

    #load all roads from files in the roads folder, note this must be done after airport and ferry creation
    def load_all_roads(self,roads_folder='road_csvs'):
        self.create_road_variables() #create the variables which store airport properties
        roads_filepaths = utility.get_filepaths_in_folder(roads_folder) #get every file in the roads folder
        for roads_filepath in tqdm.tqdm(roads_filepaths,desc="Loading Road Network Data",disable=self.error_logging==False): #load the roads from every file
            self.load_roads(roads_filepath)

    #create the variables which store road properties
    def create_road_variables(self) -> None:
        self.road_start_unique_name : list[tuple[str,str,str]] = [] #start node unique name
        self.road_end_unique_name : list[tuple[str,str,str]] = [] #end node unique name
        self.road_start_indices : list[int] = [] #start node indices
        self.road_end_indices : list[int] = [] #end node indices
        self.road_distance : list[float] = [] #distance in km
        self.road_speed : list[float] = [] #travel speed in km/h
        self.road_time : list[float] = [] #default travel time, hrs
        self.road_has_ferry : list[bool] = [] #does the road have a ferry
        self.road_ferry_index : list[list[int]] = [] #what is the index of the roads ferry
        self.road_name_forward : list[tuple[str,str,str,str,str,str]] = []#unique name with start-end format
        self.road_name_reverse : list[tuple[str,str,str,str,str,str]] = []#unique name with end-start format
        self.road_start_end_indices_dict : dict[tuple[int,int],int] = {} #dictionary allowing fast lookup of road index by start-end node index
        self.road_end_start_indices_dict : dict[tuple[int,int],int] = {} #dictionary allowing fast lookup of road index by end-start node index
        self.road_name_forward_indices_dict : dict[tuple[str,str,str,str,str,str],int] = {} #dictionary allowing fast lookup of road index by unique name with start-end format
        self.road_name_reverse_indices_dict : dict[tuple[str,str,str,str,str,str],int] = {} #dictionary allowing fast lookup of road index by unique name with end-start format
        self.road_attached_nodes_dict : dict[tuple[str,str,str],list[tuple[int,int]]] = {} #dictionary allowing fast lookup of nodes (indice) and connecting road connected to a node recorded by unique name
        self.road_attached_nodes_dict_int : dict[int,list[tuple[int,int]]] = {}#as above, but with starting node and road recorded with index

    def load_roads(self,filepath : str) -> None:
        df = pd.read_csv(filepath)
        all_nodes_valid : bool = self.get_road_names(df)
        if not all_nodes_valid:
            self.error_print("Not all roads are valid airport pairs, terminating early")
            return
        else:
            ferries_valid = self.link_roads_with_ferries(df)
            if not ferries_valid:
                self.error_print("Some roads have invalid ferries, terminating early")
                return
            else:
                self.get_road_statistics(df)

    #extract names,states,countries of start and end nodes of roads in a dataframe and store as appropriate, return a boolean which will be false if not possible for all nodes
    def get_road_names(self,df : pd.DataFrame) -> bool:
        num_roads = len(df)
        all_nodes_valid = True
        for i in range(num_roads):
            start_name : str = utility.convert_object_to_str(df.loc[i,"Start Node"])
            start_state : str = utility.convert_object_to_str(df.loc[i,"Start State"])
            start_country : str = utility.convert_object_to_str(df.loc[i,"Start Country"])
            unique_name_start : tuple[str,str,str] = (start_name,start_state,start_country)
            end_name : str = utility.convert_object_to_str(df.loc[i,"End Node"])
            end_state : str = utility.convert_object_to_str(df.loc[i,"End State"])
            end_country : str = utility.convert_object_to_str(df.loc[i,"End Country"])
            unique_name_end : tuple[str,str,str] = (end_name,end_state,end_country)
            nodes_valid = self.check_road_nodes_valid(unique_name_start,unique_name_end,i)
            if not nodes_valid:
                all_nodes_valid = False
        return all_nodes_valid
    
    #check if start and end nodes are both existing unique airports, if so add them to the relevant data structures
    def check_road_nodes_valid(self,start_name : tuple[str,str,str],end_name : tuple[str,str,str],row : int) -> bool:
        valid : bool = True
        if (start_name not in self.airport_name_indices_dict):
            self.error_print("Node = " + utility.unique_airport_name_to_str(start_name) + " is not a valid airport at row " + str(row+2))
            valid = False
        if (end_name not in self.airport_name_indices_dict):
            self.error_print("Node = " + utility.get_filepaths_in_folderunique_airport_name_to_str(end_name) + " is not a valid airport at row " + str(row+2))
            valid = False
        if (start_name==end_name):
            self.error_print("Starting and Ending Nodes " + utility.unique_airport_name_to_str(start_name) + " and " + utility.unique_airport_name_to_str(end_name) + "the same at row " + str(row+2))
            valid = False
        if not valid:
            return valid
        else:
            #look up the index of the start and end node
            node_start_index : int = self.airport_name_indices_dict[start_name]
            node_end_index : int = self.airport_name_indices_dict[end_name]
            #create a unique name for the road in both start-end and end-start format, also store the related indices
            road_name_forward : tuple[str,str,str,str,str,str] = (start_name[0],start_name[1],start_name[2],end_name[0],end_name[1],end_name[2])
            road_name_reverse : tuple[str,str,str,str,str,str] = (end_name[0],end_name[1],end_name[2],start_name[0],start_name[1],start_name[2])
            road_node_indices_forward : tuple[int,int] = (node_start_index,node_end_index)
            road_node_indices_reverse : tuple[int,int] = (node_end_index,node_start_index)
            #if start and end node airports are both valid and unique, store their detail in the road data structures
            self.road_start_unique_name.append(start_name) 
            self.road_end_unique_name.append(end_name)
            self.road_start_indices.append(node_start_index)
            self.road_end_indices.append(node_end_index)   
            self.road_name_forward.append(road_name_forward) 
            self.road_name_reverse.append(road_name_reverse) 
            road_index : int = len(self.road_start_unique_name)-1
            self.road_start_end_indices_dict[road_node_indices_forward] = road_index
            self.road_end_start_indices_dict[road_node_indices_reverse] = road_index 
            self.road_name_forward_indices_dict[road_name_forward] = road_index 
            self.road_name_reverse_indices_dict[road_name_reverse] = road_index
            #implement road network creation by name and index here
            #starting at start node
            if node_start_index not in self.road_attached_nodes_dict_int:
                self.road_attached_nodes_dict_int[node_start_index] = []
                self.road_attached_nodes_dict[start_name] = []
            self.road_attached_nodes_dict_int[node_start_index].append((node_end_index,road_index))
            self.road_attached_nodes_dict[start_name].append((node_end_index,road_index))
            #starting at end node             
            if node_end_index not in self.road_attached_nodes_dict_int:
                self.road_attached_nodes_dict_int[node_end_index] = []
                self.road_attached_nodes_dict[end_name] = []
            self.road_attached_nodes_dict_int[node_end_index].append((node_start_index,road_index))
            self.road_attached_nodes_dict[end_name].append((node_start_index,road_index))  
            return valid
    
    #link roads with ferries
    def link_roads_with_ferries(self,df : pd.DataFrame) -> bool:
        num_roads = len(df)
        all_ferries_valid = True
        for i in range(num_roads):
            has_ferry_str : str = utility.convert_object_to_str(df.loc[i,"Has Ferry"])
            has_ferry : bool = has_ferry_str.lower()=="yes"
            self.road_has_ferry.append(has_ferry)
            if not has_ferry:
                self.road_ferry_index.append([-1]) #default ferry index is -1
            else:
                ferry_names_raw = utility.convert_object_to_str(df.loc[i,"Ferries"])
                ferry_names : list[str] = ferry_names_raw.split(',')
                ferry_indices : list[int] = []
                for ferry_name in ferry_names:
                    if ferry_name in self.ferry_id_by_name_dict:
                        ferry_indices.append(self.ferry_id_by_name_dict[ferry_name])
                    else:
                        message = "Ferry Name = " + ferry_name + " is not a recorded ferry"
                        self.error_print(message)
                        ferry_indices.append(-1) #default ferry index is -1
                        all_ferries_valid = False
            
                self.road_ferry_index.append(ferry_indices)

        return all_ferries_valid
    
    #load other statistics relating to a road 
    def get_road_statistics(self, df : pd.DataFrame) -> None:
        num_roads = len(df)
        for i in range(num_roads):
            road_distance : float = float(df.loc[i,"Distance (km)"]) 
            road_speed : float = float(df.loc[i,"Speed (km/h)"])
            road_time : float = road_distance/road_speed
            self.road_distance.append(road_distance)
            self.road_speed.append(road_speed)
            self.road_time.append(road_time)
