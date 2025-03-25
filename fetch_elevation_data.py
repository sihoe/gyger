import gpxpy
import requests
import json
from geopy.distance import geodesic
import sys

# ---- Les GPX-fil ----
gpx_file = "Bingenrunden.gpx"
with open(gpx_file, "r") as f:
    gpx = gpxpy.parse(f)

# ---- Hent koordinater fra GPX ----
route = [(point.latitude, point.longitude) for track in gpx.tracks for segment in track.segments for point in segment.points]

# ---- Beregn distanse ----
distances = [0]
total_distance = 0
for i in range(1, len(route)):
    total_distance += geodesic(route[i-1], route[i]).km
    distances.append(total_distance)

# ---- Definer POI-ene ----
poi_list = [
    {"name": "Letmolivatnet badeplass", "lat": 59.928924696, "lon": 9.592851714},
    {"name": "Lampeland Hotell", "lat": 59.834554551, "lon": 9.578144874},
    {"name": "Bingen kapell", "lat": 59.88918667, "lon": 9.768934104},
    {"name": "Vatnebrynnvatnet friluftsområde og badeplass", "lat": 59.87183139, "lon": 9.54320036},
    {"name": "Kløfterhølen badeplass", "lat": 59.837962182, "lon": 9.575067953},
    {"name": "Friluftsbua", "lat": 59.8352615, "lon": 9.5774824},
    {"name": "Lyngdal kirke", "lat": 59.9106723, "lon": 9.5286842}
]

# Finn nærmeste punkt på ruten for hver POI
for poi in poi_list:
    closest_point = min(route, key=lambda p: geodesic((p[0], p[1]), (poi["lat"], poi["lon"])).km)
    closest_index = route.index(closest_point)
    poi["distance"] = distances[closest_index]

# ---- Hent høydeverdier ----
def get_elevation_data(coords):
    elevations = []
    for i, (lat, lon) in enumerate(coords):
        print(f"Henter høyde for punkt {i+1} av {len(coords)}...")
        try:
            response = requests.get(f"https://api.opentopodata.org/v1/srtm90m?locations={lat},{lon}", timeout=10)
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                elevation = data["results"][0]["elevation"]
                elevations.append({"distance": distances[i], "elevation": elevation})
        except requests.exceptions.RequestException as e:
            print(f"Feil ved henting av høyde: {e}")
            sys.exit(1)
    return elevations

elevation_data = get_elevation_data(route)

# Legg POI-er inn i elevation_data
for poi in poi_list:
    elevation_data.append({
        "distance": poi["distance"],
        "elevation": None,
        "name": poi["name"]
    })

# ---- Lagre elevation_data.json ----
with open("elevation_data.json", "w") as f:
    json.dump(elevation_data, f, indent=4)

print(f"✅ Ferdig! Data lagret i elevation_data.json (Total distanse: {total_distance:.2f} km).")
