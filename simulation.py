import pandas as pd
import os

#simulation class to store the overall simulation
class Simulation():
    #create the simulation class
    def __init__(self):
        pass


    #load all the airports in the airport folder
    def load_airports(self,airport_folder='airport_csvs'):
        airport_filenames = get_filenames_in_folder(airport_folder)
        print(airport_filenames)





def get_filenames_in_folder(foldername):
    filenames = []
    for filename in os.listdir(foldername):
        filenames.append(filename)
    
    return filenames