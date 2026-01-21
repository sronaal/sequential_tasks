from typing import List, Optional
from .task import Task, TaskStatus

class TaskQueue:
    def __init__(self):
        # Inicializa la cola de tareas
        self.tasks: List[Task] = []

    def add_task(self, name: str, duration_minutes: int) -> Task:
        # Agrega una nueva tarea a la cola
        task = Task(name=name, duration_minutes=duration_minutes)
        self.tasks.append(task)
        return task

    def remove_task(self, task_id: str):
        # Elimina una tarea de la cola por su ID
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_task(self, task_id: str) -> Optional[Task]:
        # Obtiene una tarea de la cola por su ID
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_next_pending_task(self) -> Optional[Task]:
        # Obtiene la siguiente tarea pendiente en la cola
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def get_all_tasks(self) -> List[Task]:
        # Devuelve todas las tareas en la cola
        return self.tasks
    
    def clear_completed(self):
        # Elimina todas las tareas completadas de la cola
        self.tasks = [t for t in self.tasks if t.status != TaskStatus.COMPLETED]
