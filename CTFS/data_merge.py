#!/usr/bin/env python

import pandas as pd
import calendar  

if __name__ == "__main__": 

	input_file2 = 'data/Sunday(2023-10-22).csv' #path for first input file
	input_file1 = 'data/Sunday(merged).csv' #path for second input file

	day_names = list(calendar.day_name) #list of week's day names

	pre_df1 = pd.read_csv(input_file1, dtype={'source_lng':str, 'source_lat':str, 'destination_lng':str, 'destination_lat':str})
	pre_df2 = pd.read_csv(input_file2)

	coords_df = pre_df1.iloc[:, 0:4] #keep edges' source and destination points coordinates

	df1 = pre_df1.drop(['source_lng', 'source_lat', 'destination_lng', 'destination_lat'], axis=1)
	df2 = pre_df2.drop(['source_lng', 'source_lat', 'destination_lng', 'destination_lat'], axis=1)

	merged_df = pd.concat([df1, df2], axis=1, join='inner') #merge the time series of both files
	sorted_df = merged_df.sort_index(axis=1, ascending=True) #sort them ascending by column
	last_df = pd.concat([coords_df, sorted_df], axis=1, join='inner') #merge sorted time series with coordinates
	final_df = last_df.T.drop_duplicates().T #remove duplicate columns

	file_name1 = input_file1.split('/')[-1].split('.')[0] #get the name of first file from its path
	file_name2 = input_file2.split('/')[-1].split('.')[0] #get the name of second file from its path

	if file_name1 in day_names:
		output_file_name = file_name1 + '(merged)' #e.g. file_name1 = "Friday"
	elif file_name2 in day_names:
		output_file_name = file_name2 + '(merged)' #e.g. file_name2 = "Friday"
	else:
		output_file_name = file_name1.split('(')[0] + '(merged)' #e.g. file_name1 = "Friday(YYYY/MM/DD)"

	final_df.to_csv(f'data/{output_file_name}.csv', index=False) #store as "Day_name(merged).csv"