import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

def plot_graph(G, communities=None):
    if communities is None:
        communities = [G.nodes()]
    num_communities = len(communities)
    colors = ['r', 'b', 'g', 'o'] * num_communities
    for i in renge(num_communities):
        community = communities[i]
        nx.draw_networkx_nodes(G, nodelist=community, node_color=colors[i], pos=nx.spring_layout(G, k=1), alpha=.8)
    nx.draw_networkx_edges(G, pos=nx.spring_layout(G, k=1))
    plt.show()


def get_literal_topics(topic_nodes, topic_map):
    """
    Given list of topic node ids, returns actual topic strings

    Arguments:
        topic_nodes (list): List of topic node ids
        topic_map (dict): Mapping from topic node id to topic literals

    Returns:
        literal_topics (list): List of topics
    """
    literal_topics = []
    for topic_node in topic_nodes:
        literal_topics.append(topic_map[topic_node])
    return literal_topics


def create_topic_map(node_topic_path):
    """
    Creates topic map from tsv file

    Arguments:
        node_topic_path (str): Path to tsv file containing mapping from
            topic literal to node id

    Returns:
        topic_map (dict): Mapping from topic node id to topic literals
    """
    topic_map = dict()
    with open(node_topic_path, 'r') as node_topics:
        for line in node_topics:
            topic, node = node_topics.split('\t')
            node = int(node)
            topic_map[node] = topic

    return topic_map
