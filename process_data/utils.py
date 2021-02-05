# from pathlib import Path
# import gmaps
# import gmaps.datasets
#
#
# # GOOGLE_API_KEY = "AIzaSyA6LpI23z8XAvK7k4Hg1aIBoHgmlsqtxak"
# GOOGLE_API_KEY = "AIzaSyCaaTAK0Iik7x8EK4WQdmj2liUooosOzvM"
#
# gmaps.configure(api_key=GOOGLE_API_KEY)
#
# df = gmaps.datasets.load_dataset_as_df('starbucks_kfc_uk')
# starbucks_df = df[df['chain_name'] == 'starbucks']
# starbucks_df = starbucks_df[['latitude', 'longitude']]
# starbucks_layer = gmaps.symbol_layer(
#                 starbucks_df, fill_color='green', stroke_color='green', scale=2
#                 )
# fig = gmaps.figure()
# fig.add_layer(starbucks_layer)
# fig
#
import folium
#m=folium.Map(location=[28.644800, 77.216721])
m=folium.Map(location=[52.233192,21.00313])
m