from dataclasses import dataclass, field
from enum import Enum
import uuid
from typing import Optional

# Definición de los posibles estados de una tarea
class TaskStatus(Enum):
    PENDING = "pending"   # Tarea pendiente
    RUNNING = "running"   # Tarea en ejecución
    PAUSED = "paused"     # Tarea pausada
    COMPLETED = "completed" # Tarea completada
    STOPPED = "stopped"   # Tarea detenida

# Clase que representa una tarea
@dataclass
class Task:
    name: str                          # Nombre de la tarea
    duration_minutes: int              # Duración de la tarea en minutos
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Identificador único de la tarea
    status: TaskStatus = TaskStatus.PENDING  # Estado inicial de la tarea
    remaining_seconds: Optional[int] = None  # Segundos restantes para completar la tarea

    def __post_init__(self):
        # Inicializa remaining_seconds si es None
        if self.remaining_seconds is None:
            self.remaining_seconds = self.duration_minutes * 60

    @property
    def total_seconds(self) -> int:
        """Devuelve la duración total de la tarea en segundos."""
        return self.duration_minutes * 60

    @property
    def progress(self) -> float:
        """Devuelve el progreso de la tarea como un valor entre 0.0 y 1.0"""
        if self.total_seconds == 0:
            return 0.0
        return 1.0 - (self.remaining_seconds / self.total_seconds)
