import sqlite3
import os


# def create_tables():
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     db_path = os.path.join(dir_path, 'DSC580-Luis.sqlite3')
#     conn = sqlite3.connect(db_path)
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL
#         )
#     ''')
#     conn.commit()
#     conn.close()
#
#
# # Call the function to create tables
# if __name__ == '__main__':
#     create_tables()
