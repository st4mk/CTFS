/////// The Application ///////

Run the application and display the results ($./app.py)

	Notes: Choose the options you want and hit "Show Results" button.
		   There are samples for some weekdays and specific hours in data/October.
		   e.g. Choose a "Monday" of "October", "5.00pm - 8.00pm", "10 mins" interval and "Both" traffic relationships.

		   If there is no data for your set of options, a message will show up.
		   You can see that the app is running on your terminal.



/////// Back-end Functionality ///////


1. -(One-time run)- Construct the edges ($./edge_constructor.py)

	Internal functions: get_edge_points('input/chania_osm_points.csv') -> finds the edge points of the road network and
																 				stores them into "edge_points.csv"

						display_edge_points('edge_points.csv') -> displays edge points as markers on the map, 																							creating "chania_edge_points.html"

						find_edges('input/chania_osm_points.csv', 'edge_points.csv') -> finds the edges of the network and
																		 						stores them into "edges.csv"

						find_linestrings('input/chania_osm_linestrings.csv', 'edge_points.csv') -> finds the linestring (hypothetical) 
																	edges of the network and stores them into "linestring_edges.csv"


2. Scrape some data ($./data_miner.py -d <duration_in_hrs> -s <time_slots_in_mins>)
	
	E.g. $./data_miner.py -d 4 -s 10 -> scrape data for 4 hours, start a new session every 10 minutes

	Notes: Current implementation is on hyper-edges ("linestring_edges.csv"), but can also be 
		   implemented on actual edges by changing line 22 to "edges.csv".
		   Duration depends on your needs, sessions depend on your resources.
		   Might need to replace "chromedriver-linux64" with an updated version (also check the path at line 119).
		   Produces a "Day_name(YYYY-MM-DD).csv" file in "data" folder.
		   If another file with same name exists in "data" folder, it will be extended with the data scraped.


3. Merge two data files ($./data_merge.py)

	Notes: At lines 8 and 9, insert the path of data files to be merged.
		   Produces a "Day_name(merged).csv" file in "data" folder.
		   If another file with same name exists in "data" folder, it will be replaced by the new one.


4. Move data files into the correct month folder (manually)

	Notes: When you have your data file, either from scraping or a merged one, you need to move it
		   to a proper month folder, inside "data" folder, renaming it as the day it represents, e.g. "Friday.csv".
		   There are samples in the "October" folder.

