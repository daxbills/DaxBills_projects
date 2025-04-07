import networkx as nx
import matplotlib.pyplot as plt
from map import MapMaker
import actions
from matplotlib.animation import FuncAnimation
from randomai import RandomAI
from rulebasedai import RuleBasedAI

class RiskGame:
    def __init__(self, num_players=6):
        self.num_players = num_players
        self.game_map = MapMaker(num_players)
        self.game_actions = actions.GameActions(self.game_map)
        self.fig, self.ax = plt.subplots(figsize=(16, 12))
        self.pos = nx.kamada_kawai_layout(self.game_map.Risk_Map)
        self.current_player = 0
        self.turn_phase = "reinforce"  # reinforce → attack → fortify
        self.ai_players = [
            RandomAI(self.game_map, self.game_actions, i) if i % 3 == 0 
            else RuleBasedAI(self.game_map, self.game_actions, i)
            for i in range(self.num_players)
        ]
        self.winner = None
        self.player_colors = self.generate_colors(num_players)
        self.player_colors[-1] = "gray"  # Neutral/unowned territories

    def generate_colors(self, num_players):
        cmap = plt.get_cmap("tab10")  # A colormap with 10 distinct colors
        return {i: cmap(i % 10) for i in range(num_players)}

    def check_winner(self):
        """Check if any player owns all territories"""
        owners = {self.game_map.Risk_Map.nodes[territory]["owner"] 
                 for territory in self.game_map.Risk_Map.nodes}
        if len(owners) == 1:
            self.winner = owners.pop()
            return True
        return False
    
    def update_display(self, frame):
        """Updates the display using the enhanced visualization"""
        self.ax.clear()
        
        # Prepare data for drawing
        node_colors = []
        labels = {}
        army_labels = {}
        
        for territory in self.game_map.Risk_Map.nodes:
            owner = self.game_map.Risk_Map.nodes[territory]["owner"]
            armies = self.game_map.Risk_Map.nodes[territory]["armies"]
            node_colors.append(self.player_colors.get(owner, "gray"))
            labels[territory] = territory
            army_labels[territory] = str(armies)

        # Draw nodes
        nx.draw_networkx_nodes(
            self.game_map.Risk_Map, self.pos,
            ax=self.ax,
            node_size=1800,
            node_color=node_colors,
            edgecolors="black",
            linewidths=0.8
        )
        
        # Draw territory names
        nx.draw_networkx_labels(
            self.game_map.Risk_Map, self.pos,
            labels=labels,
            ax=self.ax,
            font_size=8,
            font_weight="bold"
        )
        
        # Draw troop counts
        text_pos = {k: (v[0], v[1]-0.05) for k, v in self.pos.items()}
        nx.draw_networkx_labels(
            self.game_map.Risk_Map, text_pos,
            labels=army_labels,
            ax=self.ax,
            font_size=8,
            font_color="black",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, boxstyle="round,pad=0.3")
        )
        
        # Draw connections
        nx.draw_networkx_edges(
            self.game_map.Risk_Map, self.pos,
            ax=self.ax,
            width=0.7,
            edge_color="gray",
            alpha=0.5
        )
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label=f'Player {i}',
                      markerfacecolor=color, markersize=10)
            for i, color in self.player_colors.items() if i != -1
        ]
        self.ax.legend(handles=legend_elements, loc='upper right')
        
        title = f"Player {self.current_player}'s Turn - {self.turn_phase.capitalize()} Phase"
        self.ax.set_title(title)
        plt.pause(0.005)

    def next_phase(self):
        """Advances to the next phase of the turn"""
        if self.turn_phase == "reinforce":
            self.turn_phase = "attack"
        elif self.turn_phase == "attack":
            self.turn_phase = "fortify"
        else:
            self.turn_phase = "reinforce"
            self.next_turn()

    def next_turn(self):
        """Moves to the next player, skipping those with no territories."""
        for _ in range(self.num_players):  # Avoid infinite loops
            self.current_player = (self.current_player + 1) % self.num_players
            if self.player_has_territories(self.current_player):
                break  # Stop once a valid player is found

        print(f"Next turn: Player {self.current_player}")


    def player_has_territories(self, player_id):
        """Returns True if the player controls at least one territory."""
        return any(self.game_map.Risk_Map.nodes[t]["owner"] == player_id for t in self.game_map.Risk_Map.nodes)


    def play_demo(self):
        """Fast-paced game until one player conquers all territories"""
        turn = 0
        while not self.check_winner():
            print(f"\n=== Turn {turn + 1} ===")
            
            # Reinforce phase
            self.turn_phase = "reinforce"
            self.update_display(turn)
            self.ai_players[self.current_player].reinforce_phase()
            self.next_phase()
            
            # Attack phase
            self.update_display(turn)
            self.ai_players[self.current_player].attack_phase()
            self.next_phase()
            
            # Fortify phase
            self.update_display(turn)
            self.ai_players[self.current_player].fortify_phase()
            self.next_phase()
            
            turn += 1
        
        print(f"\nPlayer {self.winner} has conquered the world in {turn} turns!")
        plt.pause(2)


if __name__ == "__main__":
    game = RiskGame(num_players=5)  # Now with 5 players
    game.play_demo()
