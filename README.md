# sequential_tasks

**sequential_tasks** es una aplicación de escritorio desarrollada en **Python** para gestionar tareas de forma secuencial, asignando un tiempo específico a cada una.

El proyecto fue diseñado y desarrollado **Realizado con IA** como herramienta de asistencia durante el análisis, diseño y escritura del código.

---

## Descripción

La aplicación permite:

- Ingresar tareas con un tiempo de ejecución definido  
- Gestionar múltiples tareas en una lista de espera  
- Ejecutar las tareas una por una, iniciando el conteo del tiempo desde cero  
- Notificar cuando una tarea finaliza y cuando la siguiente está por comenzar  
- Controlar la ejecución mediante iniciar, pausar y esperar  

El objetivo es facilitar una mejor organización del tiempo y mantener el enfoque en una sola tarea a la vez.

---

## Tecnologías

- Python  
- Interfaz gráfica de escritorio  
- Temporizador interno para control de tiempo  

---

## Ejecución

### Windows

```bash
python -m venv venv
venv\Script\activate
```

### Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Instalación dependecias

```bash
pip install -r requirements.txt
```

### Ejecución desde terminal

```bash
python main.py
```
