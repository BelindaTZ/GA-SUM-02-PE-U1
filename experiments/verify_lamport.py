"""Comprueba el orden de Lamport en uno o más CSV de eventos."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

KEY_FIELDS = ("run_id", "mechanism", "message_id", "message_kind")
REQUIRED_FIELDS = {*KEY_FIELDS, "event_type", "node", "peer", "lamport"}


def verify(path):
    pairs = defaultdict(dict)
    issues = []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = csv.DictReader(stream)
        missing = REQUIRED_FIELDS.difference(rows.fieldnames or ())
        if missing:
            return 0, 0, ["Columnas ausentes: " + ", ".join(sorted(missing))]
        for line, row in enumerate(rows, start=2):
            if any(not row[field] for field in REQUIRED_FIELDS):
                issues.append(f"Línea {line}: faltan valores obligatorios.")
                continue
            key = tuple(row[field] for field in KEY_FIELDS)
            event = row["event_type"]
            if event not in ("send", "receive") or event in pairs[key]:
                issues.append(f"Línea {line}: evento desconocido o duplicado: {event}.")
                continue
            try:
                clock = int(row["lamport"])
                if clock < 0:
                    raise ValueError
            except ValueError:
                issues.append(f"Línea {line}: marca de Lamport inválida.")
                continue
            pairs[key][event] = (row["node"], row["peer"], clock)

    valid = 0
    for key, events in pairs.items():
        label = " / ".join(key)
        if set(events) != {"send", "receive"}:
            issues.append(f"{label}: par incompleto.")
            continue
        sender, destination, sent = events["send"]
        receiver, source, received = events["receive"]
        if (sender, destination) != (source, receiver):
            issues.append(f"{label}: nodos y dirección no coinciden.")
        elif received <= sent:
            issues.append(f"{label}: recepción {received} <= envío {sent}.")
        else:
            valid += 1
    if not pairs and not issues:
        issues.append("El CSV no contiene eventos.")
    return valid, len(pairs), issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="+", type=Path, help="Archivos de eventos")
    args = parser.parse_args()
    failed = False
    for path in args.csv:
        try:
            valid, total, issues = verify(path)
        except (OSError, UnicodeError, csv.Error) as error:
            valid, total, issues = 0, 0, [str(error)]
        print(f"{path}: {valid}/{total} pares válidos, {len(issues)} incidencias.")
        for issue in issues:
            print(f"  - {issue}")
        failed |= bool(issues)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
