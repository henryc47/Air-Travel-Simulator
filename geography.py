import math as m
import numpy as np

radius = 6371;#radius of the earth in km, assuming a perfect sphere

#calculate the great circle distance between one point on the globe and all other points on the globe
def great_circle_distance(local_latitude,local_longitude,array_latitude,array_longitude):
    #source for formula is https://en.wikipedia.org/wiki/Great-circle_distance#Formulae
    #confirmed to work, 9/06/2020
    distance = radius*np.arccos((m.sin(local_latitude)*np.sin(array_latitude))+(m.cos(local_latitude)*np.cos(array_latitude)*np.cos(array_longitude-local_longitude)))
    return distance

#calculates the great circle distance between all point pairs in the provided array
def great_circle_array(latitude,longitude):
    length = len(latitude)#find how many locations are in our list, so we know how big to make the 2x2 zeros array
    #print(length)
    distance_array = np.zeros((length,length),dtype=float)
    #loop through all the latitude/longitude combinations
    for i in range(length):
        local_latitude = latitude[i]
        local_longitude = longitude[i]
        #get the great circle distance at each latitude/longitude combination
        distance_array[i] = great_circle_distance(local_latitude,local_longitude,latitude,longitude)
    
    return distance_array

