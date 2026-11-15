from pydantic import BaseModel, Field
from typing import Literal
from fastapi import FastAPI, HTTPException
task_db=[]

class TaskCreate(BaseModel):
    title:str=Field(..., min_length=1, max_length=50, description="标题")
    category:Literal["ai","invest","health"]=Field(..., description="分类")
    estimated_minutes:int=Field(..., gt=0, description="统计时间")

class TaskOut(TaskCreate):
    id:int
    is_done:bool=Field(default=False)

app=FastAPI()
@app.post("/tasks",status_code=201)
def create_task(task: TaskCreate):
    new_task=TaskOut(
        id=len(task_db)+1,
        title=task.title,
        category=task.category,
        estimated_minutes=task.estimated_minutes,
        is_done=False
    )
    task_db.append(new_task)
    return new_task

@app.get("/tasks")
def get_task(category: Literal["ai", "invest", "health"] | None = None):
    if not category: return task_db
    result=[]
    for task in task_db:
        if task.category==category: result.append(task)
    return result

@app.patch("/tasks/{id}/done")
def alter_task(id:int):
    for task in task_db:
        if task.id==id:
            task.is_done=True
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{id}")
def delete_task(id:int):
    for task in task_db:
        if task.id==id: task_db.remove(task)
        return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")