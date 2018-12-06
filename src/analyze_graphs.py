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


def extract_topics_from_community(user_topic_graph, community, ratio_thresh=0.5):
    """
    Extracts the top topics from a community based on what ratio of user nodes
    the topic is shared. That is, if
    (# users that share topic) / (# users in community) > ratio,
    then the topic will be returned.

    Arguments:
        user_topic_graph (nx.Graph): User-topic graph to link users to
            their topics
        community (list): List of node (ids) in community
        ratio_thresh (float): Ratio of users that topic must be linked to, to be
            included in returned topic set

    Returns:
        topic_ratios (set): Set of 'top' (topic, ratio) tuples
    """
    topic_counts = dict()  # Map of topic id  -> num members linked to it
    topic_ratios = set()  # Set of (topic, ratio) tuple
    for user in community:
        # Get user's topics from user-topic graph
        user_topics = list(user_topic_graph.neighbors(user))
        # Compute ratio for each topic, if topic hasn't already been processed
        for topic in user_topics:
            if topic not in topic_counts:
                topic_counts[topic] = 0
            topic_counts[topic] += 1

    # Compute ratios for each topic and add to output set if ratio is high enough
    num_members = len(community)
    for topic in topic_counts:
        topic_ratio = float(topic_counts[topic]) / num_members
        if topic_ratio > ratio_thresh:
            topic_ratios.add((topic, topic_ratio))
