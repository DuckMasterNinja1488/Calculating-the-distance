import json
import requests
from geopy import distance
import pprint
import folium
from flask import Flask
import os
from dotenv import load_dotenv


def open_map():
    with open("index.html", encoding = "UTF8") as file:
        return file.read()


def get_coordinates(apikey, address):
    url = "https://geocode-maps.yandex.ru/1.x"
    params = {
        "geocode": address,
        "apikey": apikey,
        "format": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    geo_objects = response.json()['response']['GeoObjectCollection']['featureMember']
    if not geo_objects:
        return None
    location = geo_objects[0]['GeoObject']['Point']['pos']
    longitude, latitude = location.split(" ")
    return latitude, longitude


def get_stations():
    with open('charging_stations_by.json', 'r', encoding="UTF8") as file:
        stations = json.load(file)
    return stations


def main():
    load_dotenv()
    key = os.getenv("API_KEY")
    location = input("Где вы сечас находитесть? ")
    all_info_station = []
    stations=get_stations()
    coordinates = get_coordinates(key, location)
    for station in stations:
        station_name = station["name"]
        station_latitude = station["latitude"]
        station_longitude = station["longitude"]
        station_coord = station_latitude, station_longitude
        dist = distance.distance(coordinates, station_coord).km
        info_station = {
            'title': station_name,
            'distance': dist,
            'latitude': station_latitude,
            'longitude': station_longitude
        }
        all_info_station.append(info_station)
    sorted_stations = sorted(all_info_station, key=lambda x: x['distance'])[:15]
    pprint.pprint(sorted_stations)
    map = folium.Map(location=coordinates, zoom_start=14)
    for charging in sorted_stations:
        folium.Marker(
            location=[charging['latitude'],charging['longitude']],
            tooltip="Click me!",
            popup=charging['title'],
            icon=folium.Icon(icon="cloud"),
        ).add_to(map)
    map.save("index.html")
    app = Flask(__name__)
    app.add_url_rule('/', 'charging map', open_map)
    app.run('0.0.0.0')


if __name__ == "__main__":
   main()