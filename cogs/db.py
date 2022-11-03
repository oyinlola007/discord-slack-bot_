import sqlite3

import cogs.config as config

conn = sqlite3.connect(config.DATABASE_NAME)

def initialize_db():
    try:
        conn.execute('''CREATE TABLE DISCORD_MESSAGE_LOG
                 (MESSAGE_ID TEXT PRIMARY KEY NOT NULL,
                 SENDER_ID TEXT,
                 MESSAGE_TYPE TEXT,
                 SLACK_TIMESTAMP TEXT,
                 CONTENT TEXT);''')
    except Exception as _:
        pass

    try:
        conn.execute('''CREATE TABLE SLACK_MESSAGE_LOG
                (SLACK_TIMESTAMP TEXT PRIMARY KEY NOT NULL,
                 SENDER_ID TEXT,
                 MESSAGE_TYPE TEXT,
                 MESSAGE_ID TEXT,
                 CONTENT TEXT,
                 REACTION TEXT);''')
    except Exception as _:
        pass

    conn.commit()

def insert_discord_log(message_id, sender_id, message_type, slack_timestamp, content):
    sqlite_insert_with_param = """INSERT INTO 'DISCORD_MESSAGE_LOG'
    ('MESSAGE_ID', 'SENDER_ID', 'MESSAGE_TYPE', 'SLACK_TIMESTAMP', 'CONTENT')
    VALUES (?, ?, ?, ?, ?);"""
    data_tuple = (message_id, sender_id, message_type, slack_timestamp, content)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def insert_slack_log(slack_timestamp, sender_id, message_type, message_id, content, reaction):
    sqlite_insert_with_param = """INSERT INTO 'SLACK_MESSAGE_LOG'
    ('SLACK_TIMESTAMP', 'SENDER_ID', 'MESSAGE_TYPE', 'MESSAGE_ID', 'CONTENT', 'REACTION')
    VALUES (?, ?, ?, ?, ?, ?);"""
    data_tuple = (slack_timestamp, sender_id, message_type, message_id, content, reaction)
    conn.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

def get_timestamp(message_id):
    try:
        return conn.execute(f"select SLACK_TIMESTAMP from DISCORD_MESSAGE_LOG where MESSAGE_ID='{message_id}'").fetchone()[0]
    except Exception as _:
        return "0"

def get_last_timestamp(default_ts):
    ts = conn.execute(f"select MAX(SLACK_TIMESTAMP) from SLACK_MESSAGE_LOG").fetchone()[0]
    if ts != None:
        return ts
    else:
        return default_ts

def limit_table_to_x_rows(table_name, limit):
    conn.execute(f"DELETE FROM {table_name} WHERE ROWID IN (SELECT ROWID FROM {table_name} ORDER BY ROWID DESC LIMIT -1 OFFSET {limit})")
    conn.commit()

def get_all_slack_message_ts():
    return conn.execute(f"select * from SLACK_MESSAGE_LOG")

def get_all_slack_message_from_discord():
    return conn.execute(f"select * from DISCORD_MESSAGE_LOG ORDER BY ROWID DESC LIMIT 20")

def get_old_reactions_for_message(slack_timestamp):
    return conn.execute(f"select reaction from SLACK_MESSAGE_LOG where SLACK_TIMESTAMP = '{slack_timestamp}'").fetchone()[0]

def get_old_reactions_for_message2(slack_timestamp):
    return conn.execute(f"select MESSAGE_TYPE from DISCORD_MESSAGE_LOG where SLACK_TIMESTAMP = '{slack_timestamp}'").fetchone()[0]

def update_old_reactions_for_message(slack_timestamp, reaction):
    conn.execute(f"update SLACK_MESSAGE_LOG set REACTION = '{reaction}' where SLACK_TIMESTAMP = '{slack_timestamp}'")
    conn.commit()

def update_old_reactions_for_message2(slack_timestamp, reaction):
    conn.execute(f"update DISCORD_MESSAGE_LOG set MESSAGE_TYPE = '{reaction}' where SLACK_TIMESTAMP = '{slack_timestamp}'")
    conn.commit()

def get_timestamp_from_slack_message_log(message_id):
    try:
        return conn.execute(f"select SLACK_TIMESTAMP from SLACK_MESSAGE_LOG where MESSAGE_ID='{message_id}'").fetchone()[0]
    except Exception as _:
        return "0"



