from src.constants import *

class Item:
    def __init__(self, item_type, quantity=1, durability=None):
        self.item_type = item_type
        self.quantity = quantity
        self.durability = durability
        self.max_durability = self.get_max_durability()
    
    def get_max_durability(self):
        durability_map = {
            ITEM_WOOD_PICKAXE: 50,
            ITEM_STONE_PICKAXE: 100,
            ITEM_IRON_PICKAXE: 200,
            ITEM_DIAMOND_PICKAXE: 500,
            ITEM_WOOD_SWORD: 50,
            ITEM_STONE_SWORD: 100,
            ITEM_IRON_SWORD: 200,
            ITEM_DIAMOND_SWORD: 500,
        }
        return durability_map.get(self.item_type, None)

class Inventory:
    def __init__(self, size=36):
        self.size = size
        self.items = {}
        self.hotbar_size = 9
    
    def add_item(self, item_type, quantity):
        if item_type in self.items:
            self.items[item_type].quantity += quantity
        else:
            self.items[item_type] = Item(item_type, quantity)
        return True
    
    def remove_item(self, item_type, quantity):
        if item_type in self.items:
            if self.items[item_type].quantity >= quantity:
                self.items[item_type].quantity -= quantity
                if self.items[item_type].quantity <= 0:
                    del self.items[item_type]
                return True
        return False
    
    def get_item(self, item_type):
        return self.items.get(item_type)
    
    def get_selected_item(self, slot):
        # Get item from hotbar slot
        items_list = list(self.items.values())
        if slot < len(items_list):
            return items_list[slot]
        return None
    
    def get_item_name(self, item_type):
        names = {
            BLOCK_GRASS: "Grass Block",
            BLOCK_DIRT: "Dirt",
            BLOCK_STONE: "Stone",
            BLOCK_WOOD: "Wood",
            BLOCK_LEAVES: "Leaves",
            BLOCK_SAND: "Sand",
            BLOCK_COAL_ORE: "Coal Ore",
            BLOCK_IRON_ORE: "Iron Ore",
            BLOCK_GOLD_ORE: "Gold Ore",
            BLOCK_DIAMOND_ORE: "Diamond Ore",
            BLOCK_CACTUS: "Cactus",
            ITEM_WOOD_PICKAXE: "Wood Pickaxe",
            ITEM_STONE_PICKAXE: "Stone Pickaxe",
            ITEM_IRON_PICKAXE: "Iron Pickaxe",
            ITEM_DIAMOND_PICKAXE: "Diamond Pickaxe",
            ITEM_WOOD_SWORD: "Wood Sword",
            ITEM_STONE_SWORD: "Stone Sword",
            ITEM_IRON_SWORD: "Iron Sword",
            ITEM_DIAMOND_SWORD: "Diamond Sword",
            ITEM_BREAD: "Bread",
            ITEM_APPLE: "Apple",
            ITEM_COAL: "Coal",
            ITEM_IRON_INGOT: "Iron Ingot",
            ITEM_GOLD_INGOT: "Gold Ingot",
            ITEM_DIAMOND: "Diamond",
        }
        return names.get(item_type, f"Item {item_type}")