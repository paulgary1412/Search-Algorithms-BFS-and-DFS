import tkinter as tk
from tkinter import ttk
from graphics.node_edge import Node, Edge
from typing import List, Dict

class Graph(tk.Canvas):
    def __init__(self, parent, nodes, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.nodes: List[Node] = nodes

     
        self.configure(bg='#191414')

        self.add_node_menu = tk.Menu(self, tearoff=0)
        self.add_node_menu.add_command(label="Add Node", command=self.add_node)
        self.selected_node = None
        self.open_node_menu = False
        self.bind("<Button-3>", self.show_popup)
        self.selected_end_node = None

        self.node_menu = tk.Menu(self, tearoff=0)
        self.node_menu.add_command(label="Rename Node", command=self.rename_node)
        self.node_menu.add_command(label="Add Edge", command=self.add_edge)
        self.node_menu.add_command(label="Delete Edge", command=self.delete_edge)
        self.node_menu.add_command(label="Delete Node", command=self.delete_node)

    def node_menu_mode(self, node: Node):
        self.selected_node = node
        self.open_node_menu = True

    def show_popup(self, event: tk.Event):
        try:
            self.event = event
            if self.selected_node and self.open_node_menu:
                self.node_menu.tk_popup(event.x_root, event.y_root, 0)
            else:
                self.add_node_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            if self.open_node_menu:
                self.node_menu.grab_release()
                self.open_node_menu = False
            else:
                self.add_node_menu.grab_release()

    def add_node(self):
     
        clicked_on_node = False
        x, y = self.event.x, self.event.y
        for node in self.nodes:
            if node.contains(x, y):
                clicked_on_node = True
                break

        if not clicked_on_node:
           
            existing_names = sorted([node.tag[1:] for node in self.nodes])
            new_name = self.find_next_alphabetical_name(existing_names)

         
            node = Node(self, new_name, x, y)
            self.tag_bind(node.tag, "<Button-3>", lambda event, x=node: self.node_menu_mode(x))
            self.nodes.append(node)

    def find_next_alphabetical_name(self, existing_names):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for letter in alphabet:
            if letter not in existing_names:
                return letter

    def rename_node(self):
        title = f"Rename Node: {self.selected_node.tag[1:]}"
        self.popup = self.generate_small_popup(self, title, self.event.x_root, self.event.y_root)

        ttk.Label(self.popup, text="Node Name:", background='#191414', foreground='white').pack(pady=5)  
        entry = ttk.Entry(self.popup)
        entry.pack(pady=5)
        entry.focus_set()

        def rename():
            new_name = entry.get()
            if new_name in [node.tag[1:] for node in self.nodes]:
                self.popup.destroy()
                return  # TODO: 
            node = self.selected_node.rename(entry.get())
            self.tag_bind(node.tag, "<Button-3>", lambda event, x=node: self.node_menu_mode(x))
            self.popup.destroy()

        entry.bind("<Return>", lambda event: rename())
        rename_btn = ttk.Button(self.popup, text="Rename Node", 
                    command=lambda: rename(), style='Spotify.TButton')

    def delete_node(self):
        self.selected_node.delete()
        self.nodes.remove(self.selected_node)

    def add_edge(self):
        self.config(cursor="circle")
        self.bind("<Button-1>", self.select_end_node)

    def select_end_node(self, event: tk.Event):
        x, y = event.x, event.y
        for node in self.nodes:
            if node.contains(x, y):
                self.selected_end_node = node
                self.create_edge()
                break
        self.config(cursor="arrow")
        self.unbind("<Button-1>")

    def create_edge(self):
        node1 = self.selected_node
        node2 = self.selected_end_node

        self.popup = self.generate_small_popup(self, "Add Edge", self.event.x_root, self.event.y_root)
        directed = tk.BooleanVar()
        directed_cb = ttk.Checkbutton(self.popup, text="Directed", variable=directed)
        directed_cb.pack(pady=5)

        add_edge_btn = ttk.Button(self.popup, text="Add Edge", 
                command=lambda: [self.popup.destroy(), node1.add_edge(node2, directed=directed.get())], style='Spotify.TButton')  
        add_edge_btn.pack(pady=5)

    def delete_edge(self):
        node1 = self.selected_node
        self.popup = self.generate_small_popup(self, "Delete Edge", self.event.x_root, self.event.y_root, geometry="200x275")
        if not node1.edges:
            ttk.Label(self.popup, text="No edges to delete.", background='#191414', foreground='white').pack(pady=5)  
            return

        main = ttk.Frame(self.popup, padding=5)
        node2_select_frame = ttk.Frame(main)
        ttk.Label(node2_select_frame, text="Node to:", background='#191414', foreground='white').pack(side=tk.LEFT, pady=5) 
        edge_map: Dict[str, Edge] = {}
        def update_edge_list(event=None):
            node2 = node2_cb.get()
            edge_listbox.delete(0, tk.END)
            edge_map.clear()
            for edge in node1.get_edges_to("_" + node2):
                edge_str = str(edge)
                edge_map[edge_str] = edge
                edge_listbox.insert(tk.END, edge_str)
    
        node2_cb = ttk.Combobox(node2_select_frame, state="readonly",
                                values=[node.tag[1:] for node in node1.edges.keys()], style='Spotify.TCombobox')  
        node2_cb.current(0)
        node2_cb.bind("<<ComboboxSelected>>", lambda event: update_edge_list)
        node2_cb.focus_set()
        node2_cb.pack(side=tk.LEFT, pady=5)
        node2_select_frame.pack()

        edge_list_frame = ttk.Frame(main, width=200)
        ttk.Label(edge_list_frame, text="Edges:", background='#191414', foreground='white').pack(anchor=tk.NW)  
        list_frame = tk.Frame(edge_list_frame, relief=tk.SUNKEN, bd=1, background="white")
        edge_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, background="white", selectbackground="gray", exportselection=False)
        edge_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=edge_listbox.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        edge_listbox.config(yscrollcommand=scroll_y.set)
        list_frame.pack(pady=5)
        edge_list_frame.pack()

        update_edge_list()

        def delete_edge():
            selected_edge = edge_listbox.get(edge_listbox.curselection())
            if selected_edge in edge_map:
                edge_map[selected_edge].delete()
            self.popup.destroy()

        ttk.Button(main, text="Delete Edge", command=delete_edge, style='Spotify.TButton').pack(pady=5)  
        main.pack()

    def generate_small_popup(self, parent, title, x, y, geometry="100x100"):
        popup = tk.Toplevel(parent)
        popup.title(title)
        popup.geometry(geometry + f"+{x}+{y}")
        popup.configure(bg='#191414')
        return popup
