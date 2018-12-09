import networkx as nx
import matplotlib.pyplot as plt

def plot_graph(G):
    nx.draw(G, pos=nx.spring_layout(G, k=1), alpha=.5)
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
