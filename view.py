import tkinter as tk
from tkinter import ttk
from graphics.graph import Graph
from graphics.node_edge import Node, Edge
from search_algos import location

class View:
    def __init__(self, parent):
        self.container = parent
        self.searcher: location = None
        self.nodes = []

    def set_searcher(self, searcher):
        self.searcher = searcher

    def setup(self):
        self.create_widgets()
        self.setup_layout()

    def create_widgets(self):
        self.main_pane = ttk.PanedWindow(self.container, orient=tk.VERTICAL, style='Custom.TPanedwindow.Horizontal.TPanedwindow')  

        self.left_frame = ttk.Frame(self.main_pane, padding=5, style='Custom.TFrame')  
        self.canvas_frame = ttk.Frame(self.main_pane, padding=5, style='Custom.TFrame') 

        self.algo_frame = ttk.LabelFrame(self.left_frame, padding=5, style='Custom.TLabelframe') 
        self.caption_a = ttk.Label(self.algo_frame, text="Uninformed Search Algorithm", style='Spotify.TLabel') 
        self.caption_a.pack()

        self.choice = tk.StringVar()
        self.choice.set("DFS")

        self.options = ttk.Combobox(self.algo_frame, textvariable=self.choice, style='Custom.TCombobox')  
        self.options['values'] = ("DFS", "BFS", "IDDFS")
        self.options.pack()
        
        self.spacing_frame1 = ttk.Frame(self.left_frame, padding=5, height=10, style='Custom.TFrame') 

        self.setup_frame = ttk.LabelFrame(self.left_frame, text="", style='Custom.TLabelframe') 
        self.src_frame = ttk.Frame(self.setup_frame, padding=(5, 1), style='Custom.TFrame')  

        self.src_cb_label = ttk.Label(self.src_frame, text="Starting NODE:", style='Spotify.TLabel') 
        self.src_cb_label.pack(side=tk.LEFT)  
        self.src_node_cb = ttk.Combobox(self.src_frame, state="readonly", 
                                        postcommand=lambda: self.src_node_cb.configure(values=[node.tag[1:] for node in self.nodes]), style='Spotify.TCombobox')  
        self.src_node_cb.pack(side=tk.RIGHT, padx=(0, 5)) 

        self.dst_frame = ttk.Frame(self.setup_frame, padding=(5, 1), style='Custom.TFrame')  
        self.dst_cb_label = ttk.Label(self.dst_frame, text="Find NODE :", style='Spotify.TLabel')  
        self.dst_cb_label.pack(side=tk.LEFT) 
        self.dst_node_cb = ttk.Combobox(self.dst_frame, state="readonly", values=[None], 
                                        postcommand=lambda: self.dst_node_cb.configure(values=[None] + [node.tag[1:] for node in self.nodes]), style='Spotify.TCombobox')  
        self.dst_node_cb.pack(side=tk.RIGHT, padx=(0, 5))
                                        
        self.output_frame = ttk.Frame(self.left_frame, style='Custom.TFrame')  
        self.output_label = ttk.Label(self.output_frame, text="TERMINAL:", style='Spotify.TLabel') 
        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD, state="disabled", width=30, background='#1E1E1E', foreground='white')  

        def search():
            src = self.src_node_cb.get()
            dst = self.dst_node_cb.get()
            for node in self.nodes:
                if node.tag[1:] == src:
                    src = node
                    break
            for node in self.nodes:
                if node.tag[1:] == dst:
                    dst = node
                    break
            if not isinstance(dst, Node):
                dst = None
            if src:
                choice = self.choice.get()
                if choice == "DFS":
                    output, found = self.searcher.dfs(src, dst)
                    if output:
                        output = "Path: " + " -> ".join([node.tag[1:] for node in output])
                elif choice == "BFS":
                    output, found = self.searcher.bfs(src, dst)
                    if output:
                        output = "Path: " + " -> ".join([node.tag[1:] for node in output])
                elif choice == "IDDFS":
                    output, found = self.searcher.iddfs(src, dst)
                    if output:
                        output = "\n".join([f"Level {depth}: " + " -> ".join([node.tag[1:] for node in path]) for depth, path in output.items()])
                if dst:
                    if found:
                        output += f"\nNode {dst.tag[1:]} Found!"

                self.output_text.config(state="normal")
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, output)
                self.output_text.config(state="disabled")

        self.search_btn_frame = ttk.Frame(self.setup_frame, width=500, style='Custom.TFrame')  
        self.search_btn_frame.pack()
        self.search_btn = ttk.Button(self.search_btn_frame, text="RUN", command=search, style='Spotify.TButton')  


        self.graph = Graph(self.canvas_frame, self.nodes, bg="white", width=800, height=600, bd=1, relief=tk.SUNKEN)

   
        style = ttk.Style()
        style.theme_use('default') 
  
        style.configure('Custom.TPanedwindow.Horizontal.TPanedwindow', background='#008000')  
        style.configure('Custom.TFrame', background='#191414')  
        style.configure('Custom.TLabelframe', background='#191414', foreground='white')  
        style.configure('Spotify.TLabel', foreground='#1DB954', background='#191414')  
        style.configure('Spotify.TCombobox', fieldbackground='gray', background='gray', foreground='black', selectbackground='gray')  
        style.map('Spotify.TCombobox', background=[('disabled', 'gray')])  
        style.configure('Spotify.TButton', background='#1DB954', foreground='black')

    def setup_layout(self):
        self.main_pane.add(self.canvas_frame)  
        self.main_pane.add(self.left_frame)    
        self.main_pane.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)

        self.algo_frame.pack(anchor=tk.NW, fill=tk.X, expand=True)
        self.options.pack(fill=tk.X)

        self.create_spacing(self.left_frame, pad_top=5, pad_bottom=5, show_sep=False)
        self.setup_frame.pack(anchor=tk.NW, fill=tk.X, expand=True)
        self.src_frame.pack(fill=tk.X, expand=True)
        self.dst_frame.pack(fill=tk.X, expand=True)
        self.search_btn.pack(fill=tk.X)

        self.create_spacing(self.left_frame, pad_top=5, pad_bottom=5, show_sep=False)

      
        self.output_frame.pack(anchor=tk.NE, fill=tk.Y, expand=True, padx=10)

        self.output_label.pack(anchor=tk.W, fill=tk.X)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.create_spacing(self.left_frame, pad_top=5, pad_bottom=5, show_sep=False)

        self.graph.pack(fill=tk.BOTH, expand=True)

    @staticmethod
    def create_spacing(parent, pad_left=0, pad_right=0, pad_top=0, pad_bottom=0, show_sep=True, sep_orient=tk.HORIZONTAL):
        sep_frame = tk.Frame(parent, background='#191414')
        sep_frame.pack(padx=(pad_left, pad_right), pady=(pad_top, pad_bottom), fill=tk.X)
        separator = ttk.Separator(sep_frame, orient=sep_orient)
        separator.pack(fill=tk.X) if show_sep else separator.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Graph Search")
    view = View(root)
    view.setup()
    root.mainloop()
