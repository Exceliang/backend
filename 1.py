from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import sqlite3

app = FastAPI()
def get_conn():
    conn=sqlite3.connect("tasks.db")
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

init_db()

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=50, description="任务标题")
    category: Literal["ai", "invest", "health"] = Field(..., description="所属分类")
    estimated_minutes: int = Field(..., gt=0, description="预估耗时（分钟）")


class TaskOut(TaskCreate):
    id: int
    is_done: bool = Field(default=False)


@app.post("/tasks", status_code=201, response_model=TaskOut)
def create_task(task: TaskCreate):
    conn=get_conn()
    try:
        cur=conn.cursor()
        cur.execute(
            "insert into tasks(title, category, estimated_minutes, is_done) values (?,?,?,?)",
            (task.title,task.category,task.estimated_minutes,0)
        )
        conn.commit()
        new_id=cur.lastrowid
    finally:
        conn.close()

    return TaskOut(
        id=new_id,
        title=task.title,
        category=task.category,
        estimated_minutes=task.estimated_minutes,
        is_done=False,
    )


@app.get("/tasks", response_model=list[TaskOut])
def get_tasks(category: Literal["ai", "invest", "health"] | None = None):
    conn=get_conn()
    try:
        cur=conn.cursor()
        if not category:
            cur.execute(
                "select id, title, category, estimated_minutes, is_done from tasks"
            )
        else:
            cur.execute(
                "select id, title, category, estimated_minutes, is_done from tasks where category=(?)",
                (category,),
            )
        conn.commit()
        rows=cur.fetchall()
    finally:
        conn.close()

    return [
        TaskOut(
            id=row["id"],
            title=row["title"],
            category=row["category"],
            estimated_minutes=row["estimated_minutes"],
            is_done=bool(row["is_done"]),
        )
        for row in rows
    ]
    


@app.patch("/tasks/{task_id}/done", response_model=TaskOut)
def finish_task(task_id: int):
    conn=get_conn()
    try:
        cur=conn.cursor()
        cur.execute(
            "update tasks set is_done=1 where id=?"
            (task_id,),
        )
        conn.commit()
        if cur.rowcount==0:
            raise HTTPException(status_code=404, detail="Task not found")
        cur.execute(
            "select id, title, category, estimated_minutes, is_done from tasks where id=?"
            (task_id,),
        )
        row=cur.fetchone()
    finally:
        conn.close()

    return TaskOut(
        id=row["id"],
        title=row["title"],
        category=row["category"],
        estimated_minutes=row["estimated_minutes"],
        is_done=bool(row["is_done"]),
    )


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn=get_conn()
    try:
        cur=conn.cursor()
        cur.execute(
            "delete from tasks where id=?",
            (task_id,),
        )
        conn.commit()
        if cur.rowcount==0:
            raise HTTPException(status_code=404,detail="Task not found")
    finally:
        conn.close()

    return {"message":"Task deleted"}