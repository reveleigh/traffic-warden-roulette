class Node:
    """
    A node in the Linked List.
    Stores data and a reference to the next node.
    """
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    """
    A custom Linked List implementation for tracking player history.
    Required for NEA complex data structure marks.
    """
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data):
        """Adds a new node to the end of the list."""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def pop(self):
        """
        Removes the last node from the list and returns its data.
        Returns None if list is empty.
        """
        if not self.head:
            return None
        
        # If only one element
        if self.head == self.tail:
            data = self.head.data
            self.head = None
            self.tail = None
            self.size -= 1
            return data
        
        # Traverse to find the node before tail
        current = self.head
        while current.next != self.tail:
            current = current.next
        
        data = self.tail.data
        self.tail = current
        self.tail.next = None
        self.size -= 1
        return data

    def to_list(self):
        """Converts the linked list to a standard Python list for easy reading."""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
