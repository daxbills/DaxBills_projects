import networkx as nx
import matplotlib.pyplot as plt
from map import MapMaker
import actions
from matplotlib.animation import FuncAnimation
from randomai import RandomAI
from rulebasedai import RuleBasedAI
class RiskGame:
    def __init__(self):
        self.game_map = MapMaker()
        self.game_actions = actions.GameActions(self.game_map)
        self.fig, self.ax = plt.subplots(figsize=(16, 12))
        self.pos = nx.kamada_kawai_layout(self.game_map.Risk_Map)
        self.current_player = 0
        self.turn_phase = "reinforce"  # reinforce → attack → fortify
        self.ai_players = [
            RandomAI(self.game_map, self.game_actions, 0),
            RuleBasedAI(self.game_map, self.game_actions, 1),
            RuleBasedAI(self.game_map, self.game_actions, 2),
        ]
        self.winner = None
        self.player_colors = {  # Match colors from map.py
            0: "blue",
            1: "red",
            2: "green",
            -1: "gray"
        }

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
        plt.pause(0.01)

    def next_phase(self):
        """Advances to the next phase of the turn"""
        if self.turn_phase == "reinforce":
            self.turn_phase = "attack"
        elif self.turn_phase == "attack":
            self.turn_phase = "fortify"
        else:
            self.turn_phase = "reinforce"
            self.next_player()

    def next_player(self):
        """Moves to the next player's turn"""
        self.current_player = (self.current_player + 1) % len(self.ai_players)
        # print(f"\nPlayer {self.current_player}'s turn starting...")

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
    game = RiskGame()
    game.play_demo()
