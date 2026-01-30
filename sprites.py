import pygame
import random
from structures.linked_list import LinkedList

class Entity:
    """
    Base class for all moving characters in the game.
    """
    def __init__(self, x, y, image_path):
        self.x = x  # Grid X
        self.y = y  # Grid Y
        self.tile_size = 40 # Should match map TILE_SIZE
        # Load and scale image
        try:
            self.original_image = pygame.transform.scale(pygame.image.load(image_path), (self.tile_size, self.tile_size))
            self.image = self.original_image
        except:
            print(f"Error loading {image_path}, using placeholder.")
            self.image = None
            self.original_image = None
            self.color = (255, 0, 255) # Magenta placeholder

    def draw(self, screen, offset_x=0, offset_y=0):
        """Draws the entity."""
        rect = pygame.Rect(self.x * self.tile_size + offset_x, self.tile_size * self.y + offset_y, self.tile_size, self.tile_size)
        if self.image:
            screen.blit(self.image, rect)
        else:
            pygame.draw.rect(screen, self.color, rect.inflate(-4, -4))

class Player(Entity):
    """
    The player character controlled by the user.
    """
    def __init__(self, x, y):
        super().__init__(x, y, "assets/images/player.png") # Load car image
        self.history = LinkedList() # History for undo feature
        self.angle = 0 
        self.is_safe = False # Mechanic: If paid, immune to warden until move
        self.start_x = x
        self.start_y = y

    def reset(self):
        """Resets the player to initial state."""
        self.x = self.start_x
        self.y = self.start_y
        self.history = LinkedList()
        self.angle = 0
        self.is_safe = False


    def move(self, dx, dy, game_map):
        """
        Attempts to move the player by dx, dy.
        Checks for collisions using the game_map.
        Also rotates the sprite.
        """
        # Reset safety on any move attempt
        self.is_safe = False
        
        # Rotation Logic
        if dx == 1: self.rotate(90)   # Right
        elif dx == -1: self.rotate(-90) # Left
        elif dy == -1: self.rotate(180) # Up
        elif dy == 1: self.rotate(0)    # Down

        new_x = self.x + dx
        new_y = self.y + dy

        if game_map.is_road(new_x, new_y):
            # Record previous position before moving
            self.history.append((self.x, self.y))
            
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def rotate(self, angle):
        """Rotates the image to the specified angle."""
        self.angle = angle
        if self.original_image:
            self.image = pygame.transform.rotate(self.original_image, self.angle)

    def undo(self):
        """
        Reverts to the previous position using the Linked List history.
        """
        prev_pos = self.history.pop()
        if prev_pos:
            self.x, self.y = prev_pos
            print(f"Undo: Moved back to {prev_pos}")
            # Note: We don't track rotation history yet, so it stays facing the last direction.
            # This is acceptable for now.

class Warden(Entity):
    """
    The AI Traffic Warden.
    
    Movement is handled via pathfinding to the player's position.
    """
    def __init__(self, x, y):
        super().__init__(x, y, "assets/images/warden.png") # Load warden image
        self.path = [] # Current path to follow (List of coordinates)
        self.start_x = x
        self.start_y = y

    def reset(self):
        """Resets the warden to initial state."""
        self.x = self.start_x
        self.y = self.start_y
        self.path = []


    def update(self, game_map, target_pos):
        """
        Calculates path to target_pos and takes one step.
        """
        start_node = (self.x, self.y)
        end_node = target_pos
        
        # Recalculate path
        path = game_map.graph.pathfind(start_node, end_node)
        
        # DEBUG: Print path status
        # print(f"Warden at {start_node} hunting {end_node}. Path found: {path}")

        # If we have a path and it has more than 1 node (first node is current pos)
        if path and len(path) > 1:
            next_node = path[1] # Next step
            self.x = next_node[0]
            self.y = next_node[1]
        elif start_node == end_node:
            # Already at target, stay put.
            pass 
        else:
            # Fallback: Move to a random connected road tile if stuck
            # This prevents stuck loops and silences the spam
            neighbors = game_map.graph.get_neighbors((self.x, self.y))
            if neighbors:
                 nx, ny = random.choice(neighbors)
                 self.x, self.y = nx, ny

    def update_rage(self, game_map):
        """
        Special movement for RAGE state.
        1. If not on edge, pathfind to nearest edge.
        2. If on edge, move clockwise around the perimeter.
        """
        w = game_map.width
        h = game_map.height
        
        # Check if on edge
        on_edge = (self.x == 0 or self.x == w - 1 or self.y == 0 or self.y == h - 1)
        
        if on_edge:
            # Move Clockwise
            # Top Edge (y=0, x < w-1) -> Right
            if self.y == 0 and self.x < w - 1:
                self.x += 1
            # Right Edge (x=w-1, y < h-1) -> Down
            elif self.x == w - 1 and self.y < h - 1:
                self.y += 1
            # Bottom Edge (y=h-1, x > 0) -> Left
            elif self.y == h - 1 and self.x > 0:
                self.x -= 1
            # Left Edge (x=0, y > 0) -> Up
            elif self.x == 0 and self.y > 0:
                self.y -= 1
        else:
            # Pathfind to nearest edge
            # Find closest edge node
            # Edges are at x=0, x=w-1, y=0, y=h-1
            # We can just pick the closest point geometrically and pathfind there
            
            target = None
            min_dist = float('inf')
            
            # Candidates: (0, y), (w-1, y), (x, 0), (x, h-1)
            candidates = [
                (0, self.y), (w-1, self.y),
                (self.x, 0), (self.x, h-1)
            ]
            
            for cx, cy in candidates:
                # Ensure candidate is valid (it should be a road per map gen)
                if game_map.is_road(cx, cy):
                    dist = abs(self.x - cx) + abs(self.y - cy)
                    if dist < min_dist:
                        min_dist = dist
                        target = (cx, cy)
            
            if target:
                path = game_map.graph.pathfind((self.x, self.y), target)
                if path and len(path) > 1:
                    self.x, self.y = path[1]
                else:
                    # If path fails (shouldn't), just try to step towards target manually
                    dx = target[0] - self.x
                    dy = target[1] - self.y
                    if dx != 0: self.x += 1 if dx > 0 else -1
                    elif dy != 0: self.y += 1 if dy > 0 else -1

