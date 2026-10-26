"""Especificaciones de la máquina donde se ejecutan los benchmarks.

Uso (desde la raíz del repo, con MongoDB corriendo):
    python scripts/specs_maquina.py [--usuario NOMBRE] [--uri mongodb://localhost:27017]

Escribe resultados/especificaciones_maquina_<usuario>.json y .md.
"""

import argparse
import getpass
import json
import os
import platform
import shutil
import socket
import subprocess
from datetime import datetime
from pathlib import Path

import numpy
import pandas
import pymongo

RESULTADOS = Path(__file__).resolve().parent.parent / "resultados"
GB = 1024 ** 3


def comando(*args):
    """Salida de un comando, o None si no existe o falla."""
    try:
        return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def sysctl(clave):
    return comando("sysctl", "-n", clave)


def cpu():
    sistema = platform.system()
    datos = {"modelo": platform.processor() or platform.machine(), "nucleos_totales": os.cpu_count(),
             "nucleos_rendimiento": None, "nucleos_eficiencia": None}
    if sistema == "Darwin":
        datos["modelo"] = sysctl("machdep.cpu.brand_string") or datos["modelo"]
        datos["nucleos_totales"] = int(sysctl("hw.ncpu") or datos["nucleos_totales"])
        # En Apple Silicon perflevel0 son los núcleos de rendimiento y perflevel1 los de eficiencia
        p, e = sysctl("hw.perflevel0.logicalcpu"), sysctl("hw.perflevel1.logicalcpu")
        datos["nucleos_rendimiento"] = int(p) if p else None
        datos["nucleos_eficiencia"] = int(e) if e else None
    elif sistema == "Linux":
        texto = Path("/proc/cpuinfo").read_text()
        modelo = next((l.split(":", 1)[1].strip() for l in texto.splitlines() if l.startswith("model name")), None)
        datos["modelo"] = modelo or datos["modelo"]
    return datos


def ram_gb():
    if platform.system() == "Darwin":
        return round(int(sysctl("hw.memsize")) / GB, 1)
    if platform.system() == "Linux":
        kb = next(int(l.split()[1]) for l in Path("/proc/meminfo").read_text().splitlines() if l.startswith("MemTotal"))
        return round(kb * 1024 / GB, 1)
    try:
        import psutil
        return round(psutil.virtual_memory().total / GB, 1)
    except ImportError:
        return None


def disco():
    uso = shutil.disk_usage(RESULTADOS.parent)
    datos = {"total_gb": round(uso.total / GB, 1), "libre_gb": round(uso.free / GB, 1), "tipo": None}
    if platform.system() == "Darwin":
        info = comando("diskutil", "info", "/") or ""
        campos = dict(l.strip().split(":", 1) for l in info.splitlines() if ":" in l)
        ssd = campos.get("Solid State", "").strip()
        datos["tipo"] = ("SSD" if ssd == "Yes" else "HDD" if ssd == "No" else None)
        datos["protocolo"] = campos.get("Protocol", "").strip() or None
        datos["sistema_archivos"] = campos.get("File System Personality", "").strip() or None
    elif platform.system() == "Linux":
        rot = comando("lsblk", "-dno", "ROTA")
        if rot:
            datos["tipo"] = "HDD" if rot.split()[0] == "1" else "SSD"
    return datos


def mongodb(uri):
    cliente = pymongo.MongoClient(uri, serverSelectionTimeoutMS=3000)
    estado = cliente.admin.command("serverStatus")
    cache = estado.get("wiredTiger", {}).get("cache", {}).get("maximum bytes configured")
    return {
        "version": estado["version"],
        "motor_almacenamiento": estado["storageEngine"]["name"],
        "cache_wiredtiger_max_gb": round(cache / GB, 2) if cache else None,
    }


def sistema_operativo():
    if platform.system() == "Darwin":
        return {"nombre": "macOS", "version": platform.mac_ver()[0], "kernel": platform.release()}
    return {"nombre": platform.system(), "version": platform.version(), "kernel": platform.release()}


def a_markdown(e):
    c, d, m = e["cpu"], e["disco"], e["mongodb"]
    nucleos = f"{c['nucleos_totales']}"
    if c["nucleos_rendimiento"] is not None:
        nucleos += f" ({c['nucleos_rendimiento']} de rendimiento + {c['nucleos_eficiencia']} de eficiencia)"
    filas = [
        ("Fecha", e["fecha"]),
        ("Máquina", e["maquina"]),
        ("Usuario", e["usuario"]),
        ("CPU", c["modelo"]),
        ("Núcleos", nucleos),
        ("RAM", f"{e['ram_gb']} GB"),
        ("Sistema operativo", f"{e['sistema_operativo']['nombre']} {e['sistema_operativo']['version']}"),
        ("Disco", f"{d['tipo'] or '?'}, {d['total_gb']} GB totales, {d['libre_gb']} GB libres"),
        ("MongoDB", f"{m['version']}, motor {m['motor_almacenamiento']}, caché WiredTiger máx. {m['cache_wiredtiger_max_gb']} GB"),
        ("Python", e["python"]["version"]),
        ("Librerías", ", ".join(f"{k} {v}" for k, v in e["python"].items() if k != "version")),
    ]
    return ("# Especificaciones de la máquina\n\nGenerado por `scripts/specs_maquina.py`.\n\n"
            "| Componente | Valor |\n| --- | --- |\n" + "\n".join(f"| {k} | {v} |" for k, v in filas) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--usuario", default=getpass.getuser())
    parser.add_argument("--uri", default="mongodb://localhost:27017")
    args = parser.parse_args()

    especificaciones = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "maquina": socket.gethostname(),
        "usuario": args.usuario,
        "cpu": cpu(),
        "ram_gb": ram_gb(),
        "sistema_operativo": sistema_operativo(),
        "disco": disco(),
        "mongodb": mongodb(args.uri),
        "python": {"version": platform.python_version(), "pymongo": pymongo.__version__,
                   "numpy": numpy.__version__, "pandas": pandas.__version__},
    }
    RESULTADOS.mkdir(exist_ok=True)
    base = RESULTADOS / f"especificaciones_maquina_{args.usuario}"
    base.with_suffix(".json").write_text(json.dumps(especificaciones, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.with_suffix(".md").write_text(a_markdown(especificaciones), encoding="utf-8")
    print(a_markdown(especificaciones))


if __name__ == "__main__":
    main()
