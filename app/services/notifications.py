from plyer import notification
import threading

def send_notification(title: str, message: str, app_name: str = "Tareas Secuenciales"):
    """
    Envía una notificación de escritorio. 
    Se ejecuta en un hilo separado para evitar bloquear la interfaz de usuario si el sistema de notificaciones es lento.
    """
    def _notify():
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=app_name,
                timeout=10
            )
        except Exception as e:
            print(f"Error al enviar la notificación: {e}")

    threading.Thread(target=_notify, daemon=True).start()
