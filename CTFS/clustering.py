#!/usr/bin/env python

import webbrowser
import folium
import pandas as pd
import numpy as np
import osmnx as ox
import plotly.express as px
import geopy.distance as dist
from matplotlib import colors, cm
from sklearn.cluster import DBSCAN, OPTICS
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize


def clustering_routine(input_file, start_time, end_time, parameter, relationships):

	#------Traffic Series Construction------#
	df = pd.read_csv(input_file, dtype={'source_lng':str, 'source_lat':str, 'destination_lng':str, 'destination_lat':str})
	info = df.drop(['source_lng', 'source_lat', 'destination_lng', 'destination_lat'], axis=1)

	start_digit = start_time.split(":")[0] #get first two digits of starting time
	end_digit = end_time.split(":")[0] #get first two digits of ending time

	starting_pos = info.columns.values.searchsorted(start_digit, side='right') #search for starting time (column) in data file
	ending_pos = info.columns.values.searchsorted(end_digit, side='right') #search for ending time (column) in data file

	if ending_pos != len(info.columns) and starting_pos != ending_pos:
		spd_info = info.iloc[:, starting_pos:ending_pos+1] #select columns of data for clustering (starting time to ending time)
		data_length = len(spd_info.columns)
		print(f'Columns selected before interval parameter:\n{spd_info.head(10)}\n')

	remainder = data_length%parameter
	avg_speeds = []

	#construct data according to time interval parameter
	for row in spd_info.index:
		my_dict = {}
		col_indicator = 0

		for col in range(0, data_length, parameter):
			speeds = 0

			if col == data_length - remainder:
				for j in range(remainder):
					speeds += float(spd_info.iloc[[row], [col_indicator]].values)
					col_indicator += 1

				average = speeds/remainder
			else:
				for j in range(parameter):
					speeds += float(spd_info.iloc[[row], [col_indicator]].values)
					col_indicator += 1

				average = speeds/parameter

			key = spd_info.columns[col]
			value = average
			my_dict[key] = value
			
		avg_speeds.append(my_dict)

	final_ts = pd.DataFrame(avg_speeds)
	print(f'Columns selected after interval parameter:\n{final_ts.head(10)}\n')


	#------OPTICS (Step 1 - Shape Based Distance)------#
	X_train = np.array(final_ts.values) #create an array of the data that will be used for clustering
	X_normalized = normalize(X_train) #normalize the values of that data

	optics_model = OPTICS(min_samples=10, max_eps=0.2, metric='euclidean').fit(X_normalized) #perform OPTICS clustering
	print(f'Score at Step 1 is: {silhouette_score(X_normalized, optics_model.labels_)}')

	df['step1_clusters'] = optics_model.labels_ #store the cluster that each edge belongs to after step 1
	print(df['step1_clusters'].value_counts())
	print('\n')


	#------DBSCAN (Step 2 - Structure Based Distance)------#
	total_clusters1 = len(set(optics_model.labels_)) #get the number of clusters used at step 1
	kms_per_radian = 6371 #the radius of Earth in kilometers
	epsilon = 5/kms_per_radian #convert epsilon from km to radians
	min_samples = 3
	step2_dfs = {}

	for i in range(-1, total_clusters1-1):
		temp = df.loc[df['step1_clusters'] == i].copy() #select the edges that belong to each cluster of step 1
		coords = temp[['source_lat', 'source_lng']].values #set their starting points as coordinates
		X_train = np.array(coords) #use them as the data for clustering at step 2

		dbscan_cluster_model = DBSCAN(eps=epsilon, min_samples=min_samples, algorithm='ball_tree', metric='haversine').fit(X_train) #perform DBSCAN clustering using the haversine distance

		if len(set(dbscan_cluster_model.labels_))>1:
			print(f'Score at Step 2 (for cluster {i}) is: {silhouette_score(X_train, dbscan_cluster_model.labels_)}')
		else:
			print(f'No Score at Step 2 (for cluster {i})! Only One Cluster!')

		temp.loc[:, 'step2_clusters'] = dbscan_cluster_model.labels_ #store the cluster that each edge belongs to after step 2
		print(temp['step2_clusters'].value_counts())
		print('\n')
		step2_dfs[i] = temp

		#fig = px.scatter(x=X_train[:, 0], y=X_train[:, 1], color=temp['step2_clusters'])
		#fig.show()


	#------OPTICS (Step 3 - Value Based Distance)------#
	max_epsilon = 2
	min_samples = 2
	used_clusters = []
	step3_dfs = {}

	for i in range(-1, total_clusters1-1):
		clustered_df = pd.DataFrame(step2_dfs[i]) #for every cluster of step 1 dataframe the information retrieved from step 2
		total_clusters2 = step2_dfs[i]['step2_clusters'].nunique() #counts the number of unique entries in the 'step2_clusters' column
		temp_dfs = {}

		for j in range(-1, total_clusters2-1):
			local_data = final_ts.loc[clustered_df.index] #select the data to be clustered by index
			temp = local_data.loc[clustered_df['step2_clusters'] == j].copy() #select the edges that belong to each cluster of step 2
			X_train = np.array(temp.values)

			optics_model = OPTICS(min_samples=min_samples, max_eps=max_epsilon, metric='euclidean').fit(X_train) #perform OPTICS clustering

			if len(set(optics_model.labels_))>1:
				print(f'Score at Step 3 (for cluster {i}, {j}) is: {silhouette_score(X_train, optics_model.labels_)}')
			else:
				print(f'No Score at Step 3 (for cluster {i}, {j})! Only One Cluster!')

			temp.loc[:, 'step3_clusters'] = optics_model.labels_ #store the cluster that each edge belongs to after step 3
			print(temp['step3_clusters'].value_counts())
			print('\n')

			temp_dfs[j] = pd.merge(clustered_df, temp['step3_clusters'], left_index=True, right_index=True) #update the whole dataframe adding the clusters of step 3
			local_dframe = pd.DataFrame(temp_dfs[j])

			#for every cluster of step 2 update the number of cluster from step 3 clustering to 'final_clusters', so as to be unique and not a used one
			for row in local_dframe.index:
				step3_cluster = local_dframe.loc[row, 'step3_clusters']

				if step3_cluster != -1:
					local_dframe.loc[row, 'final_clusters'] = step3_cluster + max(used_clusters, default=0) + 1
				else:
					local_dframe.loc[row, 'final_clusters'] = -1

			local_dframe['final_clusters'] = local_dframe['final_clusters'].astype('int', errors='ignore')
			temp_dfs[j] = pd.merge(temp_dfs[j], local_dframe['final_clusters'], left_index=True, right_index=True) #update dataframe adding the 'final_clusters' column
			used_clusters.extend(local_dframe['final_clusters'].tolist()) #extend the list of used clusters, so that every time we have a different max
			print(f'Cluster\'s Dataframe:\n{local_dframe}')
			print(f'Number of different clusters used = {max(used_clusters, default=0)}\n')

		step3_dfs[i] = pd.concat(temp_dfs).reset_index() #for every cluster of step 1 concatenate all the information up to step 3

	final_df = pd.concat(step3_dfs).reset_index(drop=True) #gather everything
	print(f'Final Dataframe:\n{final_df}\n')


	#------Propagates and Splits/Merges------#
	if relationships != 'Both':
		propagates = []

		for cluster in range(-1, max(used_clusters)):
			cur_cluster = final_df.loc[final_df['final_clusters'] == cluster] #select the edges of each final cluster
			cur_cluster = cur_cluster.reset_index(drop=False)

			for i in cur_cluster.index:
				coords_source1 = (cur_cluster.iloc[i]['source_lng'], cur_cluster.iloc[i]['source_lat']) #get starting point's coordinates
				coords_dest1 = (cur_cluster.iloc[i]['destination_lng'], cur_cluster.iloc[i]['destination_lat']) #get ending point's coordinates
				lng_source1 = cur_cluster.iloc[i]['source_lng'] #get starting point's longitude
				lng_dest1 = cur_cluster.iloc[i]['destination_lng'] #get ending point's longitude

				#calculate distance between starting and ending point in km
				if dist.geodesic(coords_source1, coords_dest1).km >= 0.15:
					propagates.append(cur_cluster.iloc[i])

				#for every other edge of the same cluster
				for j in range(i, len(cur_cluster)-1):
					lng_source2 = cur_cluster.iloc[j+1]['source_lng'] #get starting point's longitude
					lng_dest2 = cur_cluster.iloc[j+1]['destination_lng'] #get ending point's longitude

					#if they are connected and in the same cluster, it's a propagate
					if ((lng_source1 == lng_dest2) or (lng_dest1 == lng_source2)):
						propagates.append(cur_cluster.iloc[i])
						propagates.append(cur_cluster.iloc[j+1])

		propagates_df = pd.DataFrame(propagates)
		propagates_df = propagates_df.drop_duplicates().reset_index(drop=True)
		print(f'Propagates Dataframe:\n{propagates_df}\n')

		splits_merges = []
		prop_index_list = propagates_df['index'].tolist() #make a list of the indexes of propagates

		#every edge that's not in propagates list is a split or a merge
		for indx in final_df.index:
			if indx not in prop_index_list:
				splits_merges.append(final_df.iloc[indx])

		splits_merges_df = pd.DataFrame(splits_merges)
		splits_merges_df = splits_merges_df.reset_index(drop=True)
		print(f'Splits/Merges Dataframe:\n{splits_merges_df}\n')


	#------Color for every Cluster------#
	cluster_colors = list(colors.CSS4_COLORS.keys()) #list of 148 different colors
	

	#------Display Clustered Edges------#
	if relationships == 'Both':
		loc_info = final_df.drop(['level_0', 'level_1'], axis=1).iloc[:, :]
	elif relationships == 'Propagates':
		loc_info = propagates_df.drop(['index', 'level_0', 'level_1'], axis=1).iloc[:, :]
	else:
		loc_info = splits_merges_df.drop(['level_0', 'level_1'], axis=1).iloc[:, :]

	ox.settings.log_console = True #print log output to the console (terminal window)
	ox.settings.use_cache = True #cache HTTP responses locally instead of calling API repeatedly for the same request
	graph = ox.graph_from_place('Municipality of Chania', network_type='drive') #download and create a graph within the boundaries of the city

	for ind in loc_info.index:
		Xsrc = float(loc_info.iloc[[ind], [1]].values) #get longitude of starting point
		Ysrc = float(loc_info.iloc[[ind], [0]].values) #get latitude of starting point
		Xdst = float(loc_info.iloc[[ind], [3]].values) #get longitude of ending point
		Ydst = float(loc_info.iloc[[ind], [2]].values) #get latitude of ending point

		origin = ox.distance.nearest_nodes(graph, Xsrc,  Ysrc) #find the nearest node to the starting point
		destination = ox.distance.nearest_nodes(graph, Xdst, Ydst) #find the nearest node to the ending point
		route = ox.distance.shortest_path(graph, origin, destination, weight='length') #find shortest path from origin node to destination node
		color_num = loc_info['final_clusters'][ind] #color for each cluster according to the list of colors

		#in case we have more than 148 clusters
		if color_num < 148:
			color = cluster_colors[color_num]
		else:
			color = cluster_colors[color_num - 148]

		if origin != destination:
			if ind == 0:
				gdf_route = ox.utils_graph.route_to_gdf(graph, route, weight='length') #return a GeoDataFrame of the edge in a path
				route_map = gdf_route.explore(tiles='OpenStreetMap', tooltip=False, color=color, style_kwds=dict(opacity=0.6, weight=7)) #generate an interactive leaflet map based on GeoDataFrame
			else:
				gdf_route = ox.utils_graph.route_to_gdf(graph, route, weight='length') #return a GeoDataFrame of the edge in a path
				route_map = gdf_route.explore(tiles='OpenStreetMap', tooltip=False, color=color, style_kwds=dict(opacity=0.6, weight=7), m=route_map) #draw the plot on existing map instance

	markers_df = pd.read_csv('input/markers.csv', dtype={'marker_location':str})
	for ind in markers_df.index:
		message = '<b>Marker'+str(ind)+'</b>' #pop up message when clicking on marker
		cur_location = markers_df.loc[ind, 'marker_location'].split(' ') #location of each marker
		folium.Marker(location=[float(cur_location[0]), float(cur_location[1])], popup=message, icon=folium.Icon(color='red', icon='pushpin')).add_to(route_map) #add marker to the interactive map
	
	route_map.save('route_map.html')
	webbrowser.open('route_map.html')


if __name__ =="__main__":
	clustering_routine("data/October/Monday.csv", "17:00", "20:00", 2, "Both")