import networkx as nx
import matplotlib.pyplot as plt

def plot_graph(G):
    nx.draw(G, pos=nx.spring_layout(G, k=1))
    plt.show()
