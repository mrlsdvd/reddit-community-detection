import sqlite3
import sys

"""
Provides some utilities for querying different data from the reddit comment db.
"""

class DBWrapper():
    def __init__(self, db_name):
        """
        Initializes dbwrapper and creates tables that will be used.
        """
        self.con = sqlite3.connect(db_name)
        self.cur = self.con.cursor()
        # Create necessary tables if they do not already exist
        # self.cur.execute("CREATE TABLE IF NOT EXISTS topic (word, sentiment, graph_id, freq);")
        # self.cur.execute("CREATE TABLE IF NOT EXISTS author (author_name, graph_id);")
        # self.cur.execute("CREATE TABLE IF NOT EXISTS topic_author (author_name, graph_id);")
        # self.cur.commit()

    def __enter__(self):
        return self

    def __exit__(self):
        self.con.close()

    def get_author_comments(self, author_name, limit=None):
        """
        Query the comments associated with a particular author.

        Arguments:
            author_name (str): The auther whose comments we want to query
            limit (int): A limit on the number of comments to return

        Returns:
            comments (list): List of comments by the author
        """
        query = "SELECT text FROM comments WHERE author_name LIKE \'{}\'".format(author_name)
        if limit:
            query += " LIMIT {}".format(limit)
        self.cur.execute(query)

        comments = self.cur.fetchall()
        # Flatten comments into list of strings
        comments = list(map(lambda comment: comment[0], comments))
        return comments

    def get_authors(self, limit=None):
        """
        Fetches the unique author_names in the data

        Arguments:
            limit (int): A limit on the number of author names to return
                [for debugging purposes]

        Returns:
            authors (list): List of unique author names
        """
        query = "SELECT DISTINCT(author_name) FROM comments"
        if limit:
            query += " LIMIT {}".format(limit)
        self.cur.execute(query)

        authors = self.cur.fetchall()
        # Flatten authors into list of strings
        authors = list(map(lambda author: author[0], authors))
        return authors

    def insert_or_update_topic(self, noun, sentiment, graph_id):
        """
        Given a noun and its sentiment, if the pair is not already in the db,
        add a new record for it. If the pair is in the db, increment the
        frequency column.

        Arguments:
            noun (str): Noun of topic
            sentiment (str): Sentiment of topic ['+', '-']
            graph_id (int): Id of topic in graph

        Returns:
            inserted (bool): True if topic was inserted, False if topic was
                updated.
        """
        pass
