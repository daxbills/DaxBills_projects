class RuleBasedAI:
    def __init__(self, game_map, game_actions, player_id):
        self.game_map = game_map
        self.game_actions = game_actions
        self.player_id = player_id
        self.continent_values = {
            "North America": 5,
            "South America": 2,
            "Europe": 5,
            "Africa": 3,
            "Asia": 7,
            "Australia": 2
        }

    def get_owned_territories(self):
        return [t for t in self.game_map.Risk_Map.nodes 
                if self.game_map.Risk_Map.nodes[t]["owner"] == self.player_id]

    def reinforce_phase(self):
        territories = self.get_owned_territories()
        if not territories:
            return

        # Calculate total reinforcements including continent bonuses
        total_reinforce = self.game_actions.calculate_reinforcements(self.player_id)
        
        # Get border territories (adjacent to enemies)
        border_territories = []
        for territory in territories:
            neighbors = list(self.game_map.Risk_Map.neighbors(territory))
            if any(self.game_map.Risk_Map.nodes[n]["owner"] != self.player_id for n in neighbors):
                border_territories.append(territory)

        if not border_territories:
            border_territories = territories

        # Distribute all reinforcements strategically
        while total_reinforce > 0:
            # Find territory that needs reinforcement most
            target = min(border_territories,
                        key=lambda t: (
                            self.game_map.Risk_Map.nodes[t]["armies"],
                            -self._get_territory_threat(t)
                        ))
            
            # Add between 1-3 armies at a time
            add = min(3, total_reinforce)
            self.game_actions.reinforce(target, add, self.player_id)
            total_reinforce -= add

    def _get_territory_threat(self, territory):
        """Calculate threat level from neighboring enemies"""
        threat = 0
        for neighbor in self.game_map.Risk_Map.neighbors(territory):
            if self.game_map.Risk_Map.nodes[neighbor]["owner"] != self.player_id:
                threat += self.game_map.Risk_Map.nodes[neighbor]["armies"]
        return threat

    def attack_phase(self):
        """Aggressive attack strategy when AI has enough resources."""
        total_armies = sum(self.game_map.Risk_Map.nodes[t]["armies"] 
                        for t in self.get_owned_territories())
        strongest_enemy = max(
            (sum(self.game_map.Risk_Map.nodes[t]["armies"] 
                for t in self.game_map.Risk_Map.nodes if self.game_map.Risk_Map.nodes[t]["owner"] == pid), pid)
            for pid in set(self.game_map.Risk_Map.nodes[t]["owner"] 
                        for t in self.game_map.Risk_Map.nodes if self.game_map.Risk_Map.nodes[t]["owner"] != self.player_id)
        )[0] if any(self.game_map.Risk_Map.nodes[t]["owner"] != self.player_id for t in self.game_map.Risk_Map.nodes) else 0

        # Enable aggressive attack mode if AI has double the armies of any opponent
        aggressive_mode = total_armies > 2 * strongest_enemy

        attackable_territories = [t for t in self.get_owned_territories()
                                if self.game_map.Risk_Map.nodes[t]["armies"] > 1]

        while attackable_territories:
            new_attackable_territories = []  # Track newly conquered territories

            for territory in attackable_territories:
                possible_targets = [
                    n for n in self.game_map.Risk_Map.neighbors(territory)
                    if (self.game_map.Risk_Map.nodes[n]["owner"] != self.player_id and
                        self.game_map.Risk_Map.nodes[territory]["armies"] > self.game_map.Risk_Map.nodes[n]["armies"])
                ]

                for target in possible_targets:
                    # Keep attacking **only if we have more armies than the target**
                    while (self.game_map.Risk_Map.nodes[target]["owner"] != self.player_id and
                        self.game_map.Risk_Map.nodes[territory]["armies"] > 1):
                        if self._execute_coordinated_attack(target, [territory], aggressive_mode):
                            new_attackable_territories.append(target)

            # Update attackable territories
            attackable_territories = new_attackable_territories

            # After all possible attacks, **check if we still have a major troop advantage**
            remaining_enemies = [t for t in self.game_map.Risk_Map.nodes
                                if self.game_map.Risk_Map.nodes[t]["owner"] != self.player_id]

            if remaining_enemies:
                strongest_enemy = max(self.game_map.Risk_Map.nodes[t]["armies"] for t in remaining_enemies)
                total_armies = sum(self.game_map.Risk_Map.nodes[t]["armies"] for t in self.get_owned_territories())

                # **Stop attacking if we don't have a clear advantage (1.5x more troops than strongest enemy)**
                if total_armies <= 1.5 * strongest_enemy:
                    break

    def _select_best_target(self):
        """Identify the best target for coordinated attack"""
        enemy_territories = [
            t for t in self.game_map.Risk_Map.nodes
            if self.game_map.Risk_Map.nodes[t]["owner"] != self.player_id
        ]
        
        if not enemy_territories:
            return None
        
        # Score each potential target
        target_scores = []
        for territory in enemy_territories:
            score = self._calculate_target_value(territory)
            attackers = self._get_potential_attackers(territory)
            if attackers:
                target_scores.append((score, territory, attackers))
        
        if not target_scores:
            return None
            
        # Select highest value target
        return max(target_scores, key=lambda x: x[0])[1:]

    def _calculate_target_value(self, territory):
        """Calculate strategic value of a target territory"""
        value = 0
        
        # Continent completion value
        continent = self._get_continent(territory)
        completion = self._get_continent_completion(continent)
        if completion > 0.6:
            value += 50 * completion
            
        # Strategic position value
        neighbor_count = len(list(self.game_map.Risk_Map.neighbors(territory)))
        value += neighbor_count * 1.2
        
        # Army strength (prefer weaker targets)
        value -= self.game_map.Risk_Map.nodes[territory]["armies"] * 0.4
        
        return value

    def _get_continent(self, territory):
        """Find which continent a territory belongs to"""
        for continent in self.game_map.continents:
            if territory in continent.nodes:
                return continent.graph.get('name', 'Unknown')
        return 'Unknown'

    def _get_continent_completion(self, continent_name):
        """Return ratio of continent owned (0-1)"""
        total = 0
        owned = 0
        for continent in self.game_map.continents:
            if continent.graph.get('name') == continent_name:
                for territory in continent.nodes:
                    total += 1
                    if self.game_map.Risk_Map.nodes[territory]["owner"] == self.player_id:
                        owned += 1
                return owned / total if total > 0 else 0
        return 0

    def _get_potential_attackers(self, target):
        """Find all adjacent territories that can attack the target"""
        attackers = []
        for neighbor in self.game_map.Risk_Map.neighbors(target):
            if (self.game_map.Risk_Map.nodes[neighbor]["owner"] == self.player_id and
                self.game_map.Risk_Map.nodes[neighbor]["armies"] > 1):
                attackers.append(neighbor)
        return attackers

    def _execute_coordinated_attack(self, target, attackers, aggressive_mode):
        """Execute an attack with adjusted aggression levels."""
        if not target or not attackers:
            return False

        valid_attackers = [a for a in attackers if self.game_map.Risk_Map.nodes[a]["armies"] > 1]

        if not valid_attackers:
            return False

        success = False
        remaining_defenders = self.game_map.Risk_Map.nodes[target]["armies"]

        for attacker in sorted(valid_attackers, key=lambda a: self.game_map.Risk_Map.nodes[a]["armies"], reverse=True):
            if remaining_defenders <= 0:
                break

            attack_dice = min(3, self.game_map.Risk_Map.nodes[attacker]["armies"] - 1)
            defend_dice = min(2, remaining_defenders)

            result = self.game_actions.attack(
                attacker=attacker,
                defender=target,
                player=self.player_id,
                num_attack_dice=attack_dice,
                num_defend_dice=defend_dice
            )

            if result:
                success = True
                remaining_defenders = self.game_map.Risk_Map.nodes[target]["armies"]

                # Aggressive mode means continuing attacks if we have overwhelming force
                if aggressive_mode and self.game_map.Risk_Map.nodes[attacker]["armies"] > remaining_defenders + 5:
                    continue
                else:
                    break

        return success

    def fortify_phase(self):
        territories = self.get_owned_territories()
        if len(territories) < 2:
            return
            
        # Find interior territories (not bordering enemies)
        interior = []
        border = []
        for territory in territories:
            neighbors = list(self.game_map.Risk_Map.neighbors(territory))
            if any(self.game_map.Risk_Map.nodes[n]["owner"] != self.player_id for n in neighbors):
                border.append(territory)
            else:
                interior.append(territory)
                
        if not interior or not border:
            return
            
        # Find interior territory with most armies
        from_territory = max(interior, 
                           key=lambda t: self.game_map.Risk_Map.nodes[t]["armies"])
        if self.game_map.Risk_Map.nodes[from_territory]["armies"] < 2:
            return
            
        # Find weakest border territory adjacent to interior
        neighbors = list(self.game_map.Risk_Map.neighbors(from_territory))
        possible_destinations = [t for t in neighbors 
                               if t in border and 
                               self.game_map.Risk_Map.nodes[t]["owner"] == self.player_id]
                               
        if not possible_destinations:
            return
            
        to_territory = min(possible_destinations,
                          key=lambda t: self.game_map.Risk_Map.nodes[t]["armies"])
                          
        # Move all but one army
        armies = self.game_map.Risk_Map.nodes[from_territory]["armies"] - 1
        self.game_actions.fortify(from_territory, to_territory, armies, self.player_id)