import geopandas as gpd
import folium
import folium.plugins
import requests
import json
from shapely.geometry import Polygon, shape


def main():

    #initalize map titles
    min_lon, max_lon = 17.70891393315022, 18.536390448353895 #gotta increase these 
    min_lat, max_lat = 59.216339768502074, 59.4527626869623

    m = folium.Map(location=(59.330179255373515, 18.057957648090127),
        tiles="cartodb positron",
        max_bounds=True,
        zoom_start = 11,
        min_zoom=10,
        max_zoom=20,
        control_scale=True,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
    )

    cartonDB = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
    folium.TileLayer(
        max_bounds=True,
        tiles= cartonDB,
	    attr= '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
	    name = 'cartonDB',
        subdomains= 'abcd',
        zoom_start = 11,
        min_zoom=10,
        max_zoom=20,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
    ).add_to(m)

    #All Other map features
    municipalities(m)
    districts(m)
    M_lines(m)
    T_lines(m)
    M_stations(m)
    T_stations(m)

    #Add location request
    folium.plugins.LocateControl(auto_start=False).add_to(m)

    #Add layer control
    folium.LayerControl().add_to(m)

    #map generation
    print("sucessfully generated map.")
    file_name = r'E:\TUE\Projects\Jet-Lag-Stockholm\Stockholm'
    m.save(file_name + '.html')

    #Function to plop the cities
    
def municipalities(m):
    
    #read Stockholm json data
    raw_municialities = gpd.read_file(r"E:\TUE\Projects\Jet-Lag-Stockholm\sweden-municipalities2.geojson")

    #clean up data
    cleaned_data = []
    cleaned_data = raw_municialities[['name', 'geometry']]

    #build a GeoDataFrame with the cleaned data
    game_area = gpd.GeoDataFrame(cleaned_data, crs="EPSG:4326")

    #Create a mask, which plots world_borer - game_area,
    world_border = [[-180, -90], [-180, 90], [180, 90], [180, -90], [-180, -90]]
    world_poly = Polygon(world_border)
    world_gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[world_poly])
    mask_gdf = gpd.overlay(world_gdf, game_area, how='difference')
    
    #Add the masked layers to the map
    folium.GeoJson(
        mask_gdf,
        name="Out of Bounds",
        control=False
    ).add_to(m)
    


    #Add boundaries of municipalities to the map
    folium.GeoJson(
        game_area,
        name= "Municipalities",
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 3
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            aliases=['Municipality:']
        ),
        show = True
    ).add_to(m)
def districts(m):
    districts = gpd.read_file(r"E:\TUE\Projects\Jet-Lag-Stockholm\stockholm-districts.geojson")

    folium.GeoJson(
        districts,
        name = "Districts",
            style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 1
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            aliases=['Districts:'],
        ),
        show = True
    ).add_to(m)

def M_lines(m):
    metro_lines = gpd.read_file(r"E:\TUE\Projects\Jet-Lag-Stockholm\metro-lines.geojson")

    #reduce length of metro line names
    metro_lines['name'] = metro_lines['name'].str[:13]

    #plot metro lines
    folium.GeoJson(
        metro_lines,
        name = "Metro Lines",
            style_function=lambda x: {
            'color': 'blue',
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels = False
        ),
        show = True
    ).add_to(m)
def M_stations(m):
    raw_Mstations = gpd.read_file(r"E:\TUE\Projects\Jet-Lag-Stockholm\metro-stations.geojson")
    metro_stations = raw_Mstations[['name','geometry']]
    
    #plot metro lines
    folium.GeoJson(
        metro_stations,
        name = "Metro Stations",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='darkblue',
                icon='train-subway', 
                prefix='fa')
        ),
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels=False
        ),
        show = False
    ).add_to(m)

def T_lines(m):
    raw_TLines = gpd.read_file(r"E:\TUE\Projects\Jet-Lag-Stockholm\tram-lines.geojson")
    tram_lines = raw_TLines[['name','geometry']]

    #reduce length of tram line names
    tram_lines['name'] = tram_lines['name'].str[:10]

    #plot tram lines
    folium.GeoJson(
        tram_lines,
        name = "Tram Lines",
            style_function=lambda x: {
            'color': 'red',
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels = False
        ),
        show = True
    ).add_to(m)
def T_stations(m):
    raw_Tstations = gpd.read_file(r"E:\TUE\Projects\Jet-Lag-Stockholm\tram-stations.geojson")
    tram_stations = raw_Tstations[['name','geometry']].drop_duplicates(subset=['name'])
    
    #plot metro lines
    folium.GeoJson(
        tram_stations,
        name = "Tram Stations",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='red',
                icon='train-tram', 
                prefix='fa')
        ),
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels=False
        ),
        show = False
    ).add_to(m)


if __name__ == "__main__":
    main()
