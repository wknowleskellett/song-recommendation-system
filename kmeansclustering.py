from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot  as plt
%matplotlib inline


dataframe=pd.read_csv('data.csv')
# dataframe.head()


# kmeans=KMeans(n_clusters=20, init='k-means++',max_iter=100, n_init=1, verbose=0, random_state=3425)
kmeans=KMeans(n_clusters=20)
# scaler = MinMaxScaler()
scaler=StandardScaler()

# newdf = dataframe.select_dtypes(np.number)
# scaled=scaler.fit_transform(newdf)

"""
Normalizing column values so they are between 0 and 1 using Standard Scaler
"""

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


# dataframe.head()


"""
Performs K-Means clustering on given N features
"""
clustering=kmeans.fit_predict(dataframe[['acousticness','valence','danceability','energy','instrumentalness','liveness','loudness','speechiness','tempo','key','duration_ms','explicit','mode','popularity','year']])
#clustering 

dataframe["cluster"]=clustering
# dataframe.head(50)


"""
Performs PCA on the clustering inorder to visualise clustering in two dimensions
"""
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
# scaler.fit_transform(datafa)
song=pca.fit_transform(dataframe[['acousticness','valence','danceability','energy','instrumentalness','liveness','loudness','speechiness','tempo','key','duration_ms','explicit','mode','popularity','year']])

graph = pd.DataFrame(columns=['x', 'y'], data=song)
graph['title'] = dataframe['name']
graph['cluster'] = dataframe['cluster']


"""
Displays the clustering after the PCA decomposition has been done on the K-means clustering on N features.
"""
import plotly.express as px
plot = px.scatter(graph, x='x', y='y', color='cluster', hover_data=['x', 'y', 'title'])
plot.show()
