from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional

app = FastAPI()

tasks = []
task_id_counter = 1

class Task(BaseModel):
    title: str
    description: str
    deadline: str

    @validator('deadline')
    def validate_deadline(cls, value):
        try:
            datetime.strptime(value, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Неправильный формат дедлайна. Используйте DD-MM-YYYY.")
        return value

class TaskResponse(Task):
    id: int

@app.post("/tasks", response_model=TaskResponse)
def add_task(task: Task):
    global task_id_counter
    task_data = task.dict()
    task_data["id"] = task_id_counter
    tasks.append(task_data)
    task_id_counter += 1
    return task_data

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks():
    sorted_tasks = sorted(tasks, key=lambda x: datetime.strptime(x["deadline"], "%d-%m-%Y"))
    return sorted_tasks

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    task_to_delete = None
    for task in tasks:
        if task["id"] == task_id:
            task_to_delete = task
            break
    if task_to_delete:
        tasks.remove(task_to_delete)
        return {"message": f"Задача с ID {task_id} удалена."}
    else:
        raise HTTPException(status_code=404, detail="Задача не найдена.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)