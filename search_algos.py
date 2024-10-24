from graphics.node_edge import Node, Edge
from collections import deque
from typing import List, Optional, Deque, Dict

class location:
    def __init__(self):
        self.graph: List[Node] = None

    def set_graph(self, graph: List[Node]):
        self.graph = sorted(graph, key=lambda node: node.tag[1:])

    def dfs(self, src: Node, dst: Optional[Node]=None, visited: Optional[List[Node]]=None):
        if visited is None:
            visited = []
        found = self.dfs_util(src, visited, dst)
        if not found:
            unvisited = sorted([node for node in self.graph if node not in visited], key=lambda node: node.tag[1:])
            if unvisited:
                return self.dfs(unvisited[0], dst, visited)
        return (visited, found)

    def dfs_util(self, node: Node, visited: List[Node], dst: Optional[Node]):
        visited.append(node)
        if dst is not None and node == dst:
            return True

        adjacents = sorted(node.get_adjacent_nodes(), key=lambda node: node.tag[1:])
        for adj in adjacents:
            if adj not in visited and adj != node:
                if self.dfs_util(adj, visited, dst):
                    return True

        return False

    def bfs(self, src: Node, dst: Optional[Node]=None, visited: Optional[List[Node]]=None):
        if visited is None:
            visited = []
        found = False
        queue = deque([src])
        while queue:
            node = queue.popleft()
            if node == dst:
                found = True
                visited.append(node)
                break
            adjacents = sorted(node.get_adjacent_nodes(), key=lambda node: node.tag[1:])
            for adj in adjacents:
                if not (adj in visited or adj in queue) and adj != node:
                    queue.append(adj)
            visited.append(node)
        if not found:
            unvisited = sorted([node for node in self.graph if node not in visited], key=lambda node: node.tag[1:])
            return self.bfs(unvisited[0], dst, visited)
        return (visited, found)

    def iddfs(self, src: Node, dst: Node):
        max_depth = 0
        paths: Dict[int, List[Node]] = {}
        found = [False]
        while True:
            natural_failure = [True]
            path = deque([src])
            self.iddfs_util(max_depth, path, dst, natural_failure, found)
  
            if max_depth != 0 and path == paths[max_depth-1]:
                break
            paths[max_depth] = path
            max_depth += 1
            if natural_failure[0] or found[0]:
                break
        return (paths, found[0])

    def iddfs_util(self, max_depth: int, path: Deque[Node], dst: Optional[Node], natural_failure: List[bool], found, prev_nodes: deque[Node]=None):
        if prev_nodes is None:
            prev_nodes = deque([])
        node = path[-1]
        if dst is not None:
            if node == dst and max_depth == 0:
                found[0] = True
                return

        if max_depth > 0:
            nodes = sorted(node.get_adjacent_nodes(), key=lambda node: node.tag[1:])
            prev_nodes.append(node)
            for adj in nodes:
                if adj != node and adj not in prev_nodes:
                    path.append(adj)
                    self.iddfs_util(max_depth-1, path, dst, natural_failure, found, prev_nodes)
            prev_nodes.pop()
        elif node.get_adjacent_nodes():
            natural_failure[0] = False



if __name__ == "__main__":
    import tkinter as tk
    canvas = tk.Canvas()


   
    nodes: List[Node] = [Node(canvas, str(i), i*100, i*100) for i in range(7)]
    nodes[0].add_edge(nodes[1])
    nodes[0].add_edge(nodes[2])
    nodes[0].add_edge(nodes[4])
    nodes[1].add_edge(nodes[3])
    nodes[1].add_edge(nodes[5])
    nodes[2].add_edge(nodes[6])
    nodes[4].add_edge(nodes[5])

    searcher = location()
    searcher.set_graph(nodes)
  
    print(searcher.iddfs(nodes[0], None))
