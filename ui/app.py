import contextlib
import io
import queue
import threading
import tkinter as tk
from tkinter import ttk

from src.main import main


class QueueWriter(io.TextIOBase):
    """
    Captura la salida de print() y la envía
    a la cola de comunicación con Tkinter.
    """

    def __init__(self, message_queue):
        super().__init__()
        self.message_queue = message_queue

    def write(self, text):
        if text:
            self.message_queue.put(("console", text))

        return len(text)

    def flush(self):
        pass


class WeatherPipelineApp:
    """
    Interfaz gráfica principal del Weather Data Pipeline.
    """

    BG = "#0f172a"
    PANEL = "#111827"
    PANEL_LIGHT = "#1e293b"
    BORDER = "#334155"
    TEXT = "#e2e8f0"
    TEXT_MUTED = "#94a3b8"
    SUCCESS = "#22c55e"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    ACCENT = "#38bdf8"
    CONSOLE_BG = "#020617"

    def __init__(self, root):
        self.root = root

        self.root.title(
            "Weather Data Pipeline"
        )

        self.root.geometry(
            "1200x750"
        )

        self.root.minsize(
            1000,
            650
        )

        self.message_queue = queue.Queue()

        self.pipeline_running = False

        self.current_stage = 0

        self.stage_widgets = {}

        self.setup_styles()

        self.build_interface()

        self.root.after(
            100,
            self.process_queue
        )

    # =====================================================
    # STYLES
    # =====================================================

    def setup_styles(self):
        """
        Configura los estilos visuales de ttk.
        """

        style = ttk.Style()

        style.theme_use(
            "clam"
        )

        style.configure(
            "TFrame",
            background=self.BG
        )

        style.configure(
            "Panel.TFrame",
            background=self.PANEL
        )

        style.configure(
            "Card.TFrame",
            background=self.PANEL_LIGHT
        )

        style.configure(
            "TLabel",
            background=self.BG,
            foreground=self.TEXT,
            font=("Arial", 10)
        )

        style.configure(
            "Title.TLabel",
            background=self.BG,
            foreground=self.TEXT,
            font=("Arial", 24, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background=self.BG,
            foreground=self.TEXT_MUTED,
            font=("Arial", 10)
        )

        style.configure(
            "CardTitle.TLabel",
            background=self.PANEL_LIGHT,
            foreground=self.TEXT,
            font=("Arial", 11, "bold")
        )

        style.configure(
            "CardText.TLabel",
            background=self.PANEL_LIGHT,
            foreground=self.TEXT_MUTED,
            font=("Arial", 9)
        )

        style.configure(
            "Status.TLabel",
            background=self.PANEL_LIGHT,
            foreground=self.TEXT,
            font=("Arial", 9, "bold")
        )

        style.configure(
            "Primary.TButton",
            font=("Arial", 10, "bold"),
            padding=(18, 10),
            background=self.ACCENT,
            foreground="#020617",
            borderwidth=0
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", "#7dd3fc"),
                ("disabled", "#475569")
            ],
            foreground=[
                ("disabled", "#cbd5e1")
            ]
        )

        style.configure(
            "Secondary.TButton",
            font=("Arial", 10),
            padding=(14, 9),
            background=self.PANEL_LIGHT,
            foreground=self.TEXT,
            borderwidth=1
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", self.BORDER)
            ]
        )

        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=self.PANEL_LIGHT,
            background=self.ACCENT,
            bordercolor=self.PANEL_LIGHT,
            lightcolor=self.ACCENT,
            darkcolor=self.ACCENT
        )

    # =====================================================
    # INTERFACE
    # =====================================================

    def build_interface(self):
        """
        Construye toda la interfaz.
        """

        self.build_header()

        content = ttk.Frame(
            self.root,
            padding=(24, 0, 24, 24)
        )

        content.pack(
            fill="both",
            expand=True
        )

        self.build_sidebar(content)

        self.build_main_area(content)

    # =====================================================
    # HEADER
    # =====================================================

    def build_header(self):
        """
        Construye la cabecera.
        """

        header = ttk.Frame(
            self.root,
            padding=(24, 22, 24, 18)
        )

        header.pack(
            fill="x"
        )

        left = ttk.Frame(
            header
        )

        left.pack(
            side="left"
        )

        ttk.Label(
            left,
            text="WEATHER DATA PIPELINE",
            style="Title.TLabel"
        ).pack(
            anchor="w"
        )

        ttk.Label(
            left,
            text=(
                "Automated data processing and analytics"
            ),
            style="Subtitle.TLabel"
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        self.status_badge = tk.Label(
            header,
            text="READY",
            bg=self.PANEL_LIGHT,
            fg=self.TEXT_MUTED,
            font=("Arial", 10, "bold"),
            padx=16,
            pady=8
        )

        self.status_badge.pack(
            side="right"
        )

    # =====================================================
    # SIDEBAR
    # =====================================================

    def build_sidebar(self, parent):
        """
        Construye el panel lateral.
        """

        sidebar = ttk.Frame(
            parent,
            style="Panel.TFrame",
            width=280,
            padding=18
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(
            False
        )

        ttk.Label(
            sidebar,
            text="PIPELINE",
            background=self.PANEL,
            foreground=self.TEXT_MUTED,
            font=("Arial", 9, "bold")
        ).pack(
            anchor="w",
            pady=(0, 15)
        )

        stages = [
            ("1", "EXTRACT", "Open-Meteo API"),
            ("2", "TRANSFORM", "Pandas"),
            ("3", "VALIDATE", "Data Quality"),
            ("4", "ANALYZE", "Pandas Analytics"),
            ("5", "LOAD", "CSV + PostgreSQL"),
        ]

        for number, name, description in stages:
            self.create_stage_card(
                sidebar,
                number,
                name,
                description
            )

        separator = tk.Frame(
            sidebar,
            bg=self.BORDER,
            height=1
        )

        separator.pack(
            fill="x",
            pady=20
        )

        ttk.Label(
            sidebar,
            text="SYSTEM",
            background=self.PANEL,
            foreground=self.TEXT_MUTED,
            font=("Arial", 9, "bold")
        ).pack(
            anchor="w",
            pady=(0, 12)
        )

        self.create_info_row(
            sidebar,
            "SOURCE",
            "Open-Meteo"
        )

        self.create_info_row(
            sidebar,
            "PROCESSING",
            "Python + Pandas"
        )

        self.create_info_row(
            sidebar,
            "DATABASE",
            "PostgreSQL"
        )

        self.create_info_row(
            sidebar,
            "OUTPUT",
            "CSV + PostgreSQL"
        )

    def create_stage_card(
        self,
        parent,
        number,
        name,
        description
    ):
        """
        Crea una tarjeta individual de etapa.
        """

        card = tk.Frame(
            parent,
            bg=self.PANEL_LIGHT,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        card.pack(
            fill="x",
            pady=5
        )

        top = tk.Frame(
            card,
            bg=self.PANEL_LIGHT
        )

        top.pack(
            fill="x",
            padx=12,
            pady=(10, 2)
        )

        circle = tk.Label(
            top,
            text=number,
            width=2,
            bg=self.BORDER,
            fg=self.TEXT_MUTED,
            font=("Arial", 9, "bold")
        )

        circle.pack(
            side="left"
        )

        name_label = tk.Label(
            top,
            text=name,
            bg=self.PANEL_LIGHT,
            fg=self.TEXT_MUTED,
            font=("Arial", 10, "bold")
        )

        name_label.pack(
            side="left",
            padx=10
        )

        status_label = tk.Label(
            top,
            text="WAITING",
            bg=self.PANEL_LIGHT,
            fg=self.TEXT_MUTED,
            font=("Arial", 8, "bold")
        )

        status_label.pack(
            side="right"
        )

        description_label = tk.Label(
            card,
            text=description,
            bg=self.PANEL_LIGHT,
            fg=self.TEXT_MUTED,
            font=("Arial", 8)
        )

        description_label.pack(
            anchor="w",
            padx=(52, 12),
            pady=(0, 10)
        )

        self.stage_widgets[name] = {
            "card": card,
            "circle": circle,
            "name": name_label,
            "status": status_label
        }

    def create_info_row(
        self,
        parent,
        label,
        value
    ):
        """
        Crea una fila de información.
        """

        frame = tk.Frame(
            parent,
            bg=self.PANEL
        )

        frame.pack(
            fill="x",
            pady=4
        )

        tk.Label(
            frame,
            text=label,
            bg=self.PANEL,
            fg=self.TEXT_MUTED,
            font=("Arial", 8, "bold")
        ).pack(
            side="left"
        )

        tk.Label(
            frame,
            text=value,
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Arial", 8)
        ).pack(
            side="right"
        )

    # =====================================================
    # MAIN AREA
    # =====================================================

    def build_main_area(self, parent):
        """
        Construye el área principal.
        """

        main_area = ttk.Frame(
            parent,
            padding=(18, 0, 0, 0)
        )

        main_area.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.build_controls(
            main_area
        )

        self.build_progress(
            main_area
        )

        self.build_console(
            main_area
        )

    # =====================================================
    # CONTROLS
    # =====================================================

    def build_controls(self, parent):
        """
        Construye los controles.
        """

        controls = ttk.Frame(
            parent
        )

        controls.pack(
            fill="x",
            pady=(0, 15)
        )

        self.run_button = ttk.Button(
            controls,
            text="Run Pipeline",
            style="Primary.TButton",
            command=self.run_pipeline
        )

        self.run_button.pack(
            side="left"
        )

        self.clear_button = ttk.Button(
            controls,
            text="Clear Console",
            style="Secondary.TButton",
            command=self.clear_console
        )

        self.clear_button.pack(
            side="left",
            padx=10
        )

        self.connection_label = tk.Label(
            controls,
            text="PostgreSQL: Connected",
            bg=self.BG,
            fg=self.SUCCESS,
            font=("Arial", 9, "bold")
        )

        self.connection_label.pack(
            side="right"
        )

    # =====================================================
    # PROGRESS
    # =====================================================

    def build_progress(self, parent):
        """
        Construye el indicador de progreso.
        """

        frame = ttk.Frame(
            parent,
            style="Card.TFrame",
            padding=15
        )

        frame.pack(
            fill="x",
            pady=(0, 15)
        )

        header = tk.Frame(
            frame,
            bg=self.PANEL_LIGHT
        )

        header.pack(
            fill="x"
        )

        tk.Label(
            header,
            text="Pipeline Progress",
            bg=self.PANEL_LIGHT,
            fg=self.TEXT,
            font=("Arial", 10, "bold")
        ).pack(
            side="left"
        )

        self.progress_label = tk.Label(
            header,
            text="0 / 5 stages",
            bg=self.PANEL_LIGHT,
            fg=self.TEXT_MUTED,
            font=("Arial", 9)
        )

        self.progress_label.pack(
            side="right"
        )

        self.progress = ttk.Progressbar(
            frame,
            style="Horizontal.TProgressbar",
            maximum=5,
            value=0
        )

        self.progress.pack(
            fill="x",
            pady=(12, 0)
        )

    # =====================================================
    # CONSOLE
    # =====================================================

    def build_console(self, parent):
        """
        Construye la consola integrada.
        """

        title_frame = tk.Frame(
            parent,
            bg=self.BG
        )

        title_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        tk.Label(
            title_frame,
            text="Execution Console",
            bg=self.BG,
            fg=self.TEXT,
            font=("Arial", 10, "bold")
        ).pack(
            side="left"
        )

        self.console_status = tk.Label(
            title_frame,
            text="Ready",
            bg=self.BG,
            fg=self.TEXT_MUTED,
            font=("Arial", 9)
        )

        self.console_status.pack(
            side="right"
        )

        console_frame = tk.Frame(
            parent,
            bg=self.CONSOLE_BG,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        console_frame.pack(
            fill="both",
            expand=True
        )

        self.console = tk.Text(
            console_frame,
            wrap="word",
            bg=self.CONSOLE_BG,
            fg="#cbd5e1",
            insertbackground=self.TEXT,
            selectbackground=self.BORDER,
            font=("Courier New", 9),
            padx=15,
            pady=15,
            borderwidth=0,
            highlightthickness=0,
            state="disabled"
        )

        scrollbar = ttk.Scrollbar(
            console_frame,
            orient="vertical",
            command=self.console.yview
        )

        self.console.configure(
            yscrollcommand=scrollbar.set
        )

        self.console.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # =====================================================
    # PIPELINE
    # =====================================================

    def run_pipeline(self):
        """
        Inicia la ejecución del pipeline.
        """

        if self.pipeline_running:
            return

        self.pipeline_running = True
        self.current_stage = 0

        self.reset_stages()

        self.progress["value"] = 0
        self.progress_label.config(
            text="0 / 5 stages"
        )

        self.status_badge.config(
            text="RUNNING",
            bg=self.PANEL_LIGHT,
            fg=self.ACCENT
        )

        self.console_status.config(
            text="Pipeline running...",
            fg=self.ACCENT
        )

        self.connection_label.config(
            text="PostgreSQL: Checking...",
            fg=self.WARNING
        )

        self.run_button.config(
            state="disabled"
        )

        self.write_console(
            "\n"
            + "=" * 70
            + "\n"
            + "WEATHER DATA PIPELINE\n"
            + "=" * 70
            + "\n\n"
        )

        thread = threading.Thread(
            target=self.pipeline_worker,
            daemon=True
        )

        thread.start()

    def pipeline_worker(self):
        """
        Ejecuta el pipeline fuera del hilo principal.
        """

        writer = QueueWriter(
            self.message_queue
        )

        try:
            with contextlib.redirect_stdout(
                writer
            ):
                with contextlib.redirect_stderr(
                    writer
                ):
                    main()

            self.message_queue.put(
                (
                    "success",
                    "PIPELINE COMPLETED SUCCESSFULLY"
                )
            )

        except Exception as error:

            self.message_queue.put(
                (
                    "error",
                    str(error)
                )
            )

    # =====================================================
    # QUEUE PROCESSING
    # =====================================================

    def process_queue(self):
        """
        Procesa mensajes del pipeline.
        """

        try:
            while True:
                message_type, message = (
                    self.message_queue.get_nowait()
                )

                if message_type == "console":

                    self.write_console(
                        message
                    )

                    self.detect_stage(
                        message
                    )

                elif message_type == "success":

                    self.pipeline_finished(
                        success=True
                    )

                    self.write_console(
                        "\n"
                        + "=" * 70
                        + "\n"
                        + message
                        + "\n"
                        + "=" * 70
                        + "\n"
                    )

                elif message_type == "error":

                    self.pipeline_finished(
                        success=False
                    )

                    self.write_console(
                        "\n"
                        + "=" * 70
                        + "\n"
                        + "PIPELINE ERROR\n"
                        + message
                        + "\n"
                        + "=" * 70
                        + "\n"
                    )

        except queue.Empty:
            pass

        self.root.after(
            100,
            self.process_queue
        )

    # =====================================================
    # STAGES
    # =====================================================

    def detect_stage(self, message):
        """
        Detecta la etapa actual a partir de la salida
        del pipeline.
        """

        stage_map = {
            "[1/5] EXTRACT": (
                1,
                "EXTRACT"
            ),
            "[2/5] TRANSFORM": (
                2,
                "TRANSFORM"
            ),
            "[3/5] VALIDATE": (
                3,
                "VALIDATE"
            ),
            "[4/5] ANALYZE": (
                4,
                "ANALYZE"
            ),
            "[5/5] LOAD": (
                5,
                "LOAD"
            ),
        }

        for text, (number, name) in stage_map.items():

            if text in message:

                self.current_stage = number

                self.progress["value"] = number

                self.progress_label.config(
                    text=f"{number} / 5 stages"
                )

                self.update_stage_status(
                    name
                )

                break

        if "Conexión a PostgreSQL exitosa" in message:

            self.connection_label.config(
                text="PostgreSQL: Connected",
                fg=self.SUCCESS
            )

    def update_stage_status(
        self,
        current_stage
    ):
        """
        Actualiza visualmente las etapas.
        """

        stage_order = [
            "EXTRACT",
            "TRANSFORM",
            "VALIDATE",
            "ANALYZE",
            "LOAD"
        ]

        current_index = stage_order.index(
            current_stage
        )

        for index, name in enumerate(
            stage_order
        ):

            widget = self.stage_widgets[
                name
            ]

            if index < current_index:

                widget["circle"].config(
                    bg=self.SUCCESS,
                    fg="#020617"
                )

                widget["name"].config(
                    fg=self.TEXT
                )

                widget["status"].config(
                    text="DONE",
                    fg=self.SUCCESS
                )

            elif index == current_index:

                widget["circle"].config(
                    bg=self.ACCENT,
                    fg="#020617"
                )

                widget["name"].config(
                    fg=self.TEXT
                )

                widget["status"].config(
                    text="RUNNING",
                    fg=self.ACCENT
                )

            else:

                widget["circle"].config(
                    bg=self.BORDER,
                    fg=self.TEXT_MUTED
                )

                widget["name"].config(
                    fg=self.TEXT_MUTED
                )

                widget["status"].config(
                    text="WAITING",
                    fg=self.TEXT_MUTED
                )

    def reset_stages(self):
        """
        Devuelve todas las etapas a estado inicial.
        """

        for widget in self.stage_widgets.values():

            widget["circle"].config(
                bg=self.BORDER,
                fg=self.TEXT_MUTED
            )

            widget["name"].config(
                fg=self.TEXT_MUTED
            )

            widget["status"].config(
                text="WAITING",
                fg=self.TEXT_MUTED
            )

    def pipeline_finished(
        self,
        success
    ):
        """
        Actualiza la interfaz al terminar.
        """

        self.pipeline_running = False

        self.run_button.config(
            state="normal"
        )

        if success:

            self.progress["value"] = 5

            self.progress_label.config(
                text="5 / 5 stages"
            )

            self.status_badge.config(
                text="COMPLETED",
                fg=self.SUCCESS
            )

            self.console_status.config(
                text="Completed",
                fg=self.SUCCESS
            )

            self.connection_label.config(
                text="PostgreSQL: Connected",
                fg=self.SUCCESS
            )

            for name in self.stage_widgets:

                widget = self.stage_widgets[
                    name
                ]

                widget["circle"].config(
                    bg=self.SUCCESS,
                    fg="#020617"
                )

                widget["name"].config(
                    fg=self.TEXT
                )

                widget["status"].config(
                    text="DONE",
                    fg=self.SUCCESS
                )

        else:

            self.status_badge.config(
                text="ERROR",
                fg=self.ERROR
            )

            self.console_status.config(
                text="Pipeline failed",
                fg=self.ERROR
            )

            self.connection_label.config(
                text="PostgreSQL: Check connection",
                fg=self.ERROR
            )

    # =====================================================
    # CONSOLE HELPERS
    # =====================================================

    def write_console(self, text):
        """
        Escribe texto en la consola.
        """

        self.console.config(
            state="normal"
        )

        self.console.insert(
            "end",
            text
        )

        self.console.see(
            "end"
        )

        self.console.config(
            state="disabled"
        )

    def clear_console(self):
        """
        Limpia la consola.
        """

        self.console.config(
            state="normal"
        )

        self.console.delete(
            "1.0",
            "end"
        )

        self.console.config(
            state="disabled"
        )

        self.console_status.config(
            text="Ready",
            fg=self.TEXT_MUTED
        )


def main_gui():
    """
    Punto de entrada de la aplicación.
    """

    root = tk.Tk()

    WeatherPipelineApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main_gui()