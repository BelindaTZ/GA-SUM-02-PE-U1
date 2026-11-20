"""Exporta los eventos de una corrida CSV a JSON sin modificar el original."""

import argparse
import csv
import json
from pathlib import Path

from src.common.event_log import EVENT_COLUMNS


def export_run(source, run_id, destination):
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != EVENT_COLUMNS:
            raise ValueError("Las columnas no coinciden con el esquema de eventos.")
        events = []
        for line, row in enumerate(reader, 2):
            if row["run_id"] != run_id:
                continue
            if None in row or any(value in (None, "") for value in row.values()):
                raise ValueError(f"Fila {line}: evento incompleto.")
            row["lamport"] = int(row["lamport"])
            if row["lamport"] < 1:
                raise ValueError(f"Fila {line}: marca Lamport fuera de rango.")
            events.append(row)
    if not events:
        raise ValueError(f"No se encontraron eventos para la corrida {run_id}.")
    payload = json.dumps(events, ensure_ascii=False, indent=2)
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(payload + "\n")
    return len(events)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("run_id")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        count = export_run(args.source, args.run_id, args.output)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(1, f"{error}\n")
    print(f"{count} eventos exportados a {args.output}.")


if __name__ == "__main__":
    main()
