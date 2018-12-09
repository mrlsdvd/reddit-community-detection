import itertools
import networkx as nx
from networkx.algorithms.community.modularity_max import greedy_modularity_communities
from networkx.algorithms.community import centrality

"""
Analyze user-user graphs with community detection and more
"""

def configuration_model(G, verbose=True):
    """
    Creates a random graph with the same degree sequence as G.

    Arguments:
        G (networkx.Graph): Graph for which the degree sequence is from
    Returns:
        A random graph with the same degree sequence as G (configuration model)
    """
    deg_sequence = []

    for nid in G.nodes():
        deg_sequence.append(G.degree(nid))

    config = nx.configuration_model(deg_sequence)
    if verbose:
        print("Number of nodes: {}".format(nx.number_of_nodes(config)))
        print("Number of edges: {}".format(nx.number_of_edges(config)))

    return config


def modularity_communities(G):
    """
    Finds communities that maximize modularity.

    Arguments:
        G (networkx.Graph): Graph for which communities will be found
    Returns:
        communities (list): List of tuples of nodes, where each tuple of nodes
            represents a community
    """
    communities = greedy_modularity_communities(G)
    return list(communities)


def top_down_communities(G, num_communities=20):
    """
    Computes communities using the Girvan-Newman method, where at each step,
    the edge with the highest edge-betweeness score is removed. This function
    returns the communities at each level until there are num_cummunities
    communities.

    Arguments:
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
                topic_counts[topic] = 0.
            topic_counts[topic] += 1.

    # Compute ratios for each topic and add to output set if ratio is high enough
    num_members = len(community)
    for topic in topic_counts:
        topic_ratio = topic_counts[topic] / num_members
        if topic_ratio > ratio_thresh:
            topic_ratios.add((topic, topic_ratio))


def community_topic_evolution(community_levels, user_topic_graph, sample_n=None):
    """
    Analyzes the topic distribution in communities over levels (such as those
    returned by Girvan-Newman community detection).

    Arguments:
        community_levels (list): List of tuples of list of nodes, where tuple at
            position i consisists of lists of nodes representing the communities
            after iteration i+1 of the Girvan-Newman method
        user_topic_graph (nx.Graph): User-topic graph to link users to
            their topics
        sample_n (int): If not None, then sample_n topics will be sampled from
            the topic distribution of each community, as opposed to keeping
            all topics

    Returns:
        evolution (list): List of tuples of list of topics, where tuple at
            position i consists of lists of topics corresponding to the
            distribution of topics for each community after iteration i+1 of
            the Girvan-Newman method
    """
    evolution = []
    # Consider each level
    for level in community_levels:
        level_topics = []
        # Consider each community in level
        for community in level:
            # Extract topics from community
            topics = extract_topics_from_community(user_topic_graph, community)
            # Sample topics if necessary
            if sample_n is not None:
                topics = sample_topics(topics, sample_n)
            level_topics.append(topics)
        evolution.append(tuple(level_topics))

    return evolution


def sample_topics(topic_scores, take_top=True, n=5):
    """
    Samples topics based on their importance or prevalance.

    Arguments:
        topic_scores (list): List of (topic, score) tuples, where the score determines
            the importance / prevalance of the topic
        take_top (bool): Whether to simply take the top scoring topics
        n (int): Number of topics to be sampled
    Returns:
        sample (list): List of randomly sampled topics
    """
    if take_top:
        sorted_topic_scores = sorted(topics, key=lambda ts: ts[1])
        top_n_topics = list(map(lambda t: t[0], sorted_topic_scores[:n]))
        return top_n_topics

    topics, scores = tuple(zip(*topics))
    # Normalize scores to sum to 1
    scores = np.array(scores)
    scores = scores / np.sum(scores)
    # Number of values that will be drawn should be min(n, len(topics))
    n = min(n, len(topics))

    topics = np.random.choice(topics, size=n, replace=False, p=scores)
    return topics.tolist()


def compute_betweenness_graph(user_user_graph):
    """
    Computes the shortest-path betweenness centrality for each node.

    Arguments:
        user_user_graph (nx.Graph): User-user graph to link users to
            other users

    Returns:
        node_betweenness (dict): Dictionary of nodes with betweenness centrality as the value
    """
    return centrality.betweenness_centrality_subset(user_user_graph)


def compute_community_betweenness(node_betweenness, community):
    """
    Computes the averege betweenness of a community. This is the average of the
    betweenness score for all the nodes in the community with respect to the
    user-user graph. The idea being that communities that have different
    views and interests will have higher average betweeness, since their
    nodes will be linked to nodes in other communities.

    Arguments:
        node_betweenness (dict): Dictionary of nodes with betweenness centrality as the value
        community (list): List of node (ids) in community

    Returns:
        community_betweenness (float): Average betweeness of community
    """

    sum_betweenness = 0

    for nid in community:
        sum_betweenness = sum_betweenness + node_betweenness[nid]

    return float(sum_betweenness)/len(community)


def determine_prototype(user_user_graph, community):
    """
    Determines the 'prototype' node that best describes the community. This
    node is determined to be that with the largest in-community degree / egonet.

    Arguments:
        user_user_graph (nx.Graph): User-user graph to link users to
            other users
        community (list): List of node (ids) in community

    Returns:
        prototype (int): ID of node that best describes the community
    """

    max_edges = 0
    prototype = None

    for nid in community:
        # all neighbors of the node in user_user_graph
        neighbors = user_user_graph.neighbors(nid)

        # find all neighbors in the community by taking an intersection
        in_community_neighbors = intersection(neighbors, community)
        # in_community_degree = len(in_community_neighbors)

        # find induced subgraph (in-community ego graph)
        in_community_neighbors.append(nid)
        ego_graph = user_user_graph.subgraph(in_community_neighbors)

        # number of edges in the ego graph
        ego_graph_edges = len(ego_graph.edges())
        if ego_graph_edges > max_ego_graph:
            max_edges = ego_graph_edges
            prototype = nid

    return prototype
