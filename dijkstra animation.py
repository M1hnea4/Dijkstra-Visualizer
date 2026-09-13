import tkinter as tk
from tkinter import simpledialog, messagebox
import heapq
import os
import graphviz
import glob

def generate_image(step, graph, distances, parent, visited, current_node, priority_queue, output_folder):
    dot = graphviz.Digraph(comment=f'Step {step}')
    dot.attr(label=f'Step {step}: Analyzing node "{current_node}"', labelloc='t', fontsize='20')
    dot.attr(rankdir='LR')

    nodes_in_queue = {node for _, node in priority_queue}

    for node in graph:
        dist = distances[node]
        label = f"{node}\ndist = {dist if dist != float('inf') else '∞'}"
        color = 'lightgrey'
        if node in nodes_in_queue: color = 'lightblue'
        if node in visited: color = 'lightgreen'
        if node == current_node: color = 'tomato'
        dot.node(node, label=label, style='filled', fillcolor=color, shape='circle')

    for source_node, neighbors in graph.items():
        for dest_node, weight in neighbors.items():
            edge_color = 'gray'
            if parent.get(dest_node) == source_node:
                edge_color = 'blue'
            dot.edge(source_node, dest_node, label=str(weight), color=edge_color)

    dot.render(f'{output_folder}/step_{step:02d}', format='png', cleanup=True)

def generate_video_and_cleanup(folder, output_name):
    print("\n--- GENERATING GIF ANIMATION ---")
    gif_path = os.path.join(folder, f"{output_name}.gif")

    command = (
        f'ffmpeg -y -framerate 0.5 -i "{folder}/step_%02d.png" '
        f'-vf "scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" '
        f'"{gif_path}"'
    )
    
    os.system(command)
    
    for img in glob.glob(os.path.join(folder, '*.png')):
        os.remove(img)
    print(f"\n✅ Done! Animation saved at: {gif_path}")

class DijkstraGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Dijkstra Graph Drawer")
        self.canvas = tk.Canvas(root, width=900, height=700, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.nodes = {}  
        self.edges = []  
        self.current_source = None
        self.node_count = 0 
        
        instructions = (
            "INSTRUCTIONS:\n"
            "1. LEFT CLICK: Add node \n"
            "2. RIGHT CLICK node 1, then node 2: Create weighted EDGE\n"
            "3. Green Button: Run Algorithm"
        )
        tk.Label(root, text=instructions, bg="#f0f0f0", justify=tk.LEFT).pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_run = tk.Button(root, text="RUN DIJKSTRA & GENERATE GIF", 
                                command=self.run_algorithm, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.btn_run.pack(pady=10)

        self.canvas.bind("<Button-1>", self.add_node)
        self.canvas.bind("<Button-3>", self.handle_right_click)

    def add_node(self, event):
        name = chr(65 + self.node_count) 
        self.node_count += 1
        
        self.nodes[name] = (event.x, event.y)
        self.canvas.create_oval(event.x-20, event.y-20, event.x+20, event.y+20, fill="lightblue", tags=name, width=2)
        self.canvas.create_text(event.x, event.y, text=name, font=("Arial", 10, "bold"))

    def handle_right_click(self, event):
        items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        clicked_node = None
        for item in items:
            tags = self.canvas.gettags(item)
            if tags and tags[0] in self.nodes:
                clicked_node = tags[0]
                break
        
        if not clicked_node: return

        if not self.current_source:
            self.current_source = clicked_node
            self.canvas.itemconfig(self.canvas.find_withtag(clicked_node)[0], fill="orange")
        else:
            if clicked_node != self.current_source:
                cost = simpledialog.askinteger("Cost", f"Edge cost from {self.current_source} to {clicked_node}:")
                if cost is not None:
                    self.edges.append((self.current_source, clicked_node, cost))
                    x1, y1 = self.nodes[self.current_source]
                    x2, y2 = self.nodes[clicked_node]
                    self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=2, fill="gray")
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2 - 10, text=str(cost), fill="red", font=("Arial", 11, "bold"))
            
            self.canvas.itemconfig(self.canvas.find_withtag(self.current_source)[0], fill="lightblue")
            self.current_source = None

    def run_algorithm(self):
        if not self.nodes:
            messagebox.showerror("Error", "Please draw some nodes first!")
            return

        start = simpledialog.askstring("Start", "Starting node :").upper()
        target = simpledialog.askstring("Destination", "Target node :").upper()

        if start not in self.nodes or target not in self.nodes:
            messagebox.showerror("Error", "Node does not exist!")
            return

        graph = {n: {} for n in self.nodes}
        for u, v, w in self.edges:
            graph[u][v] = w
            
        self.root.destroy()
        
        folder = "dijkstra_tutorial"
        if not os.path.exists(folder): os.makedirs(folder)
        
        distances = {nod: float('inf') for nod in graph}
        distances[start] = 0
        parent = {nod: None for nod in graph}
        queue = [(0, start)]
        visited = set()
        step = 0

        while queue:
            d_curr, n_curr = heapq.heappop(queue)
            
            generate_image(step, graph, distances, parent, visited, n_curr, queue, folder)
            step += 1

            if d_curr > distances[n_curr]: continue
            visited.add(n_curr)

            for neighbor, cost in graph[n_curr].items():
                if distances[n_curr] + cost < distances[neighbor]:
                    distances[neighbor] = distances[n_curr] + cost
                    parent[neighbor] = n_curr
                    heapq.heappush(queue, (distances[neighbor], neighbor))

        generate_image(step, graph, distances, parent, visited, "FINISHED", [], folder)
        generate_video_and_cleanup(folder, "dijkstra_result")

if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraGui(root)
    root.mainloop()