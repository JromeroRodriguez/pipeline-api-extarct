import copy
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


BASE_DIRECTORY = Path(__file__).resolve().parent.parent
FRONTEND_DIRECTORY = BASE_DIRECTORY / "frontend" / "dist"
PORT = int(os.getenv("PORT", "8000"))

STAGES = [
    {
        "key": "extract",
        "label": "Extracción",
        "marker": "EXTRACT",
        "running": "Obteniendo datos meteorológicos de Open-Meteo...",
        "done": "Datos extraídos de Open-Meteo",
    },
    {
        "key": "transform",
        "label": "Transformación",
        "marker": "TRANSFORM",
        "running": "Convirtiendo los datos en registros estructurados...",
        "done": "Datos transformados correctamente",
    },
    {
        "key": "validate",
        "label": "Validación",
        "marker": "VALIDATE",
        "running": "Comprobando la calidad y estructura de los datos...",
        "done": "Datos validados correctamente",
    },
    {
        "key": "analyze",
        "label": "Análisis",
        "marker": "ANALYZE",
        "running": "Calculando estadísticas por ciudad...",
        "done": "Estadísticas calculadas",
    },
    {
        "key": "load",
        "label": "Carga",
        "marker": "LOAD",
        "running": "Guardando resultados en CSV y PostgreSQL...",
        "done": "Resultados guardados en CSV y PostgreSQL",
    },
]

STAGE_INDEX = {stage["marker"]: index for index, stage in enumerate(STAGES)}
STATE_LOCK = threading.Lock()


def _initial_state():
    return {
        "status": "idle",
        "errorMessage": None,
        "startedAt": None,
        "elapsed": 0,
        "currentStage": -1,
        "stageProgress": 0,
        "stages": [
            {
                "key": stage["key"],
                "label": stage["label"],
                "status": "pending",
                "progress": 0,
                "description": "En espera",
                "meta": None,
            }
            for stage in STAGES
        ],
        "stats": {
            "records": 0,
            "cities": 0,
            "executionTime": "0.0s",
            "quality": None,
        },
        "logs": [],
    }


STATE = _initial_state()


def _add_log(message):
    message = message.strip()
    if not message:
        return

    upper_message = message.upper()
    if "ERROR" in upper_message or message.startswith("Error:"):
        level = "ERROR"
    elif "WARNING" in upper_message or "OMITIRÁ" in upper_message:
        level = "WARNING"
    elif any(word in upper_message for word in ("COMPLETADO", "EXITOSA", "GUARDADOS")):
        level = "SUCCESS"
    else:
        level = "INFO"

    STATE["logs"].append(
        {
            "id": len(STATE["logs"]),
            "time": datetime.now().astimezone().strftime("%H:%M:%S"),
            "level": level,
            "message": message,
        }
    )


def _handle_output(line):
    line = line.strip()
    if not line:
        return

    marker = re.match(r"\[\d+/5\]\s+(EXTRACT|TRANSFORM|VALIDATE|ANALYZE|LOAD)", line)
    with STATE_LOCK:
        if marker:
            stage_index = STAGE_INDEX[marker.group(1)]
            for index in range(stage_index):
                STATE["stages"][index].update(
                    status="completed",
                    progress=100,
                    description=STAGES[index]["done"],
                )

            stage = STAGES[stage_index]
            STATE["currentStage"] = stage_index
            STATE["stageProgress"] = round(stage_index / len(STAGES) * 100)
            STATE["stages"][stage_index].update(
                status="running",
                progress=0,
                description=stage["running"],
            )
            _add_log(f"Etapa {stage_index + 1}/5: {stage['label']}")
            return

        records = re.search(r"(?:Registros horarios|Registros procesados):\s*(\d+)", line)
        if records:
            STATE["stats"]["records"] = int(records.group(1))

        cities = re.search(r"Ciudades analizadas:\s*(\d+)", line)
        if cities:
            STATE["stats"]["cities"] = int(cities.group(1))

        _add_log(line)


def _run_pipeline():
    started = datetime.now().timestamp()
    try:
        process = subprocess.Popen(
            [sys.executable, "-u", "-m", "src.main"],
            cwd=BASE_DIRECTORY,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        with process:
            for line in process.stdout:
                _handle_output(line)
            return_code = process.wait()
    except Exception as error:
        return_code = 1
        with STATE_LOCK:
            _add_log(f"No se pudo ejecutar el pipeline: {error}")

    elapsed = max(0, datetime.now().timestamp() - started)
    with STATE_LOCK:
        STATE["elapsed"] = round(elapsed * 1000)
        STATE["stats"]["executionTime"] = f"{elapsed:.1f}s"

        if return_code == 0:
            for index, stage in enumerate(STAGES):
                STATE["stages"][index].update(
                    status="completed",
                    progress=100,
                    description=stage["done"],
                )
            STATE["status"] = "completed"
            STATE["currentStage"] = len(STAGES) - 1
            STATE["stageProgress"] = 100
            _add_log(f"Pipeline completado en {elapsed:.1f}s")
        else:
            stage_index = STATE["currentStage"]
            if stage_index >= 0:
                STATE["stages"][stage_index].update(
                    status="error",
                    description="La etapa terminó con un error",
                )
            STATE["status"] = "error"
            STATE["errorMessage"] = "El pipeline terminó con un error. Revisa los registros."
            _add_log(STATE["errorMessage"])


class PipelineRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/pipeline/status":
            with STATE_LOCK:
                snapshot = copy.deepcopy(STATE)
            if snapshot["status"] == "running" and snapshot["startedAt"] is not None:
                snapshot["elapsed"] = round(
                    (datetime.now().timestamp() - snapshot["startedAt"]) * 1000
                )
                snapshot["stats"]["executionTime"] = (
                    f"{snapshot['elapsed'] / 1000:.1f}s"
                )
            snapshot.pop("logs")
            self._send_json(snapshot)
            return

        if path == "/api/pipeline/logs":
            with STATE_LOCK:
                entries = copy.deepcopy(STATE["logs"])
            self._send_json({"entries": entries})
            return

        self._serve_frontend(path)

    def do_POST(self):
        if urlsplit(self.path).path != "/api/pipeline/run":
            self._send_json({"error": "Ruta no encontrada"}, status=404)
            return

        with STATE_LOCK:
            if STATE["status"] == "running":
                self._send_json({"error": "El pipeline ya está en ejecución"}, status=409)
                return

            STATE.clear()
            STATE.update(_initial_state())
            STATE["status"] = "running"
            STATE["startedAt"] = datetime.now().timestamp()
            _add_log("Ejecución del pipeline iniciada")
            threading.Thread(target=_run_pipeline, daemon=True).start()

        self._send_json({"status": "running"}, status=202)

    def _serve_frontend(self, request_path):
        if not FRONTEND_DIRECTORY.is_dir():
            self._send_json(
                {"error": "Frontend no compilado. Ejecuta npm run build en frontend/."},
                status=404,
            )
            return

        requested = unquote(request_path).lstrip("/")
        target = (FRONTEND_DIRECTORY / requested).resolve()
        frontend_root = FRONTEND_DIRECTORY.resolve()
        if not target.is_relative_to(frontend_root):
            self._send_json({"error": "Ruta no encontrada"}, status=404)
            return

        if not requested or not target.is_file():
            target = frontend_root / "index.html"

        if not target.is_file():
            self._send_json({"error": "Archivo no encontrado"}, status=404)
            return

        body = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        return


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), PipelineRequestHandler)
    print(f"Servidor disponible en http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()