import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pyodbc
from sqlalchemy import create_engine


conn2 = pyodbc.connect('Driver={SQL Server};'
                'Server=xxxxxx.cahwy5xxx.useast-1.rds.amazonaws.com,xxxx;'
                                'Database=gamdo;'
                                'uid=xxxxx;pwd=xxxxxxx')
print ("Connected")
cursor = conn2.cursor()


df = '''
          SELECT *
         FROM RFM_data
        '''

X = df.copy()
X.drop('USER_ID', axis = 1, inplace = True)


scaler = StandardScaler()
scaler.fit(X)
data_normalized = scaler.transform(X)


#Estimating the best number of cluster using Elbow method
data_normalized =pd.DataFrame(data = data_normalized, index = X.index, columns= X.columns)

sse = {}
k_range = range(1, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42) # n_init to suppress warning
    kmeans.fit(data_normalized)
    sse[k] = kmeans.inertia_

#sns.pointplot(x = list(sse.keys()), y = list(sse.values()))

kmeans = KMeans(n_clusters = 4, random_state = 1)
kmeans.fit(np.array(data_normalized))

cluster_labels = kmeans.labels_
df_k4 = df.assign(Cluster= cluster_labels)
df_k4.set_index('USER_ID', inplace = True)


customer_cluster_df = df_k4.reset_index()

#save customer cluster table to database
engine = create_engine("mssql+pyodbc://", creator=lambda: conn2, fast_executemany=True)

customer_cluster_df.to_sql('customer_cluster', con=engine, if_exists='append', index=False)

















