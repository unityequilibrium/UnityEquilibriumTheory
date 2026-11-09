import random


class MycelialNetwork:
    def __init__(self, transfer_efficiency=0.9):
        self.nodes = []  # List of entities (Trees, WasteStations)
        self.transfer_efficiency = transfer_efficiency  # 90% efficiency (Engineered Fungi)

    def add_node(self, entity):
        self.nodes.append(entity)

    def distribute_nutrients(self):
        """
        The Logic:
        1. Collect Surplus from Sources (Waste Stations, Mother Trees).
        2. Distribute to Sinks (Young Trees).
        """
        total_pool = 0.0

        # Step 1: Collection Phase
        for node in self.nodes:
            if node.type == "WASTE_STATION":
                # Waste stations produce massive nutrients from trash
                generated = node.process_waste()
                total_pool += generated
                # print(f"  [+] Waste Station generated {generated:.1f} units")

            elif node.type == "TREE" and node.age > 20:
                # Mother Trees donate 10% of their energy
                donation = node.biomass * 0.1
                node.biomass -= donation  # Cost to donor
                total_pool += donation
                # print(f"  [+] Mother Tree donated {donation:.1f} units")

        # Step 2: Distribution Phase (The Socialist Network)
        # Apply Efficiency Loss
        net_pool = total_pool * self.transfer_efficiency

        # Identify Needy Nodes (Young Trees)
        needy_nodes = [n for n in self.nodes if n.type == "TREE" and n.age < 10]

        if not needy_nodes:
            return  # No one needs food

        share_per_node = net_pool / len(needy_nodes)

        for node in needy_nodes:
            # Boost Growth!
            node.receive_nutrients(share_per_node)
            # print(f"  [->] Young Tree received {share_per_node:.1f} units (Boost!)")


class BioEntity:
    def __init__(self, entity_type, age=0):
        self.type = entity_type
        self.age = age
        self.biomass = 1.0 if entity_type == "TREE" else 0
        self.waste_input = 0

    def process_waste(self):
        # Only for Waste Stations
        nutrients = self.waste_input * 0.8  # Convert 80% of waste to food
        self.waste_input = 0  # Consumed
        return nutrients

    def receive_nutrients(self, amount):
        # Convert Nutrients to Biomass (Growth Spurt)
        # Efficiency: 1 Unit Nutrient = 0.5 Unit Biomass (Biological Conversion)
        self.biomass += amount * 0.5

    def grow_natural(self, genetic_factor=1.0):
        if self.type == "TREE":
            self.age += 1
            # Normal Logistic Growth + Genetic Factor
            rate = 1.2 * genetic_factor
            self.biomass *= rate
