import math as m
import numpy as np
import tqdm
import time

radius = 6371;#radius of the earth in km, assuming a perfect sphere

#calculate the great circle distance between one point on the globe and all other points on the globe
def get_great_circle_distance(local_latitude,local_longitude,array_latitude,array_longitude):
    #source for formula is https://en.wikipedia.org/wiki/Great-circle_distance#Formulae
    #confirmed to work, 9/06/2020
    distance = radius*np.arccos((m.sin(local_latitude)*np.sin(array_latitude))+(m.cos(local_latitude)*np.cos(array_latitude)*np.cos(array_longitude-local_longitude)))
    return distance

#wrapper for get_great_circle_distance_array, serving to convert degrees to radians
def get_great_circle_distance_array_degrees(latitude : np.ndarray,longitude : np.ndarray,verbose=True):
    latitude = np.radians(latitude)
    longitude = np.radians(longitude)
    distance_array = get_great_circle_distance_array(latitude,longitude,verbose=True)
    return distance_array

#calculates the great circle distance between all point pairs in the provided array
def get_great_circle_distance_array(latitude : np.ndarray,longitude : np.ndarray,verbose=True):
    length = len(latitude)#find how many locations are in our list, so we know how big to make the 2x2 zeros array
    distance_array = np.zeros((length,length),dtype=float)
    for i in tqdm.tqdm(range(length),desc="Calculating Great Circle Distances",disable = verbose==False):
        local_latitude = latitude[i]
        local_longitude = longitude[i]
        #get the great circle distance at each latitude/longitude combination
        distance_array[i] = get_great_circle_distance(local_latitude,local_longitude,latitude,longitude)
    
    return distance_array

def great_circle_test(num_examples,min_latitude,max_latitude,min_longitude,max_longitude):
    max_latitude = np.radians(max_latitude)
    min_latitude = np.radians(min_latitude)
    max_longitude = np.radians(max_longitude)
    min_longitude = np.radians(min_longitude)
    latitudes = (np.random.random_sample(size=num_examples)*(max_latitude-min_latitude))+min_latitude
    longitudes = (np.random.random_sample(size=num_examples)*(max_longitude-min_longitude))+min_longitude
    start_time = time.time()
    output = get_great_circle_distance_array(latitudes,longitudes)
    end_time = time.time()
    print('time to calculate pairs of ',num_examples,' airports = ',(end_time-start_time),' seconds')
    print('result')
    print(np.round(output))
    

