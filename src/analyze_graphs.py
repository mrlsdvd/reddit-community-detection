import itertools
import networkx as nx
from nx.community import modularity_max as mod_max
from networkx.algorithms.community import centrality

"""
Analyze user-user graphs with community detection and more
"""

def modularity_communities(G):
    """
    Finds communities that maximize modularity.

    Args:
        G (networkx.Graph): Graph for which communities will be found
    Returns:
        communities (list): List of tuples of nodes, where each tuple of nodes
            represents a community
    """
    communities = mod_max.greedy_modularity_communities(G)
    return list(communities)


def top_down_communities(G, num_communities=20):
    """
    Computes communities using the Girvan-Newman method, where at each step,
    the edge with the highest edge-betweeness score is removed. This function
    returns the communities at each level until there are num_cummunities
    communities.

    Args:
        G (networkx.Graph): Graph that will be split into communities
        num_communities (int): Goal for number of communities

    Returns:
        community_levels (list): List of tuples of list of nodes, where tuple at
            position i consisists of lists of nodes representing the communities
            after iteration i+1 of the Girvan-Newman method
    """
    community_levels = []
    levels = centrality.girvan_newman(G)
    for level in itertools.takewhile(lambda l: len(l) <= num_communities, levels):
        community_levels.append(tuple(c for c in level))

    return community_levels
