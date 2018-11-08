import sys
import sqlite3
import csv

def create_db(tsv_filename, headers, database_name, table_name):
    """
    Create a sqlite3 database from a csv.

    Arguments:
        tsv_filename (str): The filename of the source csv
        headers (list): List of header strings to use as table columns
        database_name (str): The name of the database to connect to
        table_name (str): The name of the table to be created
    """
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    table_columns = ", ".join(headers)  # subreddit_name, time_stamp, ..., text
    table_type_columns = ", ".join(map(lambda header: header + " text", headers))  # # subreddit_name,text time_stamp text , ..., text text
    cur.execute("CREATE TABLE {} ({});".format(table_name, table_type_columns))

    with open(tsv_filename,'r') as source_f:
        dict_reader = csv.DictReader(source_f, delimiter='\t', fieldnames=headers)
        record = [tuple([comment[header] for header in headers]) for comment in dict_reader]

    placeholders = ", ".join(["?"] * len(headers))
    cur.executemany("INSERT INTO {} ({}) VALUES ({});".format(table_name, table_columns, placeholders), record)
    con.commit()
    con.close()


def main(source_filename, database_name, table_name):
    headers = ["subreddit_name",  "time_stamp", "subreddit_id",  "comment_id",
    "parent_comment_id", "author_name", "score", "random_id", "thread_link_id", "text"]
    create_db(source_filename, headers, database_name, table_name)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception("usage: python load_data.py <source>.tsv <database_name>.db <tablename>")
    source_filename = sys.argv[1]
    database_name = sys.argv[2]
    table_name = sys.argv[3]
    main(source_filename, database_name, table_name)
