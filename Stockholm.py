import geopandas as gpd
import folium
import folium.plugins
import requests
import json
from shapely.geometry import Polygon, shape


def main():

    #initalize map titles
    min_lon, max_lon = 17.769757866310904, 18.398198129697317
    min_lat, max_lat = 59.216339768502074, 59.4527626869623

    m = folium.Map(location=(59.330179255373515, 18.057957648090127),
        max_bounds=True,
        zoom_start = 11,
        min_zoom=11,
        max_zoom=20,
        control_scale=True,
        tiles="cartodb positron",
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
        min_zoom=11,
        max_zoom=20,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
    ).add_to(m)

    #All Other map features
    city(m)



    #Add location request
    folium.plugins.LocateControl(auto_start=False).add_to(m)

    #Add layer control
    folium.LayerControl().add_to(m)

    #map generation
    print("sucessfully generated map.")
    file_name = 'E:\TUE\Projects\Jet-Lag-Stockholm\Stockholm'
    m.save(file_name + '.html')

    #Function to plop the cities
    
def city(m):
    with open("E:\TUE\Projects\Jet-Lag-Stockholm\game-area.json", 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    cleaned_data = []
    for item in raw_data['results']:
        geom = shape(item['geo_shape']['geometry'])
        kom_name = item['kom_name'][0]
        cleaned_data.append({
            'geometry': geom,
            'Name': kom_name
        })

    #build a GeoDataFrame with the cleaned data
    game_area = gpd.GeoDataFrame(cleaned_data, crs="EPSG:4326")

    '''
    Create a mask, which plots world_borer - game_area, 
    '''
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
        name="Municipalities",
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 3
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['Name'],
            aliases=['Municipality:'],
        ),
        show = True
    ).add_to(m)


if __name__ == "__main__":
    main()
