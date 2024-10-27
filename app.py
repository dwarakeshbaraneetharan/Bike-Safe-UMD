from flask import Flask, render_template, request, jsonify
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point
import json

app = Flask(__name__)

# Load the UMD comprehensive map data with costs
data = gpd.read_file("umd_comprehensive_with_costs.geojson")

# Load building data
with open('umd_buildings.json') as f:
    buildings = json.load(f)

# Initialize a graph
G = nx.Graph()

# Add edges to the graph based on geometry and costs
for _, row in data.iterrows():
    if row['geometry'].geom_type == 'LineString':
        coords = list(row['geometry'].coords)
        for i in range(len(coords) - 1):
            G.add_edge(coords[i], coords[i + 1], weight=row['cost'])

# Function to find the nearest node
def get_nearest_node(point, graph):
    return min(graph.nodes, key=lambda n: Point(n).distance(point))

# Function to calculate route between two points
def calculate_route(start, end):
    start_node = get_nearest_node(Point(start), G)
    end_node = get_nearest_node(Point(end), G)
    print(f"Start Node: {start_node}, End Node: {end_node}")  # Debugging line
    route = nx.shortest_path(G, start_node, end_node, weight='weight')
    print(f"Route: {route}")  # Debugging line
    return route


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_destination', methods=['POST'])
def submit_destination():
    destination = request.form.get('destination', '').strip().lower()
    matches = [b['name'] for b in buildings if destination in b['name'].lower()]
    return render_template('destination_select.html', matches=matches)

@app.route('/get_route', methods=['POST'])
def get_route():
    data = request.json
    user_location = data.get('user_location')
    destination_name = data.get('destination_name')

    # Find destination coordinates
    dest_coords = None
    for building in buildings:
        if building['name'].lower() == destination_name.lower():
            dest_coords = building['coordinates'][0][0]  # Extract the first coordinate pair
            break

    if dest_coords is None:
        return jsonify({'error': 'Destination not found'}), 404

    # Calculate route
    print(f"User Location: {user_location}, Destination Coordinates: {dest_coords}")  # Debugging line
    route = calculate_route(user_location, dest_coords)

    # Prepare route for response
    route_coords = [(lat, lon) for lon, lat in route]
    return jsonify({'route': route_coords})

@app.route('/map')
def map_view():
    destination = request.args.get('destination')
    return render_template('map.html', destination=destination)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
