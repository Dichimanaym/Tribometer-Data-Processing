
# coding: utf-8

# In[52]:

#Convert file from notebook to script
#get_ipython().system('jupyter nbconvert --to script Tribometer_Data_Processing.ipynb')


# In[35]:

#All the relevant imports
import numpy as np
import os
import csv
import math
import matplotlib.pyplot as plt
import pandas
import scipy.signal as signal
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory


# In[36]:

#Creates the filepath for output file
def outify(fileName):
    return fileName.replace('.csv', '_OUT.csv')


# In[37]:

#Determines whether an output file already exists, so that previous functions are not accidentally overwritten
def findOut(fileName):
    out = outify(fileName)
    if os.path.isfile(out) == True:
        return out
    else:
        return fileName


# In[38]:

#Define a function which retrieves a CSV file
def selectFile():
    root = Tk()
    ftypes = [('CSV File',"*.csv")]
    ttl  = "Select file"
    fileName = askopenfilename(filetypes = ftypes, title = ttl)
    root.destroy()
    return fileName


# In[39]:

#Define a function which retrieves the headers and then the data, as rows, of a CSV
def getRows(fileName):
    rows = []
    with open(findOut(fileName) ,newline='') as f:
        reader = csv.reader(f)
        header1 = next(reader)
        header2 = next(reader)
        header3 = next(reader)
        for row in reader:
            rows.append(row)
        return rows, header1, header2, header3


# In[40]:

#Write data to "output" csv
def write(fileName, rows, header1, header2, header3):
    
    outFile=outify(fileName)
    outFile=outFile.replace('_OUT_OUT', '_OUT')
    
    with open(outFile, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header1)
        writer.writerow(header2)
        writer.writerow(header3)
        writer.writerows(rows)


# In[41]:

#Define a function which replaces a column from the original in the output file
def replaceCol(fileName, col, data):

    rows, header1, header2, header3 = getRows(fileName)
    
    for i in range(0, len(data)):
        rows[i][col] = data[i]

    write(fileName, rows, header1, header2, header3)


# In[42]:

#Define a function which appends a new column to the end of the csv
def addCol(fileName, newHeader, data):
    
    rows, header1, header2, header3 = getRows(fileName)

    header3.append(newHeader)

    for i in range(0, len(data)):
        rows[i].append(data[i])

    write(fileName, rows, header1, header2, header3)


# In[43]:

#Part 1 - define function to reset rotary postion to zero for each new step
def revsReset():
    #Get user inputs
    fileName = selectFile()
    stepsCol=int(input("Enter column for step: "))-1
    revsCol=int(input("Enter column for rotary position: "))-1
    
    #Get data from csv
    steps, revs = np.genfromtxt(fileName, delimiter =',', usecols = (stepsCol,revsCol) , skip_footer=2, unpack = True)
    steps = [x for x in steps if (math.isnan(x) == False)]
    revs = [x for x in revs if (math.isnan(x) == False)]
    
    #Process rotary postion given steps
    step = -1
    temp = -1
    for i in range(len(revs)):
        if steps[i] != step:
            temp = revs[i]
            revs[i] = 0
            step = steps[i]
        else:
            revs[i] = revs[i] - temp
    
    #Write data to file
    replaceCol(fileName, revsCol, revs)


# In[44]:

#Part 2 - define funtion to average data from different files

#This function is used in the average() function to isolate only the relevant data
def isolate(step, steps, arr1, arr2, arr3, rate):
    temp1 = []
    temp2 = []
    temp3 = []
    while steps[0] != step:
        steps = np.delete(steps, 0)
        arr1= np.delete(arr1, 0)
        arr2= np.delete(arr2, 0)
        arr3= np.delete(arr3, 0)
    i = 0
    while steps[i] == step:
        if i % rate == 0:
            temp1.append(arr1[i])
            temp2.append(arr2[i])
            temp3.append(arr3[i])
        i=i+1
    return temp1, temp2, temp3

#Function used within average() function to ensure arrays are all the same size
def trimArrays(array):
    amin = len(array[0])
    for i in range(0, len(array)):
        if amin > len(array[i]):
            amin = len(array[i])
    
    for i in range(0, len(array)):
        array[i] = array[i][:amin]
        
#This is the function which does the averaging
def average():
    #Define lists to use later
    fileNames = []
    dataRates = []
    dataSteps = []
    COFcols = []
    revscols = []
    times =[]
    COFs = []
    revs = []
    cols = []
    
    #Get user to select files and input needed information
    print("Select first file")
    done=False

    while done==False:
        fileNames.append(selectFile())
        dataRates.append(float(input("Number of data points per second? ")))
        COFcols.append(int(input("Column corresponding to COF? "))-1)
        revscols.append(int(input("Column corresponding to rotary position? "))-1)
        dataSteps.append(int(input('Recipe step to be averaged? ')))
        i = input("Enter another file? (Y/N) ")
        if i == 'Y' or i == 'y':
            done=False
        else:
            done=True
    
    #Gets information and adds it all to relevant lists which can later be averaged
    max = np.amax(dataRates)
    for i in range(len(fileNames)):
        steps, time, COF, rev = np.genfromtxt(fileNames[i], 
                                                 delimiter =',', skip_footer = 2, usecols = (0,1,COFcols[i],revscols[i]) , unpack = True)
        steps = [x for x in steps if (math.isnan(x) == False)]
        time = [x for x in time if (math.isnan(x) == False)]
        COF = [x for x in COF if (math.isnan(x) == False)]
        rev = [x for x in rev if (math.isnan(x) == False)]    
        
        
        rate = max/dataRates[i]
        a,b,c = isolate(dataSteps[i], steps, time, COF, rev, rate)
        times.append(a)
        COFs.append(b)
        revs.append(c)
    
    cols.append(np.mean(times, axis=0))
    cols.append(np.mean(COFs, axis=0))
    cols.append(np.mean(revs, axis=0))
    
    
    
    newFile = input("Enter name for output file: ") + '.csv'
    print("Select output directory")
    root = Tk()
    ttl  = "Select output directory"
    fileDir = askdirectory(title = ttl)
    root.destroy()
    
    newFile = fileDir + '\\' + newFile
    
    with open(newFile, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "DAQ.COF", "Rotary.Position"])
        writer.writerows(np.array(cols).T.tolist())
       


# In[50]:

#Part 3 - Smoothe the data using SMA and a low-pass filter

#This function is used to do the actual filtering
def filter(data, order, freq, width):
    N  = order    # Filter order
    Wn = freq # Cutoff frequency
    B, A = signal.butter(N, Wn, output='ba')
    temp = signal.filtfilt(B,A, data)
    df = pandas.DataFrame({'data':temp})
    
    return df.rolling(window=width)['data'].mean().tolist()

#This function handles inputs and outputs
def smoothe():
    #Get file and other user inputs
    fileName = selectFile()
    col1 = int(input('Enter column for "x-axis": '))-1
    col2 = int(input('Enter column for "y-axis": '))-1
    freq = float(input('Enter low-pass filter cutoff frequency (Hz): '))
    width = int(input('Enter width for SMA smoothing: '))
    
    #Get data from csv
    steps, revs, data = np.genfromtxt(fileName, delimiter =',', usecols = (0, col1, col2) , skip_footer=2, unpack = True)
    steps = [x for x in steps if (math.isnan(x) == False)]
    revs = [x for x in revs if (math.isnan(x) == False)]
    data = [x for x in data if (math.isnan(x) == False)]
    
    #Add filter both to entire data set and to each step
    filtData=filter(data, 2, freq, width)

    step = steps[0]
    temp = []
    dataSteps = []

    for i in range(0, len(steps)):
        if steps[i] > step:
            dataSteps.append(temp)
            temp = []
            step = steps[i]
    
        temp.append(data[i])
        if i == len(steps)-1:
            dataSteps.append(temp)
    
    for i in range(0, len(dataSteps)):
        dataSteps[i] = filter(dataSteps[i], 2, freq, width)
    
    temp2 = []
    for row in dataSteps:
        for col in row:
            temp2.append(col)
    dataSteps=temp2
    
    #Save graph of data
    i = input('Save plot of data (Y/N)')
    if i =='Y' or i == 'y':
        plt.rcParams["figure.figsize"] = [50, 25]
        plt.plot(revs, data, label = 'Raw')
        plt.plot(revs, filtData, label = 'With SMA and Frequency Filter')
        plt.plot(revs, dataSteps, label = "With SMA and Frequency Filter, stepwise")
        plt.legend()
        plt.savefig(fileName.replace('.csv', '.png'))
        plt.clf()
    
    #Write data to file
    replaceCol(fileName, col2, filtData)
    addCol(outify(fileName), 'DAQ.COF (Smoothed per Step)', dataSteps)


# In[46]:

#Part 4 - define function to add information to header of csv
def addInfo():
    #Choose file and extract data
    fileName = selectFile()
    rows, header1, header2, header3 = getRows(fileName)
        
    #Get user inputs for attributes and their values
    while len(header1) > len(header2):
        header2.append('')
    
    while len(header2) > len(header1):
        header1.append('')
        
    done = False

    while done == False:
        header1.append(input("Enter attribute: "))
        header2.append(input("Enter value for this attribute: "))
        i = input("Enter another attribute? (Y/N) ")
        if i == 'Y' or i == 'y':
            done=False
        else:
            done=True
    
    #Write info to file
    write(fileName, rows, header1, header2, header3)


# In[47]:

#Part 5 - define function to find derivatives of the data
def derivative():
    #User inputs for x and y columns
    fileName = selectFile()
    xCol = int(input('Select "x" column for derivative: '))-1
    yCol = int(input('Select "y" column for derivative: '))-1
    
    #Get data from csv
    x, y= np.genfromtxt(fileName, delimiter =',', usecols = (xCol, yCol) ,skip_footer=2, unpack = True)
    x = [i for i in x if (math.isnan(i) == False)]
    y = y.tolist()
    for i in range(0, len(y)):
        if math.isnan(y[i]):
            y[i]=0
    for i in range(0, len(y)-len(x)):
        del y[0]
    
    #Calculate derivatives
    derivative = np.diff(y)/np.diff(x)
    derivative = np.append(derivative, 0)
    
    #Write data to file
    addCol(fileName, 'DAQ.COF Derivative', derivative)


# In[48]:

def main():
    #Introductory text to present the app and its options to user
    print('Welcome to Saint-Gobain Performance Plastics Tribometer Data Processing Utility')
    print('Version 1.1')
    print('Select one of the following tasks to perform:')
    print('1- Reset rotary position to zero for each step of the recipe')
    print('2- Average timestamp, DAQ.COF, and rotary position for a particular recipe step')
    print('3- Perform smoothing/filtering to data')
    print('4- Add information to CSV file')
    print('5- Find derivative for data (using "slope" approximations)')

    #Create loop which cycles until valid option chosen
    #Each input calls a function corresponding to a task
    error=True
    while error==True:
        i = input("Select function: ")
        if i == "1":
            revsReset()
            error=False
        elif i == "2":
            average()
            error=False
        elif i == "3":
            smoothe()
            error = False
        elif i == "4":
            addInfo()
            error = False
        elif i == "5":
            derivative()
            error = False
        else:
            print('Invaild input, please enter again')

