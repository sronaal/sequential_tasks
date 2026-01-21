import json
import os
from typing import List, Dict, Any
from ..core.task import Task, TaskStatus

DATA_FILE = "tasks_data.json"

def save_tasks(tasks: List[Task], filepath: str = DATA_FILE):
    # Preparamos los datos de las tareas para ser guardados en formato JSON
    data = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "name": task.name,
            "duration_minutes": task.duration_minutes,
            "status": task.status.value,
            "remaining_seconds": task.remaining_seconds
        }
        data.append(task_dict)
    
    # Intentamos guardar los datos en el archivo especificado
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error al guardar las tareas: {e}")

def load_tasks(filepath: str = DATA_FILE) -> List[Task]:
    # Verificamos si el archivo existe, si no, retornamos una lista vacía
    if not os.path.exists(filepath):
        return []
    
    tasks = []
    # Intentamos cargar los datos de las tareas desde el archivo
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Procesamos cada elemento del archivo JSON
        for item in data:
            try:
                # Creamos una tarea nueva a partir de los datos
                task = Task(
                    name=item["name"],
                    duration_minutes=item["duration_minutes"],
                    id=item.get("id"),
                    status=TaskStatus(item["status"]),
                    remaining_seconds=item.get("remaining_seconds")
                )
                tasks.append(task)
            except Exception as e:
                print(f"Omitiendo datos de tarea inválidos: {item}, error: {e}")
                
    except Exception as e:
        print(f"Error al cargar las tareas: {e}")
        return []
        
    return tasks
