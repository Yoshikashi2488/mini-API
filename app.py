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

#Мы храним задачи в виде списка словарей, где каждая задача содержит поля `id`, `title`, `description` и `deadline`.
#Уникальные ID генерируются с помощью глобальной переменной `task_id_counter`, а сортировка задач по дедлайну выполняется через
#преобразование строки дедлайна в объект `datetime` с использованием функции `sorted`. Для валидации данных, включая проверку формата дедлайна "DD-MM-YYYY",
#используется Pydantic. API поддерживает три маршрута: POST `/tasks` для добавления новой задачи, GET `/tasks` для получения отсортированного списка задач и
#DELETE `/tasks/{task_id}` для удаления задачи по её ID.

#Для улучшения проекта для продакшена можно заменить хранение задач в памяти на базу данных (например, PostgreSQL или SQLite),
#чтобы обеспечить сохранность данных при перезапуске сервера. Добавление аутентификации (например, через OAuth2 или JWT)
#ограничит доступ к API и повысит безопасность. Логирование поможет отслеживать ошибки и действия пользователей, а написание unit-тестов и
#интеграционных тестов обеспечит стабильность работы API. Автоматическая документация через Swagger UI (встроенный в FastAPI)
#упростит использование API, а контейнеризация с помощью Docker облегчит развёртывание. Для масштабируемости стоит использовать асинхронные
#вызовы и балансировку нагрузки.