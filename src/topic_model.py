import sys
import numpy as np
import sqlite3
from db_utils import DBWrapper
import nltk
from nltk import word_tokenize
nltk.download('averaged_perceptron_tagger')
from nltk import pos_tag
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

def extract_topics(dbw, author_output, topic_output,
                   topic_freq_output, author_topic_output):
    """
    For each author, the comments written by that author are analyzed in two
    ways to extract topics. First, the sentiment of the overall comment is
    extracted. Next NOUNs in the comment are extracted. The topics in the
    comment are then the (NOUN, sentiment) pairs.

    SIA.polarity_scores() returns compound neg, neu, and pos values.
    The compound values are used for determining sentiment. Specifically,
    if compound < 0, then the sentiment is labeled as negative and if
    compund > 0, the the sentiment is labeled as positive.

    While processing each comment for each author, and extrating topics, the
    frequency of each topic is kept. The author is also 'linked' to the topics.

    Arguments:
        dbw (DBWrapper): Databaser wrapper object linked to the databse that
            will be queried for the author and comments
        author_output (str): Filename of where to write author_name ->
            author_graph_id
        topic_output (str): Filename of where to write topic_name ->
            topic_graph_id
        topic_freq_output (str): Filename of where to write topic_graph_id ->
            topic frequency
        author_topic_output (str): Filename of where to write author_graph_id
            -> topic_graph_id edges
    """
    # Trackers:
    author_to_id_map = dict()  # Map from author_name -> author_graph_id
    topic_to_id_map = dict()  # Map from (word, sentiment) -> topic_graph_id
    topic_id_to_frequency_map = dict()  # Map from topic_graph_id -> frequency
    author_topic_pairs = set()  # Set of (author_graph_id, topic_graph_id) pairs

    # Instantiate SIA object
    sid = SIA()
    # Get unique list of authors from dbw
    # Load top authors
    top_authors = []
    with open("top_commentors.tsv", 'r') as top_commentors:  # To run from data/raw
        for line in top_commentors:
            top_authors.append(line.strip())

    # authors = dbw.get_authors(3000)
    authors = top_authors
    # For each author, get its comments
    author_graph_id = 1
    topic_graph_id = -1

    with open(author_topic_output, 'w') as author_topic_f:
        for i, author in enumerate(authors):
            if i % 100 == 0:
                print("On author {}: {}".format(i, author))
            # Record author name and author_graph_id
            author_to_id_map[author] = author_graph_id
            # TODO Maybe add author to db table?

            author_comments = dbw.get_author_comments(author)
            for comment in author_comments:
                # Extract sentiment
                sentiment = vader_sentiment_extractor(comment, sid)
                # Extract NOUN topics
                topics = pos_topic_extractor(comment)

                for topic in topics:
                    # Record (topic, sentiment) and topic_graph_id
                    if (topic, sentiment) not in topic_to_id_map:
                        topic_to_id_map[(topic, sentiment)] = topic_graph_id
                        topic_id_to_frequency_map[topic_graph_id] = 0
                        # Increment topic graph id
                        topic_graph_id -= 1

                    # Decrement count of topic pair
                    topic_id_to_frequency_map[topic_to_id_map[(topic, sentiment)]] += 1
                    # TODO Maybe add topic to db table?

                    # Make note of author -> topic link by writing edge in file
                    author_id = author_to_id_map[author]
                    topic_id = topic_to_id_map[(topic, sentiment)]
                    if (author_id, topic_id) not in author_topic_pairs:
                        author_topic_f.write('{}\t{}\n'.format(author_id, topic_id))
                        author_topic_pairs.add((author_id, topic_id))

            # Increment author graph id
            author_graph_id += 1

        # Write out all mappings to files
        write_mappings(author_to_id_map, author_output)
        write_mappings(topic_to_id_map, topic_output)
        write_mappings(topic_id_to_frequency_map, topic_freq_output)


def vader_sentiment_extractor(comment, sid):
    """
    Get sentiment of a comment using nltk's vader SentimentIntensityAnalyzer.

    Arguments:
        comment (str): Comment to be analyzed
        sid (SentimentIntensityAnalyzer): Vader sentiment analyzer

    Returns:
        sentiment (str): Some representation of sentiment
    """
    sentiment = '+'
    polarity_map = sid.polarity_scores(comment)
    compound_val = polarity_map['compound']
    if compound_val < 0.:
        sentiment = '-'
    return sentiment

def pos_topic_extractor(comment):
    """
    Get nouns from a comment, where nouns are determined by nltk's pos tagger.
    Nouns with fewer than 2 charaters are ignored.

    Arguments:
        comment (str): Comment to be analyzed

    Returns:
        nouns (set): Set of nouns extracted from comment
    """
    words = word_tokenize(comment)
    pos_tags = pos_tag(words)

    # Filter out words that are not NOUNs and have fewer than 2 characters
    noun_tuples = list(filter(lambda pos_tag: pos_tag[1] == 'NN' and len(pos_tag[0]) > 2, pos_tags))
    nouns = set(map(lambda noun_tuple: noun_tuple[0].lower(), noun_tuples))
    return nouns


def write_mappings(mapping, output_name):
    with open(output_name, 'w') as out_f:
        for key in mapping:
            out_f.write('{}\t{}\n'.format(key, mapping[key]))


def main(db_name, author_output, topic_output,
    topic_freq_output, author_topic_output):
    dbw = DBWrapper(db_name)
    extract_topics(dbw, author_output, topic_output,
        topic_freq_output, author_topic_output)

if __name__ == '__main__':
    db_name = sys.argv[1]
    author_output = sys.argv[2]
    topic_output = sys.argv[3]
    topic_freq_output = sys.argv[4]
    author_topic_output = sys.argv[5]

    main(db_name, author_output, topic_output,
         topic_freq_output, author_topic_output)
