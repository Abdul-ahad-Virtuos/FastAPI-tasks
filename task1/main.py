from fastapi import FastAPI, HTTPException, status
from typing import List
from datetime import datetime
from model import TaskCreate, TaskUpdate, TaskResponse, StatusEnum, PriorityEnum

# app = FastAPI(lifespan=Lifespan)
app = FastAPI()

tasks_db = {}
task_id_counter = 1

@app.post("/tasks")
async def create_task(task: TaskCreate):
    global task_id_counter
    task_data = task.dict()
    task_data["id"] = task_id_counter
    task_data["created_at"] = datetime.utcnow()
    tasks_db[task_id_counter] = task_data
    task_id_counter += 1
    return TaskResponse(**task_data)

@app.get("/tasks")
async def list_tasks():
    return [TaskResponse(**t) for t in tasks_db.values()]

@app.get("/tasks/{id}")
async def get_task(id: int):
    task = tasks_db.get(id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)

@app.put("/tasks/{id}")
async def update_task(id: int, update: TaskUpdate):
    task = tasks_db.get(id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = update.dict(exclude_unset=True)
    for k, v in update_data.items():
        task[k] = v
    tasks_db[id] = task
    return TaskResponse(**task)

@app.delete("/tasks/{id}")
async def delete_task(id: int):
    if id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[id]
    return None
