from typing import Optional, Callable
import time
from .task import Task, TaskStatus

class Timer:
    def __init__(self):
        self._current_task: Optional[Task] = None
        self._running = False
        self._on_tick: Optional[Callable[[int], None]] = None
        self._on_finish: Optional[Callable[[Task], None]] = None

    def set_callbacks(self, on_tick=None, on_finish=None):
        self._on_tick = on_tick
        self._on_finish = on_finish

    def start_task(self, task: Task):
        """Inicia una tarea estableciendo su estado como RUNNING y marcando el temporizador como en funcionamiento."""
        self._current_task = task
        self._current_task.status = TaskStatus.RUNNING
        self._running = True

    def pause(self):
        """Pausa la tarea actual, cambiando su estado a PAUSED."""
        if self._current_task and self._running:
            self._running = False
            self._current_task.status = TaskStatus.PAUSED

    def resume(self):
        """Reanuda la tarea pausada, cambiando su estado a RUNNING."""
        if self._current_task and self._current_task.status == TaskStatus.PAUSED:
            self._running = True
            self._current_task.status = TaskStatus.RUNNING

    def stop(self):
        """Detiene la tarea actual, cambiando su estado a STOPPED. Reinicia el tiempo restante."""
        if self._current_task:
            self._running = False
            self._current_task.status = TaskStatus.STOPPED
            # Reiniciar el tiempo restante. Según los requisitos del usuario, la tarea debe "Reiniciarse si se cancela la tarea".
            self._current_task.remaining_seconds = self._current_task.total_seconds
            self._current_task = None

    def tick(self):
        """Debería ser llamado cada segundo desde un bucle temporizador externo."""
        if self._running and self._current_task:
            if self._current_task.remaining_seconds > 0:
                self._current_task.remaining_seconds -= 1
                if self._on_tick:
                    self._on_tick(self._current_task.remaining_seconds)
            
            if self._current_task.remaining_seconds <= 0:
                self._complete_task()

    def _complete_task(self):
        """Marca la tarea actual como completada y llama al callback de finalización si está presente."""
        self._running = False
        if self._current_task:
            self._current_task.status = TaskStatus.COMPLETED
            if self._on_finish:
                self._on_finish(self._current_task)
            self._current_task = None

    @property
    def is_running(self):
        """Devuelve True si el temporizador está en funcionamiento, False de lo contrario."""
        return self._running
