import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import pandas as pd
import numpy as np
from scipy.optimize import minimize

import numpy as np
from bs4 import BeautifulSoup

import functions

#Import historical data from Primera Division
s2021 = pd.read_csv('SP1.csv')
s2020 = pd.read_csv('SP2.csv')
s2019 = pd.read_csv('SP3.csv')
s2018 = pd.read_csv('SP5.csv')

#Import historical data from Segunda Division
Segunda2021 = pd.read_csv('Segunda2021.csv')
Segunda2020 = pd.read_csv('Segunda2020.csv')
Segunda2019 = pd.read_csv('Segunda2019.csv')

#Choose desired columns
selected_columns = ['HomeTeam', 'AwayTeam', 'FTR', 'B365H', 'B365D', 'B365A', 'WHH', 'WHD', 'WHA']
seasons1 = [s2021[selected_columns], s2020[selected_columns]]
seasons2 = [Segunda2021[selected_columns], Segunda2020[selected_columns], Segunda2019[selected_columns]]

f1 = open("FutureMatches.txt", "r")
f2 = open('FutureMatchesSegunda.txt', 'r')
soup = BeautifulSoup(f1)
soup2 = BeautifulSoup(f2)
f1.close()
f2.close()

#Upcoming Matches in Primera and Segunda Division
#Returns dataframes with 'HomeTeam', 'AwayTeam', 'HOdds', 'DOdds', 'AOdds',  'PH', 'PD', 'PA'
new_primera = GenerateNewSeason(soup)
new_segunda = GenerateNewSeason(soup2)

#Historical dataframes of Primera and Segunda division
df_primera = GenerateDataBase(seasons1)
df_segunda = GenerateDataBase(seasons2)

#Correct wrong names
dictio1 = {'Alavés':'Alaves', 'Real Sociedad':'Sociedad', 'Atlético de Madrid':'Ath Madrid', 'Real Betis': 'Betis', 'Cádiz':'Cadiz', 'Athletic de Bilbao':'Ath Bilbao'}
dictio2 = {'FC Cartagena': 'Cartagena', 'UD Logronés':'Logrones', 'Málaga C.F.':'Malaga', 'CD Castellón':'Castellon', 'Rayo Vallecano':'Vallecano', 'Racing Santander': 'Santander'}
new_primera['HomeTeam'].replace(dictio1, inplace = True)
new_primera['AwayTeam'].replace(dictio1, inplace = True)
new_segunda['HomeTeam'].replace(dictio2, inplace = True)
new_segunda['AwayTeam'].replace(dictio2, inplace = True)
new_primera=DropNotInTeams(new_primera, df_primera)
new_segunda=DropNotInTeams(new_segunda, df_segunda)

#Encode team names for each season
le1 = preprocessing.LabelEncoder()
le2 = preprocessing.LabelEncoder()
df_primera[['HomeTeam']] = df_primera[['HomeTeam']].apply(le1.fit_transform)
df_primera[['AwayTeam']] = df_primera[['AwayTeam']].apply(le1.transform)
df_segunda[['HomeTeam']] = df_segunda[['HomeTeam']].apply(le2.fit_transform)
df_segunda[['AwayTeam']] = df_segunda[['AwayTeam']].apply(le2.transform)

new_primera[['HomeTeam', 'AwayTeam']]=new_primera[['HomeTeam', 'AwayTeam']].apply(le1.transform)
new_segunda[['HomeTeam', 'AwayTeam']]=new_segunda[['HomeTeam', 'AwayTeam']].apply(le2.transform)

cleanna(df_primera), cleanna(df_segunda), cleanna(new_primera), cleanna(new_segunda)

#Train each classifier
clf_primera = RandomForestClassifier(n_estimators=50, criterion = 'entropy', max_depth=3, random_state=0)
clf_segunda = RandomForestClassifier(n_estimators=50, criterion = 'entropy', max_depth=3, random_state=0)
clf_primera.fit(df_primera.drop('FTR', axis = 1), df_primera['FTR'])
clf_segunda.fit(df_segunda.drop('FTR', axis = 1), df_segunda['FTR'])
