import sqlite3

db_path="tasks.db"
def get_conn():
    conn=sqlite3.connect(db_path)
    conn.row_factory=sqlite3.Row
    return conn

def init_db():
    conn=get_conn()
    try:
        cur=conn.cursor()
        cur.execute(
            """create table if not exists tasks(
                    id integer primary key autoincrement,
                    title text not null,
                    category text not null,
                    estimated_minutes int not null,
                    is_done int not null default 0
                    )"""
            )
        conn.commit()
    finally:
        conn.close()
