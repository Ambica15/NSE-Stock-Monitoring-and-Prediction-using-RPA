from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
from imutils import paths
from tkinter.filedialog import askopenfilename
import pickle
import pandas as pd
import datetime
import pandas_datareader.data as web
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib as mpl
from matplotlib import cm as cm
import math
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
import seaborn as sns
from sklearn.svm import SVR  #SVR regression
from sklearn.metrics import mean_squared_error
import os
from sklearn.ensemble import GradientBoostingRegressor
import webbrowser
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM  #class for LSTM regression
from keras.layers import Dropout

import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)
from pandas_datareader import data as pdr

main = tkinter.Tk()
main.title("NSE Stock Monitoring & Prediction using Robotic Process Automation")
main.geometry("1300x1200")

global dataFrame, dfreg
global moving_avg
global dfcomp
global clfknn
global clfknndist
global X, y, X_train, y_train, X_test, y_test,X_pred
global distknn, uniknn, knnunipred, knndistpred

def loadDataset():
    text.delete('1.0', END)
    global dataFrame
    global dfcomp
    start = datetime.datetime(2010, 1, 1)
    end = datetime.datetime(2017, 1, 11)

    dataFrame = pd.read_csv("Yahoo-Finance-Dataset/Apple_YahooDataSet.csv")

    text.insert(END, "Shape of Apple Stock Dataset: "+str(dataFrame.shape)+"\n\n")
    text.insert(END, "Sample of Apple Stock Data: \n"+str(dataFrame.head(2))+"\n\n")

    dfcomp = dataFrame#web.DataReader(['AAPL', 'GE', 'GOOG', 'IBM', 'MSFT'], 'yahoo', start=start, end=end)['Adj Close']
    dfcomp.drop(['Date'], axis = 1,inplace=True)
    text.insert(END, "Shape of Apple Competitor Stock Dataset: " + str(dfcomp.shape) + "\n\n")
    text.insert(END, "Sample of Apple Competitor Stock Data: \n" + str(dfcomp.head(2)) + "\n\n")

    text.insert(END, "Dataset Downloaded from Yahoo Finance Dataset\n\n")

def dfcorr():
    text.delete('1.0', END)
    global dfcomp

    text.insert(END, "Correlation form Apple Competitor Stock\n\n")
    retscomp = dfcomp.pct_change()
    corr = retscomp.corr()
    text.insert(END, "correlation: \n"+str(corr)+"\n\n")


def dataPreProcess():
    text.delete('1.0', END)
    global dataFrame,dfreg
    global X, y, X_train, X_test, y_train, y_test,X_pred

    text.insert(END,"Data PreProcessing for Apple Stock Dataset\n\n")
    dfreg = dataFrame.loc[:,["Adj Close","Volume"]]
    dfreg["HL_PCT"] = (dataFrame["High"] - dataFrame["Low"]) / dataFrame["Close"] * 100.0
    dfreg["PCT_change"] = (dataFrame["Close"] - dataFrame["Open"]) / dataFrame["Open"] * 100.0

    # Drop missing value
    dfreg.fillna(value=-99999, inplace=True)
    # We want to separate 1 percent of the data to forecast
    forecast_out = int(math.ceil(0.01 * len(dfreg)))

    # Separating the label here, we want to predict the AdjClose
    forecast_col = 'Adj Close'
    dfreg['label'] = dfreg[forecast_col].shift(-forecast_out)
    X = np.array(dfreg.drop(['label'], 1))

    # Scale the X so that everyone can have the same distribution for linear regression
    X = preprocessing.scale(X)
    # Finally We want to find Data Series of late X and early X (train) for model generation and evaluation
    X_pred = X[-forecast_out:]
    X = X[:-forecast_out]
    # Separate label and identify it as y
    y = np.array(dfreg['label'])
    y = y[:-forecast_out]

    text.insert(END, "X lablels : \n"+str(X)+"\n\n")
    text.insert(END, "Y lablels : \n"+str(y)+"\n\n")
    text.insert(END, "Data spliting into Train and Test")
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.3)

    text.insert(END, "number of Train Samples : " + str(len(X_train)) + "\n")
    text.insert(END, "number of Test Sample: " + str(len(X_test)) + "\n")

    text.insert(END, "Data Preprocessing Completed\n\n")

def uniformKNN():
    text.delete('1.0',END)
    global clfknn
    global uniknn

    # KNN Regression
    clfknn = KNeighborsRegressor(n_neighbors=5)
    clfknn.fit(X_train, y_train)

    uniknn = clfknn.score(X_train, y_train)

    text.insert(END, "Accuracy of KNN with Uniform weights : "+str(uniknn*100)+"\n\n")

def distKNN():
    text.delete('1.0', END)
    global clfknndist,knndistpred
    global distknn,knnunipred
    # KNN Regression
    clfknndist = KNeighborsRegressor(n_neighbors=5,weights='distance')
    clfknndist.fit(X_train, y_train)
    distknn = clfknndist.score(X_train, y_train)

    text.insert(END, "Accuracy of KNN with Uniform weights : "+str(distknn*100)+"\n\n")
def predModel():
    text.delete('1.0', END)
    global clfknndist,clfknn,knnunipred,knndistpred
    global X, y, X_train, X_test, y_train, y_test

    
    filename = filedialog.askopenfilename(initialdir="Yahoo-Finance-Dataset")
    test = pd.read_csv(filename)
    text.insert(END, filename + " test file loaded\n"+str(test.columns)+"\n");
    x_pred = np.array(test.drop(['Unnamed: 0'],1))

    text.insert(END, "test Dataset: \n"+str(x_pred)+"\n\n");

    knndistpred = clfknndist.predict(x_pred)

    text.insert(END, "Predict values for KNN with Dist weights: \n" + str(knndistpred) + "\n\n");

    knnunipred = clfknn.predict(x_pred)

    text.insert(END, "Predict values for KNN with Uni Wights: \n" + str(knnunipred) + "\n\n");

def graph():
    text.delete('1.0', END)

    global uniknn,distknn
    global knnunipred,knndistpred
    global dfreg

    dfreg['Forecast'] = np.nan
    last_date = dfreg.iloc[-1].name
    last_unix = last_date
    next_unix = last_unix + datetime.timedelta(days=1)

    for i in knnunipred:
        next_date = next_unix
        next_unix += datetime.timedelta(days=1)
        dfreg.loc[next_date] = [np.nan for _ in range(len(dfreg.columns) - 1)] + [i]
    dfreg['Adj Close'].tail(500).plot()
    dfreg['Forecast'].tail(500).plot()
    plt.legend(loc=4)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.savefig('knnUniformPredGraph.png')
    plt.close()

    for i in knndistpred:
        next_date = next_unix
        next_unix += datetime.timedelta(days=1)
        dfreg.loc[next_date] = [np.nan for _ in range(len(dfreg.columns) - 1)] + [i]
    dfreg['Adj Close'].tail(500).plot()
    dfreg['Forecast'].tail(500).plot()
    plt.legend(loc=4)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.savefig('knnDistPredGraph.png')
    plt.close()

    height = [uniknn,distknn]
    bars = ('KNN with uniform weights Accuracy', 'KNN with distance weights Accuracy')
    y_pos = np.arange(len(bars))
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.show()


def createTable(original, predict, algorithm):
    output = '<table border=1 align=left>'
    output+= '<tr><th>Original Price</th><th>'+algorithm+' Predicted Price</th></tr>'
    for i in range(len(original)):
        output += '<tr><td>'+str(original[i])+'</td><td>'+str(predict[i])+'</td></tr>'
    output+='</table></body></html>'
    f = open("output.html", "w")
    f.write(output)
    f.close()
    webbrowser.open("output.html",new=1)   

def runSVM():
    text.delete('1.0', END)
    global X, y, X_train, X_test, y_train, y_test,X_pred

    svr_regression = SVR(C=1.0, epsilon=0.2)
    #training SVR with X and Y data
    svr_regression.fit(X_train, y_train)
    #performing prediction on test data
    predict = svr_regression.predict(X_test)
    labels = y_test
    labels = labels[0:100]
    predict = predict[0:100]
    #calculating MSE error
    svr_mse = mean_squared_error(labels,predict)
    text.insert(END, "SVM Mean Square Error : "+str(svr_mse)+"\n\n")
    text.update_idletasks()
    createTable(labels,predict,"SVM")
    #plotting comparison graph between original values and predicted values
    plt.plot(labels, color = 'red', label = 'Original Stock Price')
    plt.plot(predict, color = 'green', label = 'SVM Predicted Price')
    plt.title('SVM Stock Prediction')
    plt.xlabel('Test Data')
    plt.ylabel('Stock Prediction')
    plt.legend()
    plt.show()

def runGBR():
    global X, y, X_train, X_test, y_train, y_test,X_pred

    gbr_regression = GradientBoostingRegressor()
    #training Gradient Boosting Regressor with X and Y data
    gbr_regression.fit(X, y)
    #performing prediction on test data
    predict = gbr_regression.predict(X_test)
    labels = y_test
    labels = labels[0:100]
    predict = predict[0:100]
    #calculating MSE error
    svr_mse = mean_squared_error(labels,predict)
    text.insert(END, "Gradient Boosting Regressor Mean Square Error : "+str(svr_mse)+"\n\n")
    text.update_idletasks()
    createTable(labels,predict,"Decision Tree")
    #plotting comparison graph between original values and predicted values
    plt.plot(labels, color = 'red', label = 'Original Stock Price')
    plt.plot(predict, color = 'green', label = 'Gradient Boosting Regressor Predicted Price')
    plt.title('Gradient Boosting Regressor Stock Prediction')
    plt.xlabel('Test Data')
    plt.ylabel('Stock Prediction')
    plt.legend()
    plt.show()
    
def runLSTM():
    global X, y, X_train, X_test, y_train, y_test,X_pred
    if os.path.exists("model/lstm.txt"):
        with open('model/lstm.txt', 'rb') as file:
            lstm = pickle.load(file)
        file.close()
    else:
        XX = np.reshape(X, (X.shape[0], X.shape[1], 1))
        print(XX.shape)
        lstm = Sequential()
        lstm.add(LSTM(units = 50, return_sequences = True, input_shape = (XX.shape[1], XX.shape[2])))
        lstm.add(Dropout(0.2))
        lstm.add(LSTM(units = 50, return_sequences = True))
        lstm.add(Dropout(0.2))
        lstm.add(LSTM(units = 50, return_sequences = True))
        lstm.add(Dropout(0.2))
        lstm.add(LSTM(units = 50))
        lstm.add(Dropout(0.2))
        lstm.add(Dense(units = 1))
        lstm.compile(optimizer = 'adam', loss = 'mean_squared_error')
        lstm.fit(XX, y, epochs = 1000, batch_size = 16)        
    predict = lstm.predict(X_test)    
    labels = y_test
    labels = labels[0:100]
    predict = predict[0:100]
    #calculating MSE error
    svr_mse = mean_squared_error(labels,predict)
    text.insert(END, "LSTM Mean Square Error : "+str(svr_mse)+"\n\n")
    text.update_idletasks()
    createTable(labels,predict,"Decision Tree")
    #plotting comparison graph between original values and predicted values
    plt.plot(labels, color = 'red', label = 'Original Stock Price')
    plt.plot(predict, color = 'green', label = 'LSTM Predicted Price')
    plt.title('LSTM Tree Stock Prediction')
    plt.xlabel('Test Data')
    plt.ylabel('Stock Prediction')
    plt.legend()
    plt.show()

font = ('times', 16, 'bold')
title = Label(main, text='NSE Stock Monitoring & Prediction using Robotic Process Automation')
title.config(bg='DarkGoldenrod1', fg='black')
title.config(font=font)
title.config(height=3, width=120)
title.place(x=0,y=5)

font1 = ('times', 13, 'bold')
uploadButton = Button(main, text="Download Dataset", command=loadDataset)
uploadButton.place(x=700,y=100)
uploadButton.config(font=font1)

corrButton = Button(main, text="Correlation for Data", command=dfcorr)
corrButton.place(x=700,y=150)
corrButton.config(font=font1)

ppButton = Button(main, text="Data Preprocessing", command=dataPreProcess)
ppButton.place(x=700,y=200)
ppButton.config(font=font1)

uniformButton = Button(main, text="Run KNN with Uniform Weights", command=uniformKNN)
uniformButton.place(x=700,y=250)
uniformButton.config(font=font1)

distButton = Button(main, text="Run KNN with Dist Weights", command=distKNN)
distButton.place(x=700,y=300)
distButton.config(font=font1)

svmButton = Button(main, text="Run SVM Algorithm", command=runSVM)
svmButton.place(x=700,y=350)
svmButton.config(font=font1)

dtButton = Button(main, text="Run Gradient Boosting Regressor Algorithm", command=runGBR)
dtButton.place(x=700,y=400)
dtButton.config(font=font1)

lstmButton = Button(main, text="Run LSTM Algorithm", command=runLSTM)
lstmButton.place(x=700,y=450)
lstmButton.config(font=font1)

predButton = Button(main, text="Predict the Test Data ", command=predModel)
predButton.place(x=700,y=500)
predButton.config(font=font1)

graphButton = Button(main, text="KNN Accuracy", command=graph)
graphButton.place(x=700,y=550)
graphButton.config(font=font1)

font1 = ('times', 12, 'bold')
text=Text(main,height=30,width=80)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=100)
text.config(font=font1)


main.config(bg='LightSteelBlue1')
main.mainloop()

