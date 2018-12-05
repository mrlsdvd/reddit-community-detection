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
    user_topic_graph = nx.read_edgelist(G_path, nodetype=int)
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


def create_user_user_graph(user_topic_graph, connect_nodes_func, out_filename=None):
    """
    Creates user-user graph, by connecting nodes of users based on how similar
    users are.

    Arguments:
        user_topic_graph (nx.Graph): User-topic graph
        connect_nodes_func (func): Function that takes a user-topic graph,
            user node 1, and user node 2, and returns True if the two nodes
            should be connected and False otherwise
        out_filename (str): Location of where to save user-user edge list. If
            None, graph will not be saved

    Returns:
        user_user_graph (nx.Graph): User-user graph
    """
    # User nodes are those with positive ids!
    all_nodes = user_topic_graph.nodes()
    user_nodes = list(filter(lambda node: node > 0, all_nodes))
    # Create graph of user nodes
    user_user_graph = nx.Graph()
    user_user_graph.add_nodes_from(user_nodes)
    # Connect user nodes
    num_user_nodes = len(user_nodes)
    for i in range(num_user_nodes):
        node_1 = user_nodes[i]
        for j in range(i+1, num_user_nodes):
            node_2 = user_nodes[j]
            if connect_nodes_func(user_topic_graph, node_1, node_2):
                user_user_graph.add_edge(node_1, node_2)

    # Save graph if necessary
    if out_filename:
        nx.write_edgelist(user_user_graph, out_filename)

    return user_user_graph


def connect_on_IOU(user_topic_graph, u, v, threshold=0.3):
    """
    Dertermines whether to connect to nodes u and v based on their charactestics
    in the user-topic graph. Specifically, if the IOU (intersection over union)
    ratio of the neighbors of each node are above the threshold, then the
    two nodes are determined to be connected.

    Arguments:
        user_topic_graph (nx.Graph): User-topic graph
        u (int): Node to be potentially connected
        v (int): Node to be potentially connected
        threshold (float): Value for wich IOU ratio must be above for nodes to
            be connected

    Returns:
        connect (bool): Whether the two nodes should be connected
    """
    common_neigbhors = len(list(nx.common_neighbors(user_topic_graph, u, v)))
    # print(common_neigbhors)
    u_neighbors = len(list(user_topic_graph.neighbors(u)))
    v_neighbors = len(list(user_topic_graph.neighbors(v)))
    total_neighbors =  u_neighbors + v_neighbors
    # print(total_neighbors)
    if total_neighbors < 1:
        IOU = 0.
    else:
        IOU = float(common_neigbhors) / total_neighbors

    # print(IOU)

    if IOU > threshold:
        return True
    return False



def main():
    user_topic_graph_path = "../data/processed/author_topic.txt"
    topic_freqs_path = "../data/processed/topic_freq.txt"
    user_user_graph_path = "../data/processed/user_user.txt"

    user_topic_graph = load_user_topic_graph(user_topic_graph_path)
    topic_freqs = load_topic_frequencies(topic_freqs_path, sort_freqs=True)
    print("Total topics: {}".format(len(topic_freqs)))
    user_topic_graph = keep_top_n_topics(user_topic_graph, topic_freqs, n=20)
    user_user_graph = create_user_user_graph(user_topic_graph, connect_on_IOU, out_filename=user_user_graph_path)
    # Report things about user-user graph
    print("User-user graph has {} nodes and {} edges".format(user_user_graph.number_of_nodes(), user_user_graph.size()))


if __name__ == '__main__':
    main()
