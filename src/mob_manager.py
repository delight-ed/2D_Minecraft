import random
import math
from src.mob import Mob
from src.constants import *

class MobManager:
    def __init__(self):
        self.mobs = []
        self.spawn_timer = 0
        self.max_mobs = 50
    
    def spawn_mob(self, mob_type, x, y):
        if len(self.mobs) < self.max_mobs:
            mob = Mob(mob_type, x, y)
            self.mobs.append(mob)
    
    def update(self, dt, world, player):
        self.spawn_timer += dt
        
        # Update all mobs
        for mob in self.mobs[:]:  # Create a copy to iterate over
            mob.update(dt, world, player)
            
            # Remove dead mobs
            if mob.is_dead():
                self.drop_loot(mob, player)
                self.mobs.remove(mob)
        
        # Spawn new mobs occasionally
        if self.spawn_timer > 10 and len(self.mobs) < self.max_mobs // 2:
            self.spawn_random_mob(player, world)
            self.spawn_timer = 0
    
    def drop_loot(self, mob, player):
        # Drop items when mob dies
        loot_table = {
            MOB_ZOMBIE: [(ITEM_BREAD, 0.3), (ITEM_IRON_INGOT, 0.1)],
            MOB_SKELETON: [(ITEM_COAL, 0.5), (ITEM_IRON_INGOT, 0.2)],
            MOB_CREEPER: [(ITEM_COAL, 0.8)],
            MOB_SPIDER: [(ITEM_BREAD, 0.2)],
            MOB_ENDERMAN: [(ITEM_DIAMOND, 0.3), (ITEM_GOLD_INGOT, 0.5)],
            MOB_DRAGON: [(ITEM_DIAMOND, 1.0), (ITEM_GOLD_INGOT, 1.0), (ITEM_DIAMOND_SWORD, 0.5)]
        }
        
        if mob.type in loot_table:
            for item_type, chance in loot_table[mob.type]:
                if random.random() < chance:
                    player.inventory.add_item(item_type, 1)
    
    def spawn_random_mob(self, player, world):
        # Spawn mob near player but not too close
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(300, 500)
        
        spawn_x = player.x + distance * math.cos(angle)
        spawn_y = world.get_surface_height(int(spawn_x // BLOCK_SIZE)) * BLOCK_SIZE + 50
        
        # Choose mob type based on conditions
        mob_types = [MOB_ZOMBIE, MOB_SKELETON, MOB_SPIDER]
        if random.random() < 0.1:  # 10% chance for special mobs
            mob_types.extend([MOB_CREEPER, MOB_ENDERMAN])
        
        mob_type = random.choice(mob_types)
        self.spawn_mob(mob_type, spawn_x, spawn_y)
    
    def render(self, screen, camera):
        for mob in self.mobs:
            mob.render(screen, camera)