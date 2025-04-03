import networkx as nx
import matplotlib.pyplot as plt
import random


class MapMaker:
    def __init__(self):
        self.Risk_Map = nx.Graph()
        self.continents = []
        self.define_continents()
        self.add_intercontinental_connections()
        self.initialize_territories()
        self.assign_territories()

    def continent_creator(self, nodes, edges, name):
        """Creates a continent graph."""
        continent = nx.Graph(name=name)
        continent.add_nodes_from(nodes)
        continent.add_edges_from(edges)
        return continent

    def define_continents(self):
        """Defines all continents and adds them to the map."""
        continents_data = {
            "North America": (
                ["Alaska", "Northwest Territory", "Alberta", "Ontario", "Greenland",
                 "Western United States", "Eastern United States", "Central America", "Quebec"],
                [("Alaska", "Northwest Territory"), ("Alaska", "Alberta"), ("Northwest Territory", "Alberta"),
                 ("Northwest Territory", "Ontario"), ("Northwest Territory", "Greenland"),
                 ("Ontario", "Greenland"), ("Western United States", "Ontario"), ("Alberta", "Ontario"),
                 ("Alberta", "Western United States"), ("Ontario", "Quebec"),
                 ("Ontario", "Eastern United States"), ("Quebec", "Greenland"),
                 ("Quebec", "Eastern United States"), ("Western United States", "Eastern United States"),
                 ("Western United States", "Central America"), ("Eastern United States", "Central America")]
            ),
            "South America": (
                ["Venezuela", "Brazil", "Peru", "Argentina"],
                [("Venezuela", "Brazil"), ("Venezuela", "Peru"), ("Brazil", "Peru"),
                 ("Brazil", "Argentina"), ("Peru", "Argentina")]
            ),
            "Africa": (
                ["North Africa", "Egypt", "East Africa", "Congo", "South Africa", "Madagascar"],
                [("North Africa", "Egypt"), ("North Africa", "East Africa"), ("North Africa", "Congo"),
                 ("Congo", "East Africa"), ("Congo", "South Africa"), ("South Africa", "Madagascar"),
                 ("South Africa", "East Africa"), ("East Africa", "Egypt"), ("East Africa", "Madagascar")]
            ),
            "Europe": (
                ["Iceland", "Great Britain", "Scandinavia", "Ukraine", "Northern Europe", "Western Europe", "Southern Europe"],
                [("Iceland", "Scandinavia"), ("Iceland", "Great Britain"), ("Great Britain", "Northern Europe"),
                 ("Great Britain", "Western Europe"), ("Scandinavia", "Northern Europe"),
                 ("Scandinavia", "Ukraine"), ("Northern Europe", "Ukraine"), ("Northern Europe", "Western Europe"),
                 ("Northern Europe", "Southern Europe"), ("Western Europe", "Southern Europe"),
                 ("Southern Europe", "Ukraine")]
            ),
            "Asia": (
                ["Ural", "Siberia", "Yakutsk", "Kamchatka", "Irkutsk", "Mongolia", "Japan",
                 "China", "Siam", "India", "Middle East", "Afghanistan"],
                [("Ural", "Siberia"), ("Ural", "Afghanistan"), ("Ural", "China"),
                 ("Afghanistan", "China"), ("Afghanistan", "Middle East"), ("Afghanistan", "India"),
                 ("Middle East", "India"), ("India", "China"), ("India", "Siam"),
                 ("Mongolia", "Japan"), ("Mongolia", "Irkutsk"), ("Mongolia", "Kamchatka"),
                 ("Mongolia", "Yakutsk"), ("Mongolia", "Siberia"), ("Siberia", "China"),
                 ("China", "Siam"), ("Siberia", "Yakutsk"), ("Siberia", "Irkutsk"),
                 ("Yakutsk", "Irkutsk"), ("Yakutsk", "Kamchatka"), ("Irkutsk", "Kamchatka"),
                 ("Japan", "Kamchatka")]
            ),
            "Australia": (
                ["Indonesia", "New Guinea", "Western Australia", "Eastern Australia"],
                [("Indonesia", "New Guinea"), ("Indonesia", "Western Australia"),
                 ("Western Australia", "Eastern Australia"), ("Western Australia", "New Guinea"),
                 ("Eastern Australia", "New Guinea")]
            ),
        }

        for name, (territories, connections) in continents_data.items():
            continent = self.continent_creator(territories, connections, name)
            self.continents.append(continent)
            self.Risk_Map = nx.compose(self.Risk_Map, continent)

    def add_intercontinental_connections(self):
        """Adds intercontinental connections to the Risk map."""
        intercontinental_connections = [
            ("Venezuela", "Central America"), ("Brazil", "North Africa"), ("Iceland", "Greenland"),
            ("Western Europe", "North Africa"), ("Southern Europe", "North Africa"),
            ("Southern Europe", "Egypt"), ("Middle East", "Egypt"), ("Middle East", "Southern Europe"),
            ("Middle East", "Ukraine"), ("Afghanistan", "Ukraine"), ("Ural", "Ukraine"),
            ("Alaska", "Kamchatka"), ("Indonesia", "Siam")
        ]

        for edge in intercontinental_connections:
            if all(node in self.Risk_Map.nodes for node in edge):
                self.Risk_Map.add_edge(*edge)

    def initialize_territories(self):
        """Initializes ownership and army counts for each territory."""
        for territory in self.Risk_Map.nodes:
            self.Risk_Map.nodes[territory]["owner"] = -1  # No owner initially
            self.Risk_Map.nodes[territory]["armies"] = 0  # No armies initially

    def assign_territories(self):
        """Randomly assigns territories to players and gives them a random number of armies."""
        players = [0, 1, 2] 
        territories = list(self.Risk_Map.nodes)
        random.shuffle(territories)  # Shuffle for randomness

        for i, territory in enumerate(territories):
            self.Risk_Map.nodes[territory]["owner"] = players[i % len(players)]  # Alternate ownership
            self.Risk_Map.nodes[territory]["armies"] = random.randint(1, 5)  # Random initial troops (1-5)


    def draw_map(self):
        """Draws the Risk map with clear troop numbers and ownership visualization."""
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(self.Risk_Map, seed=42)
        
        # Create color mapping for players
        player_colors = {
            -1: "gray",   # Neutral/unowned
            0: "lightblue",
            1: "red",
            2: "green"
        }
        
        # Prepare node colors and labels
        node_colors = []
        labels = {}
        army_labels = {}
        
        for territory in self.Risk_Map.nodes:
            owner = self.Risk_Map.nodes[territory]["owner"]
            armies = self.Risk_Map.nodes[territory]["armies"]
            
            node_colors.append(player_colors.get(owner, "gray"))
            labels[territory] = territory
            army_labels[territory] = str(armies)

        # Draw the base map
        nx.draw_networkx_nodes(
            self.Risk_Map, pos,
            node_size=2000,
            node_color=node_colors,
            edgecolors="black",
            linewidths=1
        )
        
        # Draw territory names
        nx.draw_networkx_labels(
            self.Risk_Map, pos,
            labels=labels,
            font_size=8,
            font_weight="bold"
        )
        
        # Draw troop numbers separately for better visibility
        text_pos = {k: (v[0], v[1]-0.05) for k, v in pos.items()}  # Offset below territory name
        nx.draw_networkx_labels(
            self.Risk_Map, text_pos,
            labels=army_labels,
            font_size=10,
            font_color="black",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, boxstyle="round,pad=0.3")
        )
        
        # Draw edges (connections between territories)
        nx.draw_networkx_edges(
            self.Risk_Map, pos,
            width=1,
            edge_color="gray",
            alpha=0.7
        )
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='Player 0',
                      markerfacecolor='lightblue', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', label='Player 1',
                      markerfacecolor='lightcoral', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', label='Player 2',
                      markerfacecolor='plum', markersize=10)
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.title("Risk Game Map - Territory Ownership and Army Counts")
        plt.axis('off')
        plt.tight_layout()
        plt.show()