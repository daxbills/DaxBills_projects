import random

class RandomAI:
    def __init__(self, game_map, game_actions, player_id):
        self.game_map = game_map
        self.game_actions = game_actions
        self.player_id = player_id

    def reinforce_phase(self):
        territories = self.get_owned_territories()
        if not territories:
            return

        # Get total reinforcements including continent bonuses
        total_reinforce = self.game_actions.calculate_reinforcements(self.player_id)
        
        # Distribute randomly
        for _ in range(total_reinforce):
            territory = random.choice(territories)
            self.game_actions.reinforce(territory, 1, self.player_id)

    def attack_phase(self):
        """Handle attack phase with multiple possible attacks"""
        attack_count = random.randint(1, 1000)  # Random number of attacks
        for _ in range(attack_count):
            if not self.single_attack():
                break  # Stop if no valid attacks left

    def single_attack(self):
        """Perform one attack, returns True if attack was made"""
        attacker = self.choose_attacker()
        if not attacker:
            return False

        defender = self.choose_defender(attacker)
        if not defender:
            return False

        attacker_armies = self.game_map.Risk_Map.nodes[attacker]["armies"]
        defender_armies = self.game_map.Risk_Map.nodes[defender]["armies"]

        attack_dice = min(3, attacker_armies - 1)
        defense_dice = min(2, defender_armies)

        # print(f"Player {self.player_id} attacking {defender} from {attacker}")
        return self.game_actions.attack(
            attacker=attacker,
            defender=defender,
            player=self.player_id,
            num_attack_dice=attack_dice,
            num_defend_dice=defense_dice
        )

    def fortify_phase(self):
        """Handle fortification phase"""
        territories = self.get_owned_territories()
        if len(territories) < 2:
            return

        from_territory = random.choice(territories)
        if self.game_map.Risk_Map.nodes[from_territory]["armies"] < 2:
            return

        neighbors = list(self.game_map.Risk_Map.neighbors(from_territory))
        possible_moves = [n for n in neighbors if self.game_map.Risk_Map.nodes[n]["owner"] == self.player_id]
        
        if possible_moves:
            to_territory = random.choice(possible_moves)
            num_armies = random.randint(1, self.game_map.Risk_Map.nodes[from_territory]["armies"] - 1)
            self.game_actions.fortify(from_territory, to_territory, num_armies, self.player_id)

    def get_owned_territories(self):
        """Helper to get all territories owned by this player"""
        return [t for t in self.game_map.Risk_Map.nodes if self.game_map.Risk_Map.nodes[t]["owner"] == self.player_id]

    def choose_attacker(self):
        """Select a valid attacking territory"""
        attackable = [t for t in self.get_owned_territories() if self.game_map.Risk_Map.nodes[t]["armies"] > 1]
        return random.choice(attackable) if attackable else None

    def choose_defender(self, attacker):
        """Select a valid defender for the given attacker"""
        neighbors = list(self.game_map.Risk_Map.neighbors(attacker))
        enemies = [t for t in neighbors if self.game_map.Risk_Map.nodes[t]["owner"] != self.player_id]
        return random.choice(enemies) if enemies else None