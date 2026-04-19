# original version from
# https://hy-tikawe.github.io/materiaali/osa2/#tietokantamoduuli
import sqlite3
from contextlib import contextmanager

from flask import g

def get_connection():
    con=sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory=sqlite3.Row
    return con

def execute(sql, params=[]):
    con=get_connection()
    result=con.execute(sql, params)
    con.commit()
    g.last_insert_id=result.lastrowid
    con.close()

def last_insert_id():
    return g.last_insert_id

@contextmanager
def get_cursor():
    con=get_connection()
    cur=con.cursor()
    try:
        yield cur
        con.commit()
    except Exception as e:
        cur.close()
        raise e
    finally:
        cur.close()
        con.close()

def query(sql, params=[]):
    con=get_connection()
    result=con.execute(sql, params).fetchall()
    con.close()
    return result
