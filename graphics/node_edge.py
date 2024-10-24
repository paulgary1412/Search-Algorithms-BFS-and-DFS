import tkinter as tk
from tkinter import ttk
from graphics.shapes import *

from typing import Dict, Set
import math

class Node:
    def __init__(self, canvas: tk.Canvas, name: str, x, y):
        self.canvas = canvas
        self.center = (x, y)
        self.draw(name)

        self.edges: Dict[Node, Set[Edge]] = {}

    def draw(self, name: str):
        self.tag = "_" + name
        self.label = self.canvas.create_text(self.center, text=name, font=("Arial", 20), tags=self.tag)
        bbox = self.canvas.bbox(self.label)
        height = bbox[3] - bbox[1]
        width = max(bbox[2] - bbox[0], height)
        self.circle = EllipseBuilder()\
                .set_center(self.center)\
                .set_a(width / (2**0.5))\
                .set_b(height / (2**0.5)).build()
        self.circle_cid = self.circle.draw(self.canvas, tag=self.tag, fill="#1DB954", outline="black", width=2) 
        self.canvas.tag_raise(self.label)

        self.canvas.tag_bind(self.tag, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.tag, "<B1-Motion>", self.on_drag)

    def on_press(self, event: tk.Event):
        self.move_pt = Point(event.x, event.y)

    def on_drag(self, event: tk.Event):
        dx = event.x - self.move_pt.x
        dy = event.y - self.move_pt.y
        self.move_pt.x = event.x
        self.move_pt.y = event.y
        self.canvas.move(self.tag, dx, dy)
        self.circle.update_center(dx, dy)  
        self.canvas.tag_raise(self.tag)
        self.center = (self.center[0] + dx, self.center[1] + dy)
        self.draw_edges()

    def rename(self, new_name: str, callback=None):
        self.canvas.delete(self.tag)
        self.draw(new_name)
        self.draw_edges()
        if callback is not None:
            callback()
        return self

    def contains(self, x, y):
        return self.circle.contains(x, y)

    def delete(self):
        self.canvas.delete(self.tag)
        self.canvas.delete(self.circle_cid)
        for node, edge_list in self.edges.items():
            for edge in edge_list:
                self.canvas.delete(edge.cid)
            node.edges.pop(self)

    def add_edge(self, node, directed=False):
        edges = self.edges.get(node)
        if edges is None:
            edges = set()
            self.edges[node] = edges
            node.edges[self] = edges
        edge = Edge(self.canvas, self, node, directed)
        edges.add(edge)
        if edge.type != LOOP:
            self.update_pt_angles(node)

    def draw_edges(self):
        for edges in self.edges.values():
            for edge in edges:
                edge.draw()

    def update_pt_angles(self, node):  # TODO: 
        edges: Set[Edge] = self.edges.get(node)
        if edges is None:
            return

        count = len(edges)
        if count == 1:
            e = edges.pop()
            e.set_pt_angle(0)
            edges.add(e)
        else:
            e_list = list(edges)
            start_idx = 0
            if count % 2 != 0:  
                e_list[0].set_pt_angle(0)
                start_idx = 1

            angle = math.pi/6
            for e1, e2 in zip(e_list[start_idx::2], e_list[start_idx+1::2]):
                e1.set_pt_angle(angle if e1.is_node1(self) else -angle)
                e2.set_pt_angle(-angle if e2.is_node1(self) else angle)
                angle += math.pi/6
        self.draw_edges()

    def delete_edge(self, edge):
        edge.is_node1(self) 
        edge.delete()

    def get_edges_to(self, nodeOrTag):
        if isinstance(nodeOrTag, Node):
            return self.edges.get(nodeOrTag, set())
        for node, edges in self.edges.items():
            if node.tag == nodeOrTag:
                return edges
        return set()

    def get_adjacent_nodes(self):
        adjacents = set()
        for node, edges in self.edges.items():
            for edge in edges:
                if edge.directed:
                    if edge.is_node1(self):
                        adjacents.add(node)
                        break
                else:
                    adjacents.add(node)
                    break
        return adjacents

    def __repr__(self):
        return f"Node({self.tag})"

    def __eq__(self, other):
        assert isinstance(other, Node)
        return self.tag == other.tag

    def __hash__(self):
        return hash(self.tag)


LINE = 0
ARC = 1
LOOP = 2
class Edge:
    def __init__(self, canvas: tk.Canvas, node1: Node, node2: Node, directed=False):
        self.canvas = canvas
        self.node1 = node1
        self.node2 = node2
        self.directed = directed
        self.type = LOOP if node1 == node2 else LINE
        self.pt_angle = 0  
        self.cid = None

    def set_pt_angle(self, angle):
        self.pt_angle = angle
        if angle != 0 and angle != math.pi:
            self.type = ARC

    def draw(self, fill="black", width=2):
        if self.cid is not None:
            self.canvas.delete(self.cid)
        canvas = self.canvas
        line: Line = LineBuilder()\
                .set_start_point(self.node1.center)\
                .set_end_point(self.node2.center).build()
        angle = line.get_angle()
        start_pt = self.node1.circle.get_point_from_angle(angle + self.pt_angle)
        end_pt = self.node2.circle.get_point_from_angle(angle + math.pi - self.pt_angle)

        arrow = tk.LAST if self.directed else None

        if self.type == LINE:
            self.cid = Line(start_pt, end_pt).draw_line(canvas, fill=fill, width=width, arrow=arrow)
        elif self.type == ARC:
            center = line.get_midpoint()
            b = (50 if self.pt_angle > 0 else -50) * abs(self.pt_angle/(math.pi/6))
            mid_pt = LineBuilder()\
                    .from_radians_and_length(center, line.get_perpendicular_angle(), b).end
            self.cid = Line(start_pt, end_pt, other_points=[mid_pt]).draw_line(canvas, arrow=arrow, fill=fill, width=width)
        elif self.type == LOOP:
            pass  # TODO: 
        else:
            raise ValueError("Invalid edge type")

    def is_node1(self, node):
        result = self.node1 == node
        if not result:
            try:
                assert self.node2 == node
            except AssertionError:
                raise ValueError("Node is not connected to this edge")
        return self.node1 == node

    def delete(self):
        if self.cid is not None:
            self.canvas.delete(self.cid)
        self.node1.edges[self.node2].remove(self)
        self.node1.update_pt_angles(self.node2)
        self.node2.update_pt_angles(self.node1)

    def __str__(self) -> str:
        directed = "Directed" if self.directed else "Undirected"
        return f"({self.node1.tag[1:]}, {self.node2.tag[1:]}): {directed}"

    def __repr__(self) -> str:
        return f"Edge({self.node1.tag}, {self.node2.tag})"



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Graph Search")

    canvas = tk.Canvas(root, bg="white", width=800, height=600, bd=1, relief=tk.SUNKEN)
    canvas.pack(fill=tk.BOTH, expand=True)

    node1 = Node(canvas, "A", 100, 100)
    node2 = Node(canvas, "B", 300, 200)
    node3 = Node(canvas, "C", 300, 500)
    node4 = Node(canvas, "D", 400, 400)

    node1.add_edge(node2, directed=True)

    node3.add_edge(node1, directed=True)
    node1.add_edge(node3)
    node1.add_edge(node3, directed=True)

    node1.add_edge(node4)
    node2.add_edge(node3)
    node2.add_edge(node4)
    node3.add_edge(node4)
  
    root.mainloop()