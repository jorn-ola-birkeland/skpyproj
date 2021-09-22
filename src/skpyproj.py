
"""Transforms coordinates based on pyproj and EPSG codes

Authors:
--------

* Sveinung Himle <himsve@kartverket.no>


Description:
------------


Example:
--------

    >>> python input.csv output.csv 7789 4936

    input.csv is at the format ID(pointname) X Y Z Epoch

"""

# Standard library imports
import numpy as np
import argparse
import csv as csvinput
import os

# External library imports
from pyproj import Transformer, transform
from pyproj.aoi import AreaOfInterest, AreaOfUse, BBox
from pyproj.database import query_utm_crs_info, query_crs_info
from pyproj.datadir import get_data_dir

# Internal library imports
from utilies import get_boundary

parser = argparse.ArgumentParser(description='Transforms coordinates from csv files at format ID(pointname) x y z epoc).')

parser.add_argument('epsgsource', metavar='EPSGSource', type=int, help='EPSG code source crs')
parser.add_argument('epsgtarget', metavar='EPSGTarget', type=int, help='EPSG code target crs')
parser.add_argument('--input', metavar='InputFile', type=str, help='Path to input csv file', )
parser.add_argument('--output', metavar='OutputFile', type=str, help='Path to output csv file')
parser.add_argument('--area', metavar = "Area", type=int, help = 'EPSG code area extent')

args = parser.parse_args()
print('args is: ', args)

outputFile = None

if args.input is not None:
    inFileName = args.input
else:
    inFileName = ""    

if args.output is not None:
    outFileName = args.output
else:
    outFileName = ""

if outFileName != "":
    outputFile = open(outFileName, "w")

epsgsource = args.epsgsource
epsgtarget = args.epsgtarget

if args.area is not None:
    area = args.area
    connectionString = get_data_dir() + '\proj.db'
    bound = get_boundary(connectionString, area)
    transformer = Transformer.from_crs(epsgsource, epsgtarget, area_of_interest = bound)
else:
    transformer = Transformer.from_crs(epsgsource, epsgtarget)

pointCount = 0

if os.path.exists(inFileName):
    with open(inFileName) as csvfile:
        spamreader = csvinput.reader(csvfile, skipinitialspace = True, delimiter=' ', quotechar='|')
        for row in spamreader:        
            while ('' in row) : row.remove('')

            if len(row) < 3:
                continue

            id = row[0]
            x = float(row[1]) if len(row) > 1 else 0
            y = float(row[2]) if len(row) > 2 else 0
            z = float(row[3]) if len(row) > 3 else 0
            e = float(row[4]) if len(row) > 4 else 0

            if len(row) == 3:
                res = transformer.transform(x, y)
                L = [id + ' ' + str(res[0]) + ' ' + str(res[1])]
            elif len(row) == 4:
                res = transformer.transform(x, y, z)
                L = [id + ' ' + str(res[0]) + ' ' + str(res[1]) + ' ' + str(res[2])]
            else:
                res = transformer.transform(x, y, z, e)
                L = [id + ' ' + str(res[0]) + ' ' + str(res[1]) + ' ' + str(res[2]) + ' ' + str(res[3])]
           
            pointCount = pointCount + 1

            if outputFile is not None:
                outputFile.writelines(L)
                outputFile.writelines('\n')

            print("Source coordinates: ", row)
            print("Target coordinates: ", L)
else:
    while True:
        inputcoord = input("Enter input coordinates (X Y Z Epoch): ")
        
        if inputcoord == '' or inputcoord.lower() == 'exit' or inputcoord.lower() == 'quit':
            break

        splitline = inputcoord.split()
        if len(splitline) == 2:
            x = float(splitline[0])
            y = float(splitline[1])
            res = transformer.transform(x, y)
            L = [str(res[0]) + ' ' + str(res[1])]
        elif len(splitline) ==3:        
            x = float(splitline[0])
            y = float(splitline[1])
            z = float(splitline[2])
            res = transformer.transform(x, y, z)
            L = [str(res[0]) + ' ' + str(res[1]) + ' ' + str(res[2])]          
        elif len(splitline) == 4:
            x = float(splitline[0])
            y = float(splitline[1])
            z = float(splitline[2])
            e = float(splitline[3])
            res = transformer.transform(x, y, z, e)
            L = [str(res[0]) + ' ' + str(res[1]) + ' ' + str(res[2]) + ' ' + str(res[3])]

        pointCount = pointCount + 1

        print(L)

        if outputFile is not None:
            outputFile.writelines(L)
            outputFile.writelines('\n')

if outputFile is not None:
    outputFile.close()

print('Transformations succeed!')
print(f'{pointCount} points were transformed')

#if __name__ == '__main__':
