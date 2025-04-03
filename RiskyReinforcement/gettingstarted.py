import networkx as nx
import matplotlib.pyplot as plt
import random 
import numpy as np

Risk_Map = nx.Graph()
Risk_Map.clear()

def continent_creater(nodes, edges, name, color = "red"):
    continent = nx.Graph(name=name)
    continent.add_nodes_from(nodes)
    continent.add_edges_from(edges)
    return continent


north_america_territories = [
    "Alaska", "Northwest Territory", "Alberta", "Ontario", "Greenland",
    "Western United States", "Eastern United States", "Central America", "Quebec"
]

north_america_connections = [
    ("Alaska", "Northwest Territory"),
    ("Alaska", "Alberta"),
    ("Northwest Territory", "Alberta"),
    ("Northwest Territory", "Ontario"),
    ("Northwest Territory", "Greenland"),
    ("Ontario", "Greenland"),
    ("Western United States","Ontario"),
    ("Alberta", "Ontario"),
    ("Alberta", "Western United States"),
    ("Ontario", "Quebec"),
    ("Ontario", "Eastern United States"),
    ("Quebec", "Greenland"),
    ("Quebec", "Eastern United States"),
    ("Western United States", "Eastern United States"),
    ("Western United States", "Central America"),
    ("Eastern United States", "Central America"),

]

south_america_territories = ["Venezuela", "Brazil", "Peru", "Argentina"]

south_america_connections = [
    ("Venezuela", "Brazil"),
    ("Venezuela", "Peru"),
    ("Brazil", "Peru"),
    ("Brazil", "Argentina"),
    ("Peru", "Argentina")
]

African_territories =["North Africa","Egypt","East Africa","Congo","South Africa","Madagascar"]
African_connections =[
    ("North Africa", "Egypt"),
    ("North Africa", "East Africa"),
    ("North Africa", "Congo"),
    ("Congo","East Africa"),
    ("Congo","South Africa"),
    ("South Africa","Madagascar"),
    ("South Africa","East Africa"),
    ("East Africa","Egypt"),
    ("East Africa","Madagascar")
]

European_territories = ["Iceland","Great Britain","Scandinavia","Ukraine","Northern Europe","Western Europe","Southern Europe"]
European_connections =[
    ("Iceland","Scandinavia"),
    ("Iceland","Great Britain"),
    ("Great Britain","Northern Europe"),
    ("Great Britain","Western Europe"),
    ("Scandinavia","Northern Europe"),
    ("Scandinavia","Ukraine"),
    ("Northern Europe","Ukraine"),
    ("Northern Europe","Western Europe"),
    ("Northern Europe","Southern Europe"),
    ("Western Europe","Southern Europe"),
    ("Southern Europe","Ukraine"),
]
Asia_territories=["Ural","Siberia","Yakutsk","Kamchatka","Irkutsk","Mongolia","Japan","China","Siam","India","Middle East","Afghanistan"]
Asia_connections=[
    ("Ural","Siberia"),("Ural","Afghanistan"),("Ural","China"),
    ("Afghanistan","China"),("Afghanistan","Middle East"),("Afghanistan","India"),
    ("Middle East","India"),("India","China"),("India","Siam"),
    ("Mongolia","Japan"),("Mongolia","Irkutsk"),("Mongolia","Kamchatka"),("Mongolia","Yakutsk"),("Mongolia","Siberia"),
    ("Siberia","China"),("China","Siam"),("Siberia","Yakutsk"),("Siberia","Irkutsk"),
    ("Yakutsk","Irkutsk"),("Yakutsk","Kamchatka"),
    ("Irkutsk","Kamchatka"),("Japan","Kamchatka")
]

Australia_territories=["Indonesia","New Guinea","Western Australia","Eastern Australia"]
Australia_connections=[("Indonesia","New Guinea"),("Indonesia","Western Australia"),
    ("Western Australia","Eastern Australia"),("Western Australia","New Guinea"),("Eastern Australia","New Guinea")]

continents =[]
Sa = continent_creater(south_america_territories, south_america_connections, "South America")
Na = continent_creater(north_america_territories, north_america_connections, "North America")
Af = continent_creater(African_territories, African_connections, "Africa")
Eu = continent_creater(European_territories, European_connections, "Europe")
As =continent_creater(Asia_territories, Asia_connections, "Asia")
Au =continent_creater(Australia_territories, Australia_connections, "Australia")

continents.append(Sa)
continents.append(Na)
continents.append(Af)
continents.append(Eu)
continents.append(As)
continents.append(Au)

for i in continents:
    Risk_Map= nx.compose(Risk_Map,i)

intercontinental_connections = [
    ("Venezuela", "Central America"),
    ("Brazil", "North Africa"),
    ("Iceland", "Greenland"),
    ("Western Europe", "North Africa"),
    ("Southern Europe", "North Africa"),
    ("Southern Europe", "Egypt"),
    ("Middle East", "Egypt"),
    ("Middle East", "Southern Europe"),
    ("Middle East", "Ukraine"),
    ("Afghanistan", "Ukraine"),
    ("Ural", "Ukraine"),
    ("Alaska", "Kamchatka"),
    ("Indonesia","Siam")
]

for edge in intercontinental_connections:
    if all(node in Risk_Map.nodes for node in edge):
        Risk_Map.add_edge(*edge)

isolated_nodes = list(nx.isolates(Risk_Map))
Risk_Map.remove_nodes_from(isolated_nodes)


for territory in Risk_Map.nodes:
    Risk_Map.nodes[territory]["owner"] = -1  # No owner initially
    Risk_Map.nodes[territory]["armies"] = 0  # No armies initially

players = [0, 1]  # Two players
territories = list(Risk_Map.nodes)
random.shuffle(territories)  # Shuffle for randomness

# Assign territories to players
for i, territory in enumerate(territories):
    Risk_Map.nodes[territory]["owner"] = players[i % len(players)]  # Alternating ownership
    Risk_Map.nodes[territory]["armies"] = random.randint(1, 5)  # Random initial troops (1-5)








color_palette = [
    "red", "blue", "green", "purple", "orange", "brown", "pink", "olive", "yellow"
]
node_colors = [random.choice(color_palette) for _ in Risk_Map.nodes]
continent_colors = {
    "North America": "red",
    "South America": "blue",
    "Africa": "green",
    "Europe": "purple",
    "Asia": "orange",
    "Australia": "brown"
}
territory_to_continent = {}

for continent, territories in zip(
    ["North America", "South America", "Africa", "Europe", "Asia", "Australia"], 
    [north_america_territories, south_america_territories, African_territories, 
     European_territories, Asia_territories, Australia_territories]
):
    for territory in territories:
        territory_to_continent[territory] = continent
node_colors = [continent_colors[territory_to_continent[node]] for node in Risk_Map.nodes]


def rotate_layout(pos, angle):
    """Rotate node positions by a given angle (in degrees)."""
    theta = np.radians(angle)
    rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    return {node: np.dot(rotation_matrix, coords) for node, coords in pos.items()}

def flip_horizontal(pos):
    """Flip the layout horizontally (mirror effect)."""
    return {node: (-x, y) for node, (x, y) in pos.items()}

plt.figure(figsize=(16, 12))
pos = nx.kamada_kawai_layout(Risk_Map)
pos = rotate_layout(pos, 60)
# pos = flip_horizontal(pos) 


def spread_intercontinental_edges(pos, stretch_factor=1.1):
    """Move intercontinental nodes farther apart."""
    for edge in intercontinental_connections:
        node1, node2 = edge
        if node1 in pos and node2 in pos:
            mid_x = (pos[node1][0] + pos[node2][0]) / 2
            mid_y = (pos[node1][1] + pos[node2][1]) / 2
            pos[node1] = (pos[node1][0] + (pos[node1][0] - mid_x) * (stretch_factor - 1), 
                          pos[node1][1] + (pos[node1][1] - mid_y) * (stretch_factor - 1))
            pos[node2] = (pos[node2][0] + (pos[node2][0] - mid_x) * (stretch_factor - 1), 
                          pos[node2][1] + (pos[node2][1] - mid_y) * (stretch_factor - 1))

# Apply stretching
spread_intercontinental_edges(pos, stretch_factor=1.1)

nx.draw(
    Risk_Map, pos, with_labels=True, 
    node_color=node_colors, edge_color="black", 
    node_size=2200, font_size=10, font_color="black"
)

plt.title("Risk Board")
plt.show()

