"""Análisis de latencia y rendimiento TCP (sockets) vs gRPC.

Bloque 4 de GA-SUM-02 / PE-U1. Lee solo los CSV reales de data/ con el
formato de ACUERDOS_TECNICOS.md y genera estadísticas, gráficos y tablas LaTeX.

Uso, desde la raíz del repositorio:
    python analysis/analyze.py --input data/tcp_lotes data/grpc_lotes

Criterios:
- Se excluyen las filas con warmup=1 de todas las estadísticas.
- Los modos (sequential/concurrent) nunca se mezclan.
- Las estadísticas de RTT usan solo intentos con status=ok; los fallos se reportan aparte.
- Intervalo: IC 95 % t de Student sobre la media de RTT de cada corrida válida
  (unidad estadística = corrida, n = número de corridas).
- Rendimiento: completed / elapsed_s por corrida, desde runs.csv.
"""

from pathlib import Path
import argparse
import shutil
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "analysis" / "figures"
TABLES = ROOT / "analysis" / "tables"
DOCS_FIGURES = ROOT / "docs" / "figures"

LATENCY_COLS = ["run_id", "message_id", "mechanism", "payload_bytes", "mode",
                "warmup", "client_id", "rtt_ms", "status"]
RUNS_COLS = ["run_id", "mechanism", "payload_bytes", "mode", "warmup",
             "clients", "attempted", "completed", "failed", "elapsed_s"]
GROUP = ["mode", "mechanism", "payload_bytes"]
INT_COLS = {"payload_bytes", "runs", "n", "attempted", "failed"}
CONFIDENCE = 0.95
DPI = 300


def load_csv(path, columns):
    if not path.exists():
        sys.exit(f"Falta {path.relative_to(ROOT)}. No se generan resultados sin datos reales.")
    df = pd.read_csv(path)
    missing = [c for c in columns if c not in df.columns]
    if missing:
        sys.exit(f"{path.name}: faltan columnas {missing} (ver ACUERDOS_TECNICOS.md).")
    if df.empty:
        sys.exit(f"{path.name} no tiene filas.")
    return df[columns]


def ci_halfwidth(values):
    n = len(values)
    if n < 2:
        return float("nan")
    return stats.t.ppf((1 + CONFIDENCE) / 2, n - 1) * values.std(ddof=1) / n ** 0.5


def latency_summary(ok):
    rows = []
    for key, g in ok.groupby(GROUP):
        run_means = g.groupby("run_id")["rtt_ms"].mean()
        rows.append({
            **dict(zip(GROUP, key)),
            "runs": len(run_means),
            "n": len(g),
            "mean_ms": g["rtt_ms"].mean(),
            "median_ms": g["rtt_ms"].median(),
            "std_ms": g["rtt_ms"].std(ddof=1),
            "p95_ms": g["rtt_ms"].quantile(0.95),
            "ci95_ms": ci_halfwidth(run_means),
        })
    return pd.DataFrame(rows)


def throughput_summary(runs):
    runs = runs.assign(msg_s=runs["completed"] / runs["elapsed_s"])
    rows = []
    for key, g in runs.groupby(GROUP):
        rows.append({
            **dict(zip(GROUP, key)),
            "runs": len(g),
            "attempted": int(g["attempted"].sum()),
            "failed": int(g["failed"].sum()),
            "mean_msg_s": g["msg_s"].mean(),
            "std_msg_s": g["msg_s"].std(ddof=1),
            "ci95_msg_s": ci_halfwidth(g["msg_s"]),
        })
    return pd.DataFrame(rows)


def failure_summary(lat):
    return (lat.groupby(GROUP + ["status"]).size()
               .unstack("status", fill_value=0).reset_index())


def fmt(x):
    return "--" if pd.isna(x) else f"{x:.3f}"


def write_latex(df, path, columns, headers, caption, label):
    lines = [
        "% Generado por analysis/analyze.py. No editar a mano.",
        "\\begin{table}[htbp]", "\\centering", f"\\caption{{{caption}}}",
        f"\\label{{{label}}}", "\\resizebox{\\linewidth}{!}{%",
        f"\\begin{{tabular}}{{{'l' * 3 + 'r' * (len(columns) - 3)}}}",
        "\\toprule", " & ".join(headers) + " \\\\", "\\midrule",
    ]
    for _, r in df.iterrows():
        cells = [str(int(r[c])) if c in INT_COLS else str(r[c]) if c in GROUP else fmt(r[c])
                 for c in columns]
        lines.append(" & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}%", "}", "\\end{table}", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def boxplot(ok, path):
    modes = sorted(ok["mode"].unique())
    fig, axes = plt.subplots(1, len(modes), figsize=(6 * len(modes), 4.5), squeeze=False)
    for ax, mode in zip(axes[0], modes):
        sub = ok[ok["mode"] == mode]
        keys = sorted(sub.groupby(["payload_bytes", "mechanism"]).groups)
        data = [sub[(sub["payload_bytes"] == b) & (sub["mechanism"] == m)]["rtt_ms"] for b, m in keys]
        ax.boxplot(data, tick_labels=[f"{m}\n{b} B" for b, m in keys])
        ax.set_title(f"RTT ({mode})")
        ax.set_ylabel("RTT (ms)")
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def bars(summary, value, err, ylabel, title, path):
    modes = sorted(summary["mode"].unique())
    fig, axes = plt.subplots(1, len(modes), figsize=(6 * len(modes), 4.5), squeeze=False)
    for ax, mode in zip(axes[0], modes):
        sub = summary[summary["mode"] == mode].sort_values(["payload_bytes", "mechanism"])
        labels = [f"{m}\n{b} B" for m, b in zip(sub["mechanism"], sub["payload_bytes"])]
        ax.bar(labels, sub[value], yerr=sub[err], capsize=5)
        ax.set_title(f"{title} ({mode})")
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.3)
    fig.text(0.5, 0.01, "Barras de error: IC 95 % t de Student entre corridas", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def load_dirs(dirs):
    lat, runs = [], []
    for d in dirs:
        d = d if d.is_absolute() else ROOT / d
        if not d.is_dir():
            sys.exit(f"No existe la carpeta {d}.")
        lat += [load_csv(f, LATENCY_COLS) for f in sorted(d.glob("latency_*.csv"))]
        runs.append(load_csv(d / "runs.csv", RUNS_COLS))
    if not lat:
        sys.exit("Ninguna carpeta contiene latency_*.csv.")
    return pd.concat(lat, ignore_index=True), pd.concat(runs, ignore_index=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, nargs="+", required=True,
                        help="Carpetas de corridas finales, p. ej. data/tcp_lotes data/grpc_lotes")
    args = parser.parse_args()
    lat, runs = load_dirs(args.input)

    lat = lat[lat["warmup"] == 0]
    runs = runs[runs["warmup"] == 0]
    if lat.empty or runs.empty:
        sys.exit("No hay corridas válidas (warmup=0) para analizar.")
    ok = lat[lat["status"] == "ok"].dropna(subset=["rtt_ms"])

    for d in (FIGURES, TABLES, DOCS_FIGURES):
        d.mkdir(parents=True, exist_ok=True)

    lat_sum = latency_summary(ok)
    thr_sum = throughput_summary(runs)
    fail_sum = failure_summary(lat)

    lat_sum.to_csv(TABLES / "latency_summary.csv", index=False)
    thr_sum.to_csv(TABLES / "throughput_summary.csv", index=False)
    fail_sum.to_csv(TABLES / "failures_summary.csv", index=False)

    write_latex(lat_sum, TABLES / "summary.tex",
                GROUP + ["runs", "n", "mean_ms", "median_ms", "std_ms", "p95_ms", "ci95_ms"],
                ["Modo", "Mecanismo", "Bytes", "Corridas", "n", "Media (ms)", "Mediana (ms)",
                 "Desv. (ms)", "p95 (ms)", "IC95 $\\pm$ (ms)"],
                "Latencia RTT por modo, mecanismo y tamaño (sin calentamiento, solo status=ok)",
                "tab:latencia")
    write_latex(thr_sum, TABLES / "throughput.tex",
                GROUP + ["runs", "attempted", "failed", "mean_msg_s", "std_msg_s", "ci95_msg_s"],
                ["Modo", "Mecanismo", "Bytes", "Corridas", "Intentos", "Fallos",
                 "Media (msg/s)", "Desv. (msg/s)", "IC95 $\\pm$ (msg/s)"],
                "Rendimiento (completed/elapsed\\_s) por corrida válida", "tab:rendimiento")

    boxplot(ok, FIGURES / "boxplot.png")
    shutil.copy2(FIGURES / "boxplot.png", DOCS_FIGURES / "boxplot.png")
    bars(lat_sum, "mean_ms", "ci95_ms", "RTT medio (ms)", "Latencia", FIGURES / "latency_bars.png")
    bars(thr_sum, "mean_msg_s", "ci95_msg_s", "Mensajes/s", "Rendimiento", FIGURES / "throughput_bars.png")

    print(lat_sum.to_string(index=False))
    print(thr_sum.to_string(index=False))
    print(f"Fallos (sin calentamiento):\n{fail_sum.to_string(index=False)}")
    print(f"Salidas en {FIGURES.relative_to(ROOT)}, {TABLES.relative_to(ROOT)} y docs/figures/boxplot.png")


if __name__ == "__main__":
    main()
