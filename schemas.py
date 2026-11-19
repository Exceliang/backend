from typing import Literal
from pydantic import BaseModel,Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=50, description="任务标题")
    category: Literal["ai", "invest", "health"] = Field(..., description="所属分类")
    estimated_minutes: int = Field(..., gt=0, description="预估耗时（分钟）")


class TaskOut(TaskCreate):
    id: int
    is_done: bool = Field(default=False)

class TaskParamRequest(BaseModel):
    text:str=Field(...,min_length=1,description="接收文本")