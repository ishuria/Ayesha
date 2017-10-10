#coding=utf-8
import db_config
import MySQLdb as mdb


def db_connect():
    """Get connections from data base.

    Retrieves connection and cursor object.

    Args:
        None

    Returns:
        a connection object and a cursor object.

    Raises:
        None
    """
    conn = mdb.connect(host=db_config.mysql_ip, port=db_config.mysql_port,
    	user=db_config.mysql_user,passwd=db_config.mysql_pass,
    	db=db_config.mysql_db,charset='utf8')
    cursor = conn.cursor()
    return conn,cursor

def db_close(conn,cursor):
    """Close data base connections.

    Args:
        conn: a connection object.
        cursor: a cursor object.

    Returns:
        None

    Raises:
        None
    """
    cursor.close()
    conn.close()

