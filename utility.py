#external packages
import os
import pandas as pd


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