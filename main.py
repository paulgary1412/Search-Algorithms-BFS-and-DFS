import tkinter as tk
from view import View
from search_algos import location

if __name__ == "__main__":
    location = location()
    root = tk.Tk()
    root.title("OcaMuaña Lab Activity 4")
    view = View(root)
    view.setup()
    view.set_searcher(location)
    location.set_graph(view.graph.nodes)

    root.mainloop()