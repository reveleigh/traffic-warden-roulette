import random
import pygame
from structures.graph import Graph

# Tile Types
TILE_EMPTY = 0
TILE_ROAD = 1
TILE_BUILDING = 2
TILE_SHOP = 3
TILE_PARK = 4

# Specific Shop Types
TILE_SHOP_BAKERY = 10
TILE_SHOP_CLOTHING = 11
TILE_SHOP_TECH = 12
TILE_SHOP_CAFE = 13

TILE_SHOP_CAFE = 13

# New Constants for Landmarks
TILE_POOL = 24
TILE_MUSEUM = 25
TILE_SUPERMARKET = 26
TILE_CHURCH = 27
TILE_SCHOOL = 28

# Large Structures (2x2)
TILE_OFFICE_LARGE = 20
TILE_HOSPITAL = 21
TILE_PARK_LARGE = 22
TILE_AMPITHEATRE = 23
TILE_OCCUPIED = 99 # Invisible tile for the other 3 parts of a 2x2

ALL_SHOPS = [TILE_SHOP, TILE_SHOP_BAKERY, TILE_SHOP_CLOTHING, TILE_SHOP_TECH, TILE_SHOP_CAFE]
ALL_BUILDINGS = [TILE_BUILDING, TILE_OFFICE_LARGE, TILE_HOSPITAL, TILE_PARK_LARGE, TILE_AMPITHEATRE, TILE_OCCUPIED, 
                 TILE_POOL, TILE_MUSEUM, TILE_SUPERMARKET, TILE_CHURCH, TILE_SCHOOL]

# Map Settings
MAP_WIDTH = 20  # Tiles
MAP_HEIGHT = 15 # Tiles
TILE_SIZE = 40  # Pixels

# Fixed Landmark Definitions
LANDMARKS = [
    # Name, X, Y, W, H, Tile Type, Image Path, Specific Tasks
    {
        "name": "Roman Amphitheatre", 
        "x": 15, "y": 3, "w": 3, "h": 3, 
        "tile": TILE_AMPITHEATRE, 
        "image": "assets/images/ampitheatre.png", 
        "size": (120, 120),
        "tasks": ["Meet Tour Group", "Photo Opportunity", "Historical Walk", "School Trip Help"]
    },
    {
        "name": "Open Air Pool", 
        "x": 3, "y": 11, "w": 2, "h": 2, 
        "tile": TILE_POOL, 
        "image": "assets/images/swimming_pool.png", 
        "size": (80, 80),
        "tasks": ["Swimming Lesson (Fenella)", "Morning Laps (Rupert)", "Lifeguard Chat", "Collect Swimming Kit"]
    },
    {
        "name": "Corinium Museum", 
        "x": 7, "y": 7, "w": 2, "h": 2, 
        "tile": TILE_MUSEUM, 
        "image": "assets/images/museum.png", 
        "size": (80, 80),
        "tasks": ["View Roman Mosaic", "Donate Old Coin", "Meet Curator", "Kids Workshop"]
    },
    {
        "name": "Tesco Extra", 
        "x": 3, "y": 3, "w": 2, "h": 2, 
        "tile": TILE_SUPERMARKET, 
        "image": "assets/images/supermarket.png", 
        "size": (80, 80),
        "tasks": ["Weekly Big Shop", "Buy Clementine's Wine", "Emergency Nappy Run", "Return Trolley"]
    },
    {
        "name": "Cirencester Church", 
        "x": 11, "y": 7, "w": 2, "h": 2, 
        "tile": TILE_CHURCH, 
        "image": "assets/images/church.png", 
        "size": (80, 80),
        "tasks": ["Bell Ringing Practice", "Flower Arranging", "Meet Vicar", "Choir Practice"]
    },
    {
        "name": "Deer Park School", 
        "x": 15, "y": 11, "w": 2, "h": 2, 
        "tile": TILE_SCHOOL, 
        "image": "assets/images/school.png", 
        "size": (80, 80),
        "tasks": ["Pick up Ivor", "Drop off Fenella", "Parents Evening", "Sports Day Event", "School Play"]
    },
    {
        "name": "St Micheals Hoard Mgt", 
        "x": 7, "y": 3, "w": 2, "h": 2, 
        "tile": TILE_OFFICE_LARGE, 
        "image": "assets/images/building_large_office.png", 
        "size": (80, 80),
        "tasks": ["Count Gold Bars", "Lease Sign-off", "Hide Assets", "Investment Meeting", "Hoard Check"]
    },
    {
        "name": "Minor Injuries Unit", 
        "x": 11, "y": 3, "w": 2, "h": 2, 
        "tile": TILE_HOSPITAL, 
        "image": "assets/images/hospital.png", 
        "size": (80, 80),
        "tasks": ["Rugby Injury (Ivor)", "X-Ray Appointment", "Stitched Finger", "Tetanus Shot", "Visit Granny"]
    },
]

class Map:
    """
    Handles map generation and tile management.
    """
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.tile_size = TILE_SIZE
        self.grid = []  # The 2D Array
        self.graph = Graph() # The navigation graph
        
        # Load Images
        self.images = {
            TILE_ROAD: self.load_image("assets/images/road.png", (50, 50, 50)),
            TILE_BUILDING: self.load_image("assets/images/building.png", (100, 100, 100)),
            TILE_SHOP: self.load_image("assets/images/shop.png", (0, 0, 200)),
            TILE_PARK: self.load_image("assets/images/park.png", (34, 139, 34)),
            TILE_SHOP_BAKERY: self.load_image("assets/images/shop_bakery.png", (200, 100, 50)),
            TILE_SHOP_CLOTHING: self.load_image("assets/images/shop_clothing.png", (100, 50, 100)),
            TILE_SHOP_TECH: self.load_image("assets/images/shop_tech.png", (50, 50, 50)),
            TILE_SHOP_CAFE: self.load_image("assets/images/shop_cafe.png", (150, 75, 0)),
            TILE_OFFICE_LARGE: self.load_image("assets/images/building_large_office.png", (100, 100, 100), size=(80, 80)),
            TILE_HOSPITAL: self.load_image("assets/images/hospital.png", (200, 0, 0), size=(80, 80)),
            TILE_PARK_LARGE: self.load_image("assets/images/park_large.png", (34, 139, 34), size=(80, 80)),
            # Landmarks
            TILE_AMPITHEATRE: self.load_image("assets/images/ampitheatre.png", (100, 100, 0), size=(120, 120)),
            TILE_POOL: self.load_image("assets/images/swimming_pool.png", (0, 150, 255), size=(80, 80)),
            TILE_MUSEUM: self.load_image("assets/images/museum.png", (150, 150, 150), size=(80, 80)),
            TILE_SUPERMARKET: self.load_image("assets/images/supermarket.png", (0, 0, 255), size=(80, 80)),
            TILE_CHURCH: self.load_image("assets/images/church.png", (100, 100, 100), size=(80, 80)),
            TILE_SCHOOL: self.load_image("assets/images/school.png", (200, 100, 100), size=(80, 80)),
        }
        
        self.generate_map()
    
    def load_image(self, path, fallback_color, size=None):
        """Helper to safely load an image or return a coloured placeholder."""
        if size is None: size = (self.tile_size, self.tile_size)
        try:
            img = pygame.image.load(path)
            # Ensure image supports transparency (alpha)
            img = img.convert_alpha()
            return pygame.transform.scale(img, size)
        except (FileNotFoundError, pygame.error) as e:
            import os
            abs_path = os.path.abspath(path)
            print(f"Warning: Could not load {path} (Abs: {abs_path}). Error: {e}")
            surf = pygame.Surface(size)
            surf.fill(fallback_color)
            return surf

    def generate_map(self):
        """
        Generates the town layout with roads and landmarks.
        """
        # 1. Initialise empty grid (2D Array)
        self.grid = [[TILE_EMPTY for _ in range(self.width)] for _ in range(self.height)]

        # 2. Generate Roads (Simple Grid Pattern)
        # Border
        for x in range(self.width):
            self.grid[0][x] = TILE_ROAD
            self.grid[self.height - 1][x] = TILE_ROAD
        for y in range(self.height):
            self.grid[y][0] = TILE_ROAD
            self.grid[y][self.width - 1] = TILE_ROAD

        # Internal Roads
        for x in range(2, self.width - 2, 4):
            for y in range(self.height):
                self.grid[y][x] = TILE_ROAD
        
        for y in range(2, self.height - 2, 4):
            for x in range(self.width):
                self.grid[y][x] = TILE_ROAD

        # 3. Place Fixed Landmarks
        for lm in LANDMARKS:
            x, y, w, h = lm['x'], lm['y'], lm['w'], lm['h']
            tile_type = lm['tile']
            
            # Place main tile
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = tile_type
                
                # Mark occupied tiles
                for r in range(y, y+h):
                    for c in range(x, x+w):
                        if 0 <= r < self.height and 0 <= c < self.width:
                            if r == y and c == x: continue # Don't overwrite main tile
                            # Check if overwriting road (should be fine if designed well, but warn?)
                            # self.grid[r][c] = TILE_OCCUPIED
                            # FORCE override roads for landmarks
                            self.grid[r][c] = TILE_OCCUPIED

        # 4. Fill Empty Spots
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == TILE_EMPTY:
                    dice = random.random()
                    if dice < 0.6:
                        self.grid[y][x] = TILE_BUILDING
                    elif dice < 0.8:
                        self.grid[y][x] = random.choice([TILE_SHOP_BAKERY, TILE_SHOP_CLOTHING, TILE_SHOP_TECH, TILE_SHOP_CAFE])
                    else:
                        self.grid[y][x] = TILE_PARK

        # 5. Build Navigation Graph
        self.build_graph()

    def build_graph(self):
        """
        Converts the tile grid into a logical graph for navigation.
        """
        self.graph = Graph() # Reset graph
        
        # Add nodes
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == TILE_ROAD:
                    self.graph.add_node((x, y))
        
        # Add edges
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == TILE_ROAD:
                    # Check neighbours (Right and Down is enough for undirected)
                    # Check Right
                    if x + 1 < self.width and self.grid[y][x+1] == TILE_ROAD:
                        self.graph.add_edge((x, y), (x+1, y))
                    # Check Down
                    if y + 1 < self.height and self.grid[y+1][x] == TILE_ROAD:
                        self.graph.add_edge((x, y), (x, y+1))

    def draw(self, screen, offset_x=0, offset_y=0):
        """
        Visualises the map on the given Pygame screen surface.
        """
        # Pass 1: Draw Background (Grass) for ALL tiles
        # This ensures there is a background under transparent images
        # and covers the empty/occupied spots.
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * self.tile_size + offset_x, y * self.tile_size + offset_y, self.tile_size, self.tile_size)
                pygame.draw.rect(screen, (34, 139, 34), rect)

        # Pass 2: Draw Images (Roads, Buildings, Shops, Large Structures)
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.grid[y][x]
                rect = pygame.Rect(x * self.tile_size + offset_x, y * self.tile_size + offset_y, self.tile_size, self.tile_size)
                
                # Skip tiles that are just background (Empty) or placeholders (Occupied)
                if tile_type == TILE_EMPTY or tile_type == TILE_OCCUPIED:
                    continue
                
                if tile_type in self.images:
                    screen.blit(self.images[tile_type], rect)

    def is_road(self, x, y):
        """Helper to check if a coordinate is a road."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] == TILE_ROAD
        return False

        return TILE_EMPTY

    def get_parking_spots(self):
        """
        Returns a list of (x, y) tuples representing valid parking spots.
        A valid spot is a ROAD tile that is adjacent to a BUILDING or SHOP.
        """
        spots = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == TILE_ROAD:
                    # Check neighbours
                    has_building = False
                    for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.height and 0 <= nx < self.width:
                            # Check if neighbour is a building or any type of shop
                            tile = self.grid[ny][nx]
                            if tile in ALL_BUILDINGS or tile in ALL_SHOPS:
                                has_building = True
                                break
                    if has_building:
                        spots.append((x, y))
        return spots

    def get_landmark_mission_spot(self, landmark_name):
        """
        Finds a road tile adjacent to the specified landmark.
        """
        target_lm = None
        for lm in LANDMARKS:
            if lm['name'] == landmark_name:
                target_lm = lm
                break
        
        if not target_lm:
            return None
            
        lx, ly = target_lm['x'], target_lm['y']
        lw, lh = target_lm['w'], target_lm['h']
        
        # Search perimeter of the landmark rectangle
        perimeter_tiles = []
        for r in range(ly-1, ly+lh+1):
            for c in range(lx-1, lx+lw+1):
                # Check if it's on the border of the rectangle
                if (r < ly or r >= ly+lh or c < lx or c >= lx+lw):
                    if 0 <= r < self.height and 0 <= c < self.width:
                        if self.grid[r][c] == TILE_ROAD:
                            perimeter_tiles.append((c, r))
                            
        if perimeter_tiles:
            return random.choice(perimeter_tiles)
        return None
