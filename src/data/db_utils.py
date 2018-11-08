import sqlite3
import sys

"""
Provides some utilities for querying different data from the reddit comment db.
"""

class DBWrapper():
    def __init__(self, db_name):
        self.con = sqlite3.connect(db_name)
        self.cur = self.con.cursor()

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
        """
        query = "SELECT text FROM comments WHERE author_name LIKE \'{}\'".format(author_name)
        if limit:
            query += " LIMIT {}".format(limit)
        self.cur.execute(query)

        comments = self.cur.fetchall()
        return comments
