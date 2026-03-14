import time
import psutil
import pandas as pd # Se non l'hai, aggiungilo al toml

def benchmark_run(task_name, script_function, *args):
    start_time = time.perf_counter()
    start_mem = psutil.Process().memory_info().rss / (1024 * 1024) # MB
    
    try:
        # Esegui la funzione del task
        result = script_function(*args)
        
        end_time = time.perf_counter()
        end_mem = psutil.Process().memory_info().rss / (1024 * 1024)
        
        return {
            "Task": task_name,
            "Time (s)": round(end_time - start_time, 4),
            "Memory (MB)": round(end_mem - start_mem, 4),
            "Value": result.get("value", 0),
            "Feasible": result.get("feasible", True)
        }
    except Exception as e:
        return {"Task": task_name, "Error": str(e)}
