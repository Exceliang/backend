from database import init_db, get_conn
from schemas import TaskOut,TaskCreate, TaskParamRequest, Literal
from fastapi import FastAPI, HTTPException
from ai import parse_tasks_from_text

app = FastAPI()

@app.post("/tasks/parse", status_code=201, response_model=list[TaskOut])
def parse_and_create_tasks(req: TaskParamRequest):
    # 1. 先调大模型拆解自然语言，失败则报 502
    try:
        tasks = parse_tasks_from_text(req.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 解析失败: {e}")

    conn = get_conn()
    try:
        task_list = []
        cur = conn.cursor()
        for task in tasks:
            # 2. 注意参数元组必须在 execute 的括号内部
            cur.execute(
                "INSERT INTO tasks (title, category, estimated_minutes, is_done) VALUES (?, ?, ?, ?)",
                (task.title, task.category, task.estimated_minutes, 0),
            )
            new_id = cur.lastrowid
            # 3. 每插完一条，立刻组装 TaskOut 放进列表
            task_list.append(
                TaskOut(
                    id=new_id,
                    title=task.title,
                    category=task.category,
                    estimated_minutes=task.estimated_minutes,
                    is_done=False,
                )
            )
        # 4. 全部循环结束后，在外面统一提交一次事务
        conn.commit()
    finally:
        conn.close()

    return task_list

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
            "update tasks set is_done=1 where id=?",
            (task_id,),
        )
        conn.commit()
        if cur.rowcount==0:
            raise HTTPException(status_code=404, detail="Task not found")
        cur.execute(
            "select id, title, category, estimated_minutes, is_done from tasks where id=?",
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