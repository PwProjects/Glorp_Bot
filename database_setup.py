import sqlite3
import random

# Table creation
connection = sqlite3.connect("glorp.db")
cursor = connection.cursor()

cursor.execute("""DROP TABLE IF EXISTS user_bans""")
cursor.execute("""CREATE TABLE IF NOT EXISTS user_bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                glorp_id INTEGER NOT NULL)""")
'''
cursor.execute("""DROP TABLE IF EXISTS crafting""")
cursor.execute("""CREATE TABLE IF NOT EXISTS crafting (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                glorp_id INTEGER,
                requirements TEXT,
                rewards TEXT,
                notes TEXT,
                created DATETIME default (datetime('now', 'localtime')))"""
)

cursor.execute("""DROP TABLE IF EXISTS user_glorps""")
cursor.execute("""CREATE TABLE IF NOT EXISTS user_glorps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                glorp_id INTEGER,
                created DATETIME default (datetime('now', 'localtime')))"""
)

cursor.execute("""DROP TABLE IF EXISTS users""")
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                user_name TEXT NOT NULL,
                sac_points INT default 0,
                created DATETIME default (datetime('now', 'localtime')),
                last_spin DATETIME default (datetime('now', 'localtime')))"""
)

cursor.execute("""DROP TABLE IF EXISTS glorp_cards""")
cursor.execute("""CREATE TABLE IF NOT EXISTS glorp_cards (
                glorp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                stars INT NOT NULL,
                has_hat INT NOT NULL,
                spinnable INT NOT NULL,
                craftable INT NOT NULL,
                is_ingredient INT NOT NULL,
                can_sacrifice INT NOT NULL,
                can_gamble INT NOT NULL,
                spin_odds INT NOT NULL,
                gamble_odds REAL NOT NULL,
                perk INT NOT NULL,
                created DATETIME default (datetime('now', 'localtime')),
                last_updatd DATETIME default (datetime('now', 'localtime')))"""
)
'''

cursor.close()
connection.close()
