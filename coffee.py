import json
import requests
from geopy.distance import geodesic
import folium
from decouple import config


API_KEY = config('API_KEY')
COFFEE_FILE = 'coffee.json'
OUTPUT_FILE = 'index.html'


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)


def main():
    with open(COFFEE_FILE, "r", encoding="CP1251") as my_file:
        data = json.load(my_file)

    address = input("Где вы находитесь? ")
    user_coords = fetch_coordinates(API_KEY, address)

    if user_coords:
        user_lat, user_lon = user_coords
    
        coffee_shops = []
    
        for coffee_shop in data:
            title = coffee_shop.get("Name", 0)
            lat = coffee_shop.get("Latitude_WGS84", 0)
            lon = coffee_shop.get("Longitude_WGS84", 0)
        
            if lat == 0 or lon == 0:
                continue
            
            shop_coords = (lat, lon)
            distance = geodesic(user_coords, shop_coords).kilometers
        
            coffee_info = {
                'title': title,
                'distance': distance,
                'latitude': lat,
                'longitude': lon
            }
        
            coffee_shops.append(coffee_info)
    
        nearest_coffees = sorted(coffee_shops, key=lambda x: x['distance'])[:5]
    
        coffee_map = folium.Map(location=[user_lat, user_lon], zoom_start=12)

        folium.Marker(
            [user_lat, user_lon],
            popup="Ваше местоположение",
            tooltip="Вы здесь",
            icon=folium.Icon(color='red', icon='user')
        ).add_to(coffee_map)

        for i, coffee in enumerate(nearest_coffees, 1):
            folium.Marker(
                [coffee['latitude'], coffee['longitude']],
                popup=f"{i}. {coffee['title']}",
                tooltip=f"{coffee['title']} ({coffee['distance']:.2f} км)",
                icon=folium.Icon(color='green', icon='coffee')
            ).add_to(coffee_map)

        coffee_map.save(OUTPUT_FILE)


if __name__ == '__main__':
    main()