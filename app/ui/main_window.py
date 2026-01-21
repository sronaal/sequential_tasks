import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QLineEdit, QSpinBox, QMessageBox, QSystemTrayIcon, QMenu,
    QStyle
)
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QIcon, QAction

from ..core.task_queue import TaskQueue
from ..core.task import Task, TaskStatus
from ..core.timer import Timer
from ..services.notifications import send_notification
from ..services.sound_service import SoundService
from ..storage.persistence import save_tasks, load_tasks

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus Task Manager")
        self.resize(400, 600)
        
        # Componentes principales
        self.task_queue = TaskQueue()
        self.timer = Timer()  # Temporizador de lógica
        self.sound_service = SoundService()
        
        # Cargar tareas
        loaded_tasks = load_tasks()
        self.task_queue.tasks = loaded_tasks
        
        # Callbacks para el temporizador de lógica
        self.timer.set_callbacks(
            on_tick=self.update_timer_display,
            on_finish=self.on_task_finish
        )
        
        # Temporizador Qt para impulsar el tick del temporizador de lógica
        self.qt_timer = QTimer()
        self.qt_timer.timeout.connect(self.timer.tick)
        self.qt_timer.start(1000) # Intervalo de 1 segundo

        # Configuración de la interfaz de usuario
        self.setup_ui()
        self.refresh_task_list()
        self.setup_tray()
        
        # Check if there was a running task saved (persistence didn't save running state perfectly in first pass, 
        # so we'll just reset running ones to pending/paused or handle it later. For now, let's assume restart calls for pause.)
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Sección de Tarea Actual ---
        self.lbl_current_task = QLabel("Sin tarea activa")
        self.lbl_current_task.setAlignment(Qt.AlignCenter)
        self.lbl_current_task.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 5px;")
        
        self.lbl_timer = QLabel("00:00:00")
        self.lbl_timer.setAlignment(Qt.AlignCenter)
        self.lbl_timer.setStyleSheet("font-size: 32px; font-family: monospace; color: #333;")
        
        main_layout.addWidget(self.lbl_current_task)
        main_layout.addWidget(self.lbl_timer)
        
        # --- Controles ---
        controls_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶")
        self.btn_start.setToolTip("Iniciar/Reanudar")
        self.btn_start.clicked.connect(self.start_current_task)
        
        self.btn_pause = QPushButton("⏸")
        self.btn_pause.setToolTip("Pausar")
        self.btn_pause.clicked.connect(self.pause_task)
        
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setToolTip("Detener/Reiniciar")
        self.btn_stop.clicked.connect(self.stop_task)
        
        self.btn_skip = QPushButton("⏭")
        self.btn_skip.setToolTip("Saltar/Siguiente")
        self.btn_skip.clicked.connect(self.skip_task)
        
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.btn_skip)
        
        main_layout.addLayout(controls_layout)
        
        # --- Sección de Agregar Tarea ---
        add_layout = QHBoxLayout()
        self.input_task_name = QLineEdit()
        self.input_task_name.setPlaceholderText("Nombre de la tarea...")
        
        self.spin_minutes = QSpinBox()
        self.spin_minutes.setRange(1, 480) # De 1 minuto a 8 horas
        self.spin_minutes.setValue(25) # Valor por defecto Pomodoro
        self.spin_minutes.setSuffix(" min")
        
        btn_add = QPushButton("+")
        btn_add.clicked.connect(self.add_task)
        
        add_layout.addWidget(self.input_task_name)
        add_layout.addWidget(self.spin_minutes)
        add_layout.addWidget(btn_add)
        
        main_layout.addLayout(add_layout)
        
        # --- Lista de Tareas ---
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)
        
        # --- Estilo ---
        # El estilo minimalista se puede mejorar más adelante con qss
        
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # Usar un icono estándar por ahora, normalmente se cargaría desde los activos
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon)) 
        
        tray_menu = QMenu()
        action_show = QAction("Mostrar", self)
        action_show.triggered.connect(self.show)
        
        action_quit = QAction("Salir", self)
        action_quit.triggered.connect(self.quit_app)
        
        tray_menu.addAction(action_show)
        tray_menu.addSeparator()
        tray_menu.addAction(action_quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def update_timer_display(self, remaining_seconds):
        hours = remaining_seconds // 3600
        minutes = (remaining_seconds % 3600) // 60
        seconds = remaining_seconds % 60
        self.lbl_timer.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
        
    def add_task(self):
        name = self.input_task_name.text().strip()
        minutes = self.spin_minutes.value()
        if not name:
            return
        
        self.task_queue.add_task(name, minutes)
        save_tasks(self.task_queue.get_all_tasks())
        self.input_task_name.clear()
        self.refresh_task_list()
        
    def refresh_task_list(self):
        self.list_widget.clear()
        tasks = self.task_queue.get_all_tasks()
        
        # Filtrar completadas si se desea, o mostrarlas tachadas.
        # Por ahora mostrar todas pero separar tareas pendientes de completadas visualmente es mejor.
        # Mostrar todas para el historial, ¿o solo pendientes/en ejecución?
        # El usuario pidió "Lista de tareas pendientes", e "Historial" es extra.
        # Mostrar todas pero marcar las completadas.
        
        for task in tasks:
            if task.status == TaskStatus.COMPLETED:
                display_text = f"✔ {task.name} ({task.duration_minutes}m)"
            elif task.status == TaskStatus.RUNNING:
                display_text = f"▶ {task.name} ({task.duration_minutes}m)"
            elif task.status == TaskStatus.PAUSED:
                display_text = f"⏸ {task.name} ({task.duration_minutes}m)"
            else:
                display_text = f"{task.name} ({task.duration_minutes}m)"
                
            item = QListWidgetItem(display_text)
            self.list_widget.addItem(item)

    def start_current_task(self):
        if self.timer.is_running:
            return # Ya está en ejecución
            
        # Si el temporizador tiene una tarea pausada, reanúdala
        if self.timer._current_task and self.timer._current_task.status == TaskStatus.PAUSED:
            self.timer.resume()
            self.refresh_task_list()
            return
            
        # Si no, selecciona la siguiente pendiente
        next_task = self.task_queue.get_next_pending_task()
        if next_task:
            self.timer.start_task(next_task)
            self.sound_service.play_start_sound()
            self.lbl_current_task.setText(next_task.name)
            self.refresh_task_list()
        else:
            QMessageBox.information(self, "Información", "¡No hay tareas pendientes!")

    def pause_task(self):
        self.timer.pause()
        self.refresh_task_list()

    def stop_task(self):
        self.timer.stop()
        self.lbl_current_task.setText("Stopped")
        self.lbl_timer.setText("00:00:00")
        self.refresh_task_list()

    def skip_task(self):
        # Detener la actual, ¿marcar como omitida? ¿O solo detener e iniciar la siguiente?
        # Por ahora, simplemente detener y el usuario puede iniciar la siguiente manualmente o iniciamos automáticamente.
        self.stop_task()
        # Podría auto-seleccionar la siguiente
        
    def on_task_finish(self, task: Task):
        self.refresh_task_list()
        self.lbl_current_task.setText("¡Tarea Completada!")
        self.sound_service.play_finish_sound()
        send_notification("Tarea Completada", f"¡{task.name} ha finalizado!")
        save_tasks(self.task_queue.get_all_tasks())
        
        # Verificar lógica de la siguiente tarea
        next_task = self.task_queue.get_next_pending_task()
        if next_task:
            self.tray_icon.showMessage("Tarea en Cola", f"Siguiente: {next_task.name}", QSystemTrayIcon.Information, 5000)
            # ¿Lógica de auto-inicio? "Iniciar automáticamente ... tras confirmación o retardo"
            # Por simplicidad ahora, esperemos al usuario o tal vez auto-iniciar después de 5 seg?
            # Solo notificar por ahora.
        else:
            self.tray_icon.showMessage("Todo Hecho", "No hay más tareas en la cola.", QSystemTrayIcon.Information, 5000)

    def quit_app(self):
        save_tasks(self.task_queue.get_all_tasks())
        sys.exit()

    def closeEvent(self, event):
        # Minimizar a bandeja en lugar de cerrar
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Ejecutándose en Segundo Plano", 
            "La aplicación sigue ejecutándose en la bandeja del sistema.",
            QSystemTrayIcon.Information,
            2000
        )
