from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot  as plt
# % matplotlib inline

dataframe=pd.read_csv('data.csv')


#defining  KMeans
kmeans=KMeans(n_clusters=100, init='k-means++', max_iter=100, n_init=1, verbose=0, random_state=3425)

"""
Normalizing numerical columns of the graph using Standard Scalar to perform k-means clustering
"""

scaler=StandardScaler()
scaler.fit(dataframe[['loudness']])
dataframe['loudness'] = scaler.transform(dataframe[['loudness']])
scaler.fit(dataframe[['tempo']])
dataframe['tempo'] = scaler.transform(dataframe[['tempo']])
scaler.fit(dataframe[['key']])
dataframe['key'] = scaler.transform(dataframe[['key']])
scaler.fit(dataframe[['year']])
dataframe['year'] = scaler.transform(dataframe[['year']])
scaler.fit(dataframe[['duration_ms']])
dataframe['duration_ms'] = scaler.transform(dataframe[['duration_ms']])
scaler.fit(dataframe[['explicit']])
dataframe['explicit'] = scaler.transform(dataframe[['explicit']])
scaler.fit(dataframe[['mode']])
dataframe['mode'] = scaler.transform(dataframe[['mode']])
scaler.fit(dataframe[['popularity']])
dataframe['popularity'] = scaler.transform(dataframe[['popularity']])


"""
Perform K-Means clustering on N features
"""
clustering=kmeans.fit_predict(dataframe[['acousticness','valence','danceability','energy','instrumentalness','liveness','loudness','speechiness','tempo','key','duration_ms','mode']])


#adding the predicted clusterings to the dataframe graph as a column
dataframe["cluster"]=clustering

#make a dataframe with the features as columns of the top5 songs of the user
top5user=pd.DataFrame(data=results2)


"""
Normalize the numerical columns for the top5 songs usin Standard Scaler
"""
scaler.fit(top5user[['loudness']])
top5user['loudness'] = scaler.transform(top5user[['loudness']])
scaler.fit(top5user[['tempo']])
top5user['tempo'] = scaler.transform(top5user[['tempo']])
scaler.fit(top5user[['key']])
top5user['key'] = scaler.transform(top5user[['key']])
scaler.fit(top5user[['duration_ms']])
top5user['duration_ms'] = scaler.transform(top5user[['duration_ms']])
scaler.fit(top5user[['mode']])
top5user['mode'] = scaler.transform(top5user[['mode']])


#predict which clusters the top5 songs belong to using the k-means cluster that we built
clustering5songs=kmeans.predict(top5user[['acousticness','valence','danceability','energy','instrumentalness','liveness','loudness','speechiness','tempo','key','duration_ms','mode']])

"""
Making the recommendations
"""

finalreccoid=[] 
finalrecconame=[]

for x in clustering5songs:
    filtereddf=dataframe.loc[dataframe['cluster']==x]
    filtereddf=filtereddf.sample(n=5)
    recommendedsongidlist=filtereddf['id'].tolist()
    recommendedsongnamelist=filtereddf['name'].tolist()
    finalreccoid.extend(recommendedsongidlist)
    finalrecconame.extend(recommendedsongnamelist)
    
    
# print(finalreccoid)
# print(finalrecconame)


#finalreccoid is the list of ids 
#finalrecconame is the list of names
