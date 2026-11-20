"""Carga el plan de intercambios compartido por los mecanismos."""

import csv

from src.common.config import NODES


def load_plan(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["sequence", "sender", "receiver"]:
            raise ValueError("El plan debe tener las columnas sequence,sender,receiver.")

        exchanges = []
        for sequence, row in enumerate(reader, start=1):
            sender, receiver = row["sender"], row["receiver"]
            if None in row or row["sequence"] != str(sequence):
                raise ValueError(f"Fila {sequence}: la secuencia debe comenzar en 1 y ser continua.")
            if sender not in NODES or receiver not in NODES or sender == receiver:
                raise ValueError(f"Fila {sequence}: origen o destino inválido.")
            exchanges.append((sequence, sender, receiver))

    if not exchanges:
        raise ValueError("El plan no tiene intercambios.")
    return exchanges
