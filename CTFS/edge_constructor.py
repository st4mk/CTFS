#!/usr/bin/env python

import gmplot
import webbrowser
import pandas as pd


'''
	Get Edge Points from Random Points
'''
def get_edge_points(input_file):
	df = pd.read_csv(input_file)
	df[['latitude', 'longitude']] = df.geom.str.split(" ", expand = True) #get latitude and longitude (coordinates) of city's random points by spliting geom column in "POINT(latitude" and "longitude)" format

	df_doubles = df.pivot_table(columns = ['latitude','longitude'], aggfunc = 'size', sort = False).reset_index(name = 'count') #find duplicates in dataframe and store the number of them in count column
	edge_points = []

	for ind in df_doubles.index:
		count = df_doubles.iloc[[ind], [2]].to_string(index = False, header = False)

		#if duplicate then this point is an edge point
		if int(count) > 1: 
			lat = df_doubles.iloc[[ind], [0]].to_string(index = False, header = False).replace('POINT(', '') #from "POINT(latitude" to "latitude" format
			lng = df_doubles.iloc[[ind], [1]].to_string(index = False, header = False).replace(')', '') #from "longitude)" to "longitude" format

			edge_points.append([lng, lat]) #store the edge point

	edges_df = pd.DataFrame(edge_points, columns = ['longitude', 'latitude']) #convert list to dataframe
	edges_df.to_csv("edge_points.csv", index=False) #save dataframe to file


'''
	Mark and Plot Edge Points
''' 
def display_edge_points(edge_points_file):
	df = pd.read_csv(edge_points_file, dtype={'longitude':str, 'latitude':str})
	chaniaGmap = gmplot.GoogleMapPlotter(35.5127361, 24.0174443, 15) #draw a Google Map with specific center and zoom level

	for ind in df.index:
		templng = df.iloc[[ind], [0]].to_string(index = False, header = False)
		templat = df.iloc[[ind], [1]].to_string(index = False, header = False)

		chaniaGmap.marker(float(templng), float(templat), 'cornflowerblue') #put markers on edge points

	chaniaGmap.draw('chania_edge_points.html')
	webbrowser.open('chania_edge_points.html')


'''
	Find and Store Edges
'''
def find_edges(input_file, edge_points_file):
	df1 = pd.read_csv(edge_points_file, dtype={'longitude':str, 'latitude':str}) #first dataframe with city's edge points
	df2 = pd.read_csv(input_file) #second dataframe with city's random points
	edges = []

	df2[['latitude', 'longitude']] = df2.geom.str.split(" ", expand = True)

	for row in df1.index:
		point_lng = df1.iloc[[row], [0]].to_string(index = False, header = False) #get edge point's longitude
		point_lat = df1.iloc[[row], [1]].to_string(index = False, header = False) #get edge point's latitude

		for ind in df2.index:
			if ind != 0:
				tmp_prvid = df2.iloc[[ind-1], [0]].to_string(index = False, header = False) #get previous random point's id
				tmp_prvlat = df2.iloc[[ind-1], [2]].to_string(index = False, header = False).replace('POINT(', '') #get previous random point's latitude 
				tmp_prvlng = df2.iloc[[ind-1], [3]].to_string(index = False, header = False).replace(')', '') #get previous random point's longitude
			if ind != len(df2) - 1:
				tmp_nxtid = df2.iloc[[ind+1], [0]].to_string(index = False, header = False) #get next random point's id
				tmp_nxtlat = df2.iloc[[ind+1], [2]].to_string(index = False, header = False).replace('POINT(', '') #get next random point's latitude 
				tmp_nxtlng = df2.iloc[[ind+1], [3]].to_string(index = False, header = False).replace(')', '') #get next random point's longitude

			tmp_id = df2.iloc[[ind], [0]].to_string(index = False, header = False) #get current random point's id
			tmp_lat = df2.iloc[[ind], [2]].to_string(index = False, header = False).replace('POINT(', '') #get current random point's latitude 
			tmp_lng = df2.iloc[[ind], [3]].to_string(index = False, header = False).replace(')', '') #get current random point's longitude

			#if current random point is an edge point
			if (point_lng == tmp_lng) and (point_lat == tmp_lat):
				#check the id of next random point, if true we got an edge from current (edge) point to next point
				if tmp_id == tmp_nxtid:
					edges.append([point_lng, point_lat, tmp_nxtlng, tmp_nxtlat])
					print('Entry from #1..')
				#else we got an edge from previous point to current (edge) point
				else:
					edges.append([tmp_prvlng, tmp_prvlat, point_lng, point_lat])
					print('Entry from #2..')

	edges_df = pd.DataFrame(edges, columns = ['source_lng', 'source_lat', 'destination_lng', 'destination_lat'])
	final_df = edges_df.drop_duplicates()
	final_df.to_csv("edges.csv", index=False) #the actual edges of the network


'''
	Find Edge Points in Linestrings
'''
def find_linestrings(input_file, edge_points_file):
	df1 = pd.read_csv(edge_points_file, dtype={'longitude':str, 'latitude':str}) #first dataframe with city's edge points
	df2 = pd.read_csv(input_file) #second dataframe with city's linestrings
	edges = []

	for row in df1.index:
		point_lng = df1.iloc[[row], [0]].to_string(index = False, header = False)
		point_lat = df1.iloc[[row], [1]].to_string(index = False, header = False)
		check_point = point_lat+' '+point_lng #set a "latitude longitude" format for the edge point
		print(check_point)

		for ind in df2.index:
			cur_linestring = df2.iloc[[ind], [1]].to_string(index = False, header = False)

			if check_point in cur_linestring: 
				cur_linestring = cur_linestring.split(',')
				src_coords = cur_linestring[0].split(' ') #get starting coordinates of linestring
				dst_coords = cur_linestring[-1].split(' ') #get ending coordinates of linestring
				edges.append([src_coords[1], src_coords[0].replace('LINESTRING(', ''), dst_coords[1].replace(')', ''), dst_coords[0]]) #store coordinates in proper format for later use on web scrapping (Google Maps)
				print('New Entry..')

	edges_df = pd.DataFrame(edges, columns = ['source_lng', 'source_lat', 'destination_lng', 'destination_lat'])
	final_df = edges_df.drop_duplicates()
	final_df.to_csv("linestring_edges.csv", index=False) #the hypothetical (linestring) edges of the network

'''
	Main Program 
'''
if __name__ =="__main__":

	get_edge_points('input/chania_osm_points.csv')
	display_edge_points('edge_points.csv')
	find_edges('input/chania_osm_points.csv', 'edge_points.csv')
	find_linestrings('input/chania_osm_linestrings.csv', 'edge_points.csv')
