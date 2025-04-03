import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
from map import MapMaker

class GameActions:
    def __init__(self, game_map):
        self.game_map = game_map  # An instance of MapMaker
        self.continent_bonuses = {
            "North America": 5,
            "South America": 2,
            "Europe": 5,
            "Africa": 3,
            "Asia": 7,
            "Australia": 2
        }

    def calculate_reinforcements(self, player):
        """Calculate total reinforcements including continent bonuses"""
        # Base reinforcements (minimum 3)
        owned_territories = [t for t in self.game_map.Risk_Map.nodes 
                            if self.game_map.Risk_Map.nodes[t]["owner"] == player]
        base_reinforce = max(3, len(owned_territories) // 3)
        
        # Continent bonuses
        continent_bonus = 0
        for continent in self.game_map.continents:
            continent_name = continent.graph.get('name', 'Unknown')
            if continent_name in self.continent_bonuses:
                if all(self.game_map.Risk_Map.nodes[t]["owner"] == player 
                       for t in continent.nodes):
                    continent_bonus += self.continent_bonuses[continent_name]
        
        return base_reinforce + continent_bonus
    
    def reinforce(self, territory, num_armies, player):
        """Adds reinforcements to a player's owned territory."""
        if self.game_map.Risk_Map.nodes[territory]["owner"] == player:
            self.game_map.Risk_Map.nodes[territory]["armies"] += num_armies
            print(f"{num_armies} armies added to {territory}.")
        else:
            print("You don't own this territory!")

    def attack(self, attacker, defender, player, num_attack_dice=1, num_defend_dice=1):
        """Performs an attack between two territories with variable dice."""
        if not self.validate_attack(attacker, defender, player):
            print("Invalid attack!")
            return False

        attack_rolls = sorted([random.randint(1,6) for _ in range(num_attack_dice)], reverse=True)
        defense_rolls = sorted([random.randint(1,6) for _ in range(num_defend_dice)], reverse=True)
        
        # Compare dice pairwise
        for a, d in zip(attack_rolls, defense_rolls):
            if a > d:
                self.game_map.Risk_Map.nodes[defender]["armies"] -= 1
            else:
                self.game_map.Risk_Map.nodes[attacker]["armies"] -= 1

        # Check for territory capture
        if self.game_map.Risk_Map.nodes[defender]["armies"] <= 0:
            self.capture_territory(attacker, defender, player, num_attack_dice)
            return True
        return False
    
    def validate_attack(self, attacker, defender, player):
        """Check if attack is valid."""
        return (self.game_map.Risk_Map.nodes[attacker]["owner"] == player and
                self.game_map.Risk_Map.nodes[defender]["owner"] != player and
                self.game_map.Risk_Map.nodes[attacker]["armies"] > 1 and
                defender in self.game_map.Risk_Map.neighbors(attacker))

    def capture_territory(self, attacker, defender, player, armies_to_move):
        """Handle territory capture."""
        self.game_map.Risk_Map.nodes[defender]["owner"] = player
        armies_to_move = min(armies_to_move, self.game_map.Risk_Map.nodes[attacker]["armies"]-1)
        self.game_map.Risk_Map.nodes[attacker]["armies"] -= armies_to_move
        self.game_map.Risk_Map.nodes[defender]["armies"] = armies_to_move
        print(f"{defender} captured! {armies_to_move} armies moved in.")

    def fortify(self, from_territory, to_territory, num_armies, player):
        """Moves armies between two territories owned by the same player."""
        if (self.game_map.Risk_Map.nodes[from_territory]["owner"] == player and 
            self.game_map.Risk_Map.nodes[to_territory]["owner"] == player and 
            num_armies < self.game_map.Risk_Map.nodes[from_territory]["armies"]):

            self.game_map.Risk_Map.nodes[from_territory]["armies"] -= num_armies
            self.game_map.Risk_Map.nodes[to_territory]["armies"] += num_armies
            # print(f"Moved {num_armies} armies from {from_territory} to {to_territory}.")
        else:
            print("Invalid fortification! Make sure you own both territories and have enough armies.")


