import networkx as nx
import matplotlib.pyplot as plt
import csv


def load_user_topic_graph(G_path, verbose=True):
    """
    Loads user-topic graph from saved edge list

    Arguments:
        G_path (str): String path of file containing user-topic edge list
        verbose (bool): If true basic info of graph is printed

    Returns:
        user_topic_graph (nx.Graph): User-topic graph
    """
    user_topic_graph = nx.read_edgelist(G_path)
    if verbose:
        print("Number of nodes: {}".format(nx.number_of_nodes(user_topic_graph)))
        print("Number of edges: {}".format(nx.number_of_edges(user_topic_graph)))
    return user_topic_graph


def load_topic_frequencies(topic_freqs_path, sort_freqs=True):
    """
    Loads frequencies of topics.

    Arguments:
        topic_freqs_path (str): String path of file containing topic ids and
            frequenies
        sort_freqs (bool): Whether to sort frequency pairs in descending order
            of frequency
    Returns:
        frequencies (list): List of (id, freq) pairs
    """
    frequencies = []

    with open(topic_freqs_path) as tsv_rd:
        rd = csv.reader(tsv_rd, delimiter="\t", quotechar='"')
        for row in rd:
            topic_id = int(row[0])
            freq = int(row[1])
            frequencies.append((topic_id, freq))

    if sort_freqs:
        frequencies.sort(key=lambda x: x[1], reverse=True)
    return frequencies



def keep_top_n_topics(user_topic_graph, topic_frequencies, n=20):
    """
    Removes topic nodes from the user-topic graph that are not part of the
    top n topics, based on frequency

    Arguments:
        user_topic_graph (nx.Graph): User-topic graph
        topic_frequencies (list): List of (id, freq) pairs
        n (int): Number of top topic ids to return

    Returns:
        user_topic_graph (nx.Graph): User-topic graph with nodes not in top n removed
    """
    # Get topics not in top in
    lower_topics = set(map(lambda x: x[0], topic_frequencies[n+1:]))
    # Remove lower topic nodes from graph
    user_topic_graph.remove_nodes_from(lower_topics)

    return user_topic_graph


def create_user_user_graph(user_topic_graph, connect_nodes_func):
    """
    Creates user-user graph, by connecting nodes of users based on how similar
    users are.

    Arguments:
        user_topic_graph (nx.Graph): User-topic graph
        connect_nodes_func (func): Function that takes a user-topic graph,
            user node 1, and user node 2, and returns True if the two nodes
            should be connected and False otherwise

    Returns:
        user_user_graph (nx.Graph): User-user graph
    """
    pass


def main():
    user_topic_graph_path = "../data/processed/author_topic.txt"
    topic_freqs_path = "../data/processed/topic_freq.txt"

    user_topic_graph = load_user_topic_graph(user_topic_graph_path)
    topic_freqs = load_topic_frequencies(topic_freqs_path, sort_freqs=True)
    user_topic_graph = keep_top_n_topics(user_topic_graph, topic_freqs, n=20)


if __name__ == '__main__':
    main()
