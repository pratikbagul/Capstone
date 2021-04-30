
# coding: utf-8

# ## Import and Install    

# In[ ]:

get_ipython().system('pip install bs4')
    #!pip install requests

    from bs4 import BeautifulSoup # this module helps in web scrapping.
    import requests  # this module helps us to download a web page

    import pandas as pd
    import requests
    import numpy as np


# In[2]:

import matplotlib.cm as cm
import matplotlib.colors as colors


# In[3]:

get_ipython().system('pip install folium')
import folium 


# In[4]:

from sklearn.cluster import KMeans


# In[5]:

get_ipython().system('pip install geocoder')


# In[6]:

get_ipython().system('pip install geopy')


# In[7]:

import geocoder


# In[8]:

html_data = requests.get('https://en.wikipedia.org/w/index.php?title=List_of_postal_codes_of_Canada:_M&oldid=906439794').text 


# In[9]:

bs=BeautifulSoup(html_data, 'html5lib')


# In[10]:

tables = bs.find_all('table')


# In[11]:

for index,table in enumerate(tables):
    if ("M1A" in str(table)):
        table_index = index
print(table_index)


# In[12]:

toronto_data = pd.DataFrame(columns=["Postal_Code", "Borough", "Neighbourhood"])


# In[13]:

for row in tables[table_index].tbody.find_all("tr"):
    col = row.find_all("td")
    for i in range(3):
        if (col != []):
            Postal_Code = col[0].text
            Borough =col[1].text
            Neighbourhood =col[2].text
            toronto_data = toronto_data.append({"Postal_Code":Postal_Code, "Borough":Borough, "Neighbourhood":Neighbourhood}, ignore_index=True)


# ## Clean dataframe

# In[14]:

toronto_data.replace('\n','', regex=True, inplace = True)


# In[15]:

df2=toronto_data[(toronto_data.Borough !="Not assigned")]
df2['Neighbourhood'] = np.where(df2['Neighbourhood'] == 'Not assigned',df2['Borough'], df2['Neighbourhood'])
df3=df2.groupby(['Postal_Code','Borough'], sort=False).agg(', '.join)


# In[16]:

df3.reset_index(inplace=True)


# In[17]:

df3.head(10)


# In[18]:

df4=df3


# ## Get Longitude and Latitude from geocoders
# 

# In[19]:

lat_lng_coords = ["Postal_code","Latitude","Longitude"]


# In[20]:

from geopy.geocoders import Nominatim


# In[21]:

def eval_results(x):
    try:
        return [x.latitude, x.longitude]
    except:
        return [None, None]


# In[22]:

geolocator = Nominatim(user_agent="ny_explorer")
for i in range(103):
  location = geolocator.geocode('{}, Toronto, Ontario'.format(df3.Postal_Code[i]))
  location1 = eval_results(location)
  latitude = location1[0]
  longitude = location1[1]
  lat_lng_coords.append([df3.Postal_Code[i],latitude,longitude])
 # print('The geograpical coordinate of Manhattan are {}, {}.'.format(latitude, longitude))
 


# In[23]:

lat_lng = pd.DataFrame(lat_lng_coords[3:106])
lat_lng


# In[24]:

lat_lng.columns = ['Postal_Code','Longitude','Latitude']


# In[25]:

lat_lng


# In[26]:

df4 = pd.merge(df3,lat_lng,on='Postal_Code')
df4.head()


# In[27]:

df4.shape


# ## Get Longitude and Latitude from excel

# In[28]:

lat_lon = pd.read_csv('https://cocl.us/Geospatial_data')
lat_lon.head()


# In[31]:

lat_lon.rename(columns={'Postal Code':'Postal_Code'},inplace=True)


# In[32]:

df6 = pd.merge(df3,lat_lon,on='Postal_Code')
df6.head()


# ## Toronto as Borough

# In[33]:

df7 = df6[df6['Borough'].str.contains('Toronto',regex=False)]


# In[34]:

df7


# ## Map

# In[35]:

map_toronto = folium.Map(location=[43.651070,-79.347015],zoom_start=10)

for lat,lng,borough,neighbourhood in zip(df7['Latitude'],df7['Longitude'],df7['Borough'],df7['Neighbourhood']):
    label = '{}, {}'.format(neighbourhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
    [lat,lng],
    radius=5,
    popup=label,
    color='blue',
    fill=True,
    fill_color='#3186cc',
    fill_opacity=0.7,
    parse_html=False).add_to(map_toronto)
map_toronto


# ## Cluster

# In[36]:

k=5
toronto_clustering = df7.drop(['Postal_Code','Borough','Neighbourhood'],1)
kmeans = KMeans(n_clusters = k,random_state=0).fit(toronto_clustering)
kmeans.labels_
df7.insert(0, 'Cluster Labels', kmeans.labels_)


# In[37]:

df7


# ## Cluster on Map

# In[39]:

# create map
map_clusters = folium.Map(location=[43.651070,-79.347015],zoom_start=10)

# set color scheme for the clusters
x = np.arange(k)
ys = [i + x + (i*x)**2 for i in range(k)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, neighbourhood, cluster in zip(df7['Latitude'], df7['Longitude'], df7['Neighbourhood'], df7['Cluster Labels']):
    label = folium.Popup(' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# In[ ]:



