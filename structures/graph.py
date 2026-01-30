class Graph:
    """
    A custom Graph implementation for map navigation.
    Required for NEA complex data structure marks.
    Uses an adjacency list to store connections between nodes (intersections).
    """
    def __init__(self):
        # Dictionary mapping node_id -> list of connected node_ids
        self.adjacency_list = {}

    def add_node(self, node_id):
        """Adds a new node to the graph if it doesn't exist."""
        if node_id not in self.adjacency_list:
            self.adjacency_list[node_id] = []

    def add_edge(self, node_a, node_b):
        """Adds an undirected edge between two nodes."""
        if node_a in self.adjacency_list and node_b in self.adjacency_list:
            self.adjacency_list[node_a].append(node_b)
            self.adjacency_list[node_b].append(node_a) # Undirected graph
    
    def get_neighbors(self, node_id):
        """Returns the list of neighbours for a given node."""
        return self.adjacency_list.get(node_id, [])

    def pathfind(self, start_node, end_node):
        """
        Implements A* (A-Star) Pathfinding Algorithm.
        Returns a list of nodes representing the path from start to end.
        """
        # Open set: nodes to be evaluated (priority queue could be better, using list for now)
        open_set = [start_node]
        # Came from: map of navigated nodes to reconstruct path
        came_from = {}
        
        # g_score: cost from start to node
        g_score = {node: float('inf') for node in self.adjacency_list}
        g_score[start_node] = 0
        
        # f_score: g_score + heuristic cost to end
        f_score = {node: float('inf') for node in self.adjacency_list}
        f_score[start_node] = self.heuristic(start_node, end_node)
        
        while open_set:
            # Get node in open_set with lowest f_score
            current = min(open_set, key=lambda node: f_score[node])
            
            if current == end_node:
                return self.reconstruct_path(came_from, current)
            
            open_set.remove(current)
            
            for neighbor in self.get_neighbors(current):
                # Assumes distance between neighbours is always 1 (grid based)
                tentative_g_score = g_score[current] + 1
                
                if tentative_g_score < g_score[neighbor]:
                    # This path to neighbour is better than any previous one
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, end_node)
                    
                    if neighbor not in open_set:
                        open_set.append(neighbor)
                        
        return [] # No path found

    def heuristic(self, node_a, node_b):
        """
        Manhattan distance heuristic for grid grids.
        node is expected to be a tuple (x, y).
        """
        (x1, y1) = node_a
        (x2, y2) = node_b
        return abs(x1 - x2) + abs(y1 - y2)

    def reconstruct_path(self, came_from, current):
        """Rebuilds the path backwards from end to start."""
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.insert(0, current)
        return total_path
