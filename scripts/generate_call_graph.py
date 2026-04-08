from pathlib import Path
import ast
import matplotlib.pyplot as plt
import networkx as nx

SRC = Path("src/eeg_causal")
OUT = Path("docs/diagrams")
OUT.mkdir(parents=True, exist_ok=True)

module_names = [p.stem for p in SRC.glob("*.py") if p.name != "__init__.py"]
edges = []
for path in SRC.glob("*.py"):
    if path.name == "__init__.py":
        continue
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module in module_names:
            edges.append((path.stem, node.module))

G = nx.DiGraph()
G.add_nodes_from(module_names)
G.add_edges_from(edges)

plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, seed=7)
nx.draw_networkx(G, pos, with_labels=True, node_size=2200, arrows=True)
plt.axis("off")
plt.tight_layout()
plt.savefig(OUT / "module_dependency_graph_regenerated.png", dpi=200, bbox_inches="tight")
