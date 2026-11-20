# Ejecución experimental pendiente

Crear run_experiments.py y un plan común de intercambios/configuración.
Distinguir prueba de 20 intercambios, RTT secuencial y concurrencia.
Identificar corridas, calentamiento, mecanismo, bytes y clientes activos; usar la matriz del PLAN_ACTIVIDAD.md.
No escribir registros de ejemplo en data: solo ejecuciones reales.
## Lotes TCP

Desde la raíz del repositorio, usa una carpeta de salida nueva:

```text
python -m experiments.run_tcp_batches --output data/tcp_lotes
```

Ejecuta una corrida de calentamiento y cinco medidas por tamaño y modo.
Cada corrida repite el plan de 20 intercambios cinco veces. En modo
concurrente, los tres emisores empiezan con una barrera compartida y
reparten los 100 intentos en 35, 35 y 30, según el plan. El CSV de corridas
registra el tiempo de pared de cada lote y los fallos.

Los tres nodos son hilos en un proceso local. Para comparar TCP y gRPC,
usar la misma topología, plan, preparación de conexiones y medición de
tiempo en ambos mecanismos.
