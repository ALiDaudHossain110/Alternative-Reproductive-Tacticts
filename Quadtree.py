class Quadtree:
    def __init__(self, bounds, capacity):
        self.bounds = bounds  # (x, y, width, height) of the region
        self.capacity = capacity  # Max objects before subdivision
        self.objects = []  # Objects currently in this region
        self.children = []  # Subdivided child nodes
        self.divided = False  # Whether this node has been subdivided

    def subdivide(self):
        """Divide the current node into 4 child nodes."""
        x, y, w, h = self.bounds
        half_width, half_height = w / 2, h / 2
        self.children = [
            Quadtree((x, y, half_width, half_height), self.capacity),  # Top-left
            Quadtree((x + half_width, y, half_width, half_height), self.capacity),  # Top-right
            Quadtree((x, y + half_height, half_width, half_height), self.capacity),  # Bottom-left
            Quadtree((x + half_width, y + half_height, half_width, half_height), self.capacity),  # Bottom-right
        ]
        self.divided = True

    def insert(self, obj):
        """Insert an object into the quadtree."""
        if not self._within_bounds(obj.rect):
            return False  # Ignore objects outside the bounds of this node

        if len(self.objects) < self.capacity:
            self.objects.append(obj)
            return True
        else:
            if not self.divided:
                self.subdivide()
            # Attempt to insert into child nodes
            for child in self.children:
                if child.insert(obj):
                    return True
        return False

    def query(self, range_rect):
        """Retrieve all objects within a specified range."""
        found = []
        if not self._intersects(range_rect):
            return found  # If range doesn't intersect this node, return empty

        # Check objects in the current node
        for obj in self.objects:
            if self._within_bounds(obj.rect, range_rect):
                found.append(obj)

        # Check child nodes if subdivided
        if self.divided:
            for child in self.children:
                found.extend(child.query(range_rect))
        return found

    def _within_bounds(self, obj_rect, bounds=None):
        """Check if a rectangle is within bounds."""
        if bounds is None:
            bounds = self.bounds
        x, y, w, h = bounds
        return (
            obj_rect.x >= x and
            obj_rect.y >= y and
            obj_rect.x + obj_rect.width <= x + w and
            obj_rect.y + obj_rect.height <= y + h
        )

    def _intersects(self, range_rect):
        """Check if two rectangles intersect."""
        x, y, w, h = self.bounds
        rx, ry, rw, rh = range_rect
        return not (x + w < rx or rx + rw < x or y + h < ry or ry + rh < y)
