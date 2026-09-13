#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AutoClicker Pro v1.0 — by Qwen
Auto-clicker completo para Linux Mint Cinnamon (X11)
Con marca de agua, macros, perfiles y estadísticas en vivo.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import time
import threading
import random
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

try:
    from pynput.mouse import Button, Controller as MouseController
    from pynput.keyboard import Listener as KeyboardListener, KeyCode
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN Y CONSTANTES
# ═══════════════════════════════════════════════════════════════

VERSION = "1.0"
WATERMARK_TEXT = f"AutoClicker Pro v{VERSION} — by Qwen"
CONFIG_FILE = Path.home() / ".autoclicker_config.json"
PROFILES_FILE = Path.home() / ".autoclicker_profiles.json"
MACROS_FILE = Path.home() / ".autoclicker_macros.json"

# Paleta de colores (Catppuccin-inspired)
COLORS = {
    "bg": "#1e1e2e",
    "fg": "#cdd6f4",
    "accent_blue": "#89b4fa",
    "accent_green": "#a6e3a1",
    "accent_red": "#f38ba8",
    "border": "#45475a",
    "watermark": "#888888",
    "entry_bg": "#313244",
    "button_bg": "#45475a",
    "button_active": "#585b70"
}

DEFAULT_CONFIG = {
    "interval_ms": 100,
    "click_type": "left",
    "click_mode": "current",
    "fixed_coords": (0, 0),
    "multi_points": [],
    "burst_count": 10,
    "burst_pause": 2000,
    "countdown_seconds": 3,
    "turbo_enabled": False,
    "turbo_min_interval": 10,
    "sound_click": False,
    "sound_stop": False,
    "show_animation": False,
    "overlay_enabled": False,
    "always_on_top": False,
    "opacity": 100,
    "profiles": {}
}


# ═══════════════════════════════════════════════════════════════
# CLASE PRINCIPAL
# ═══════════════════════════════════════════════════════════════

class AutoClickerPro:
    """Clase principal del AutoClicker Pro."""

    def __init__(self) -> None:
        """Inicializa la aplicación."""
        self.root = tk.Tk()
        self.root.title(f"⚡ {WATERMARK_TEXT}")
        self.root.geometry("420x520")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        # Controladores
        self.mouse = MouseController() if PYNPUT_AVAILABLE else None
        self.keyboard_listener: Optional[KeyboardListener] = None

        # Estado
        self.running = False
        self.paused = False
        self.recording = False
        self.macro_events: List[Dict[str, Any]] = []
        self.click_count = 0
        self.session_start = 0.0
        self.last_click_time = 0.0
        self.cps_history: List[float] = []
        self.turbo_counter = 0
        self.current_interval = DEFAULT_CONFIG["interval_ms"]

        # Configuración cargada
        self.config = self.load_config()

        # Variables de control
        self.interval_var = tk.IntVar(value=self.config.get("interval_ms", 100))
        self.click_type_var = tk.StringVar(value=self.config.get("click_type", "left"))
        self.click_mode_var = tk.StringVar(value=self.config.get("click_mode", "current"))
        self.fixed_x_var = tk.StringVar(value=str(self.config.get("fixed_coords", (0, 0))[0]))
        self.fixed_y_var = tk.StringVar(value=str(self.config.get("fixed_coords", (0, 0))[1]))
        self.burst_count_var = tk.IntVar(value=self.config.get("burst_count", 10))
        self.burst_pause_var = tk.IntVar(value=self.config.get("burst_pause", 2000))
        self.countdown_var = tk.IntVar(value=self.config.get("countdown_seconds", 3))
        self.turbo_var = tk.BooleanVar(value=self.config.get("turbo_enabled", False))
        self.sound_click_var = tk.BooleanVar(value=self.config.get("sound_click", False))
        self.sound_stop_var = tk.BooleanVar(value=self.config.get("sound_stop", False))
        self.animation_var = tk.BooleanVar(value=self.config.get("show_animation", False))
        self.overlay_var = tk.BooleanVar(value=self.config.get("overlay_enabled", False))
        self.always_on_top_var = tk.BooleanVar(value=self.config.get("always_on_top", False))
        self.opacity_var = tk.IntVar(value=self.config.get("opacity", 100))

        # Multi-puntos
        self.multi_points: List[Tuple[int, int]] = self.config.get("multi_points", [])
        self.multi_point_vars: List[Tuple[tk.StringVar, tk.StringVar]] = []

        # Overlay window
        self.overlay_window: Optional[tk.Toplevel] = None

        # Animación canvas
        self.anim_toplevel: Optional[tk.Toplevel] = None
        self.anim_canvas: Optional[tk.Canvas] = None

        # Inicializar pygame para sonido
        if PYGAME_AVAILABLE and self.sound_click_var.get():
            pygame.mixer.init()

        # Construir UI
        self.build_ui()
        self.build_watermark()

        # Aplicar configuración
        self.apply_config()

        # Iniciar listener de teclado
        if PYNPUT_AVAILABLE:
            self.start_keyboard_listener()

        # Actualizar estadísticas periódicamente
        self.update_stats()

        # Guardar config al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def build_ui(self) -> None:
        """Construye la interfaz de usuario."""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ══ SECCIÓN 1: INTERVALO ═══════════════════════════════
        interval_frame = ttk.LabelFrame(main_frame, text="⏱ Intervalo entre clics (ms)", padding=5)
        interval_frame.pack(fill=tk.X, pady=(0, 10))

        # Campo numérico
        entry_frame = ttk.Frame(interval_frame)
        entry_frame.pack(fill=tk.X, pady=(0, 5))

        self.interval_entry = ttk.Entry(entry_frame, textvariable=self.interval_var, width=10, justify="center")
        self.interval_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Botones preset
        presets = [10, 50, 100, 250, 500, 1000]
        for preset in presets:
            btn = ttk.Button(entry_frame, text=f"{preset}", width=4,
                           command=lambda p=preset: self.set_interval(p))
            btn.pack(side=tk.LEFT, padx=2)

        # Slider
        self.interval_slider = ttk.Scale(interval_frame, from_=1, to=60000,
                                         variable=self.interval_var, orient=tk.HORIZONTAL,
                                         command=self.on_slider_change)
        self.interval_slider.pack(fill=tk.X, pady=(5, 0))

        # ══ SECCIÓN 2: TIPO DE CLIC ════════════════════════════
        type_frame = ttk.LabelFrame(main_frame, text="🖱 Tipo de clic", padding=5)
        type_frame.pack(fill=tk.X, pady=(0, 10))

        types = [("Izquierdo", "left"), ("Derecho", "right"), ("Doble", "double"), ("Medio", "middle")]
        for i, (text, value) in enumerate(types):
            rb = ttk.Radiobutton(type_frame, text=text, variable=self.click_type_var, value=value)
            rb.grid(row=0, column=i, sticky=tk.W, padx=5)

        # ══ SECCIÓN 3: MODO DE CLIC ════════════════════════════
        mode_frame = ttk.LabelFrame(main_frame, text="📍 Modo de clic", padding=5)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        # Radio buttons de modo
        mode_inner = ttk.Frame(mode_frame)
        mode_inner.pack(fill=tk.X)

        ttk.Radiobutton(mode_inner, text="Posición actual", variable=self.click_mode_var,
                       value="current").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(mode_inner, text="Coordenadas fijas", variable=self.click_mode_var,
                       value="fixed").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(mode_inner, text="Multi-punto", variable=self.click_mode_var,
                       value="multi").grid(row=0, column=2, sticky=tk.W)

        # Coordenadas fijas
        coords_frame = ttk.Frame(mode_frame)
        coords_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(coords_frame, text="X:").pack(side=tk.LEFT, padx=(0, 5))
        self.fixed_x_entry = ttk.Entry(coords_frame, textvariable=self.fixed_x_var, width=6)
        self.fixed_x_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(coords_frame, text="Y:").pack(side=tk.LEFT, padx=(0, 5))
        self.fixed_y_entry = ttk.Entry(coords_frame, textvariable=self.fixed_y_var, width=6)
        self.fixed_y_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(coords_frame, text="📌 Capturar", command=self.capture_coords).pack(side=tk.LEFT)

        # Multi-puntos
        self.multi_frame = ttk.Frame(mode_frame)
        self.multi_frame.pack(fill=tk.X, pady=(5, 0))
        self.build_multi_points()

        # ══ SECCIÓN 4: OPCIONES AVANZADAS ═════════════════════
        adv_frame = ttk.LabelFrame(main_frame, text="⚙ Opciones avanzadas", padding=5)
        adv_frame.pack(fill=tk.X, pady=(0, 10))

        # Burst
        burst_frame = ttk.Frame(adv_frame)
        burst_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(burst_frame, text="Ráfaga:").pack(side=tk.LEFT)
        ttk.Entry(burst_frame, textvariable=self.burst_count_var, width=4).pack(side=tk.LEFT, padx=5)
        ttk.Label(burst_frame, text="clics + pausa").pack(side=tk.LEFT, padx=5)
        ttk.Entry(burst_frame, textvariable=self.burst_pause_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(burst_frame, text="ms").pack(side=tk.LEFT, padx=5)

        # Countdown
        countdown_frame = ttk.Frame(adv_frame)
        countdown_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(countdown_frame, text="Temporizador:").pack(side=tk.LEFT)
        ttk.Entry(countdown_frame, textvariable=self.countdown_var, width=3).pack(side=tk.LEFT, padx=5)
        ttk.Label(countdown_frame, text="segundos").pack(side=tk.LEFT, padx=5)

        # Checkboxes
        checks_frame = ttk.Frame(adv_frame)
        checks_frame.pack(fill=tk.X)

        ttk.Checkbutton(checks_frame, text="Turbo", variable=self.turbo_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checks_frame, text="Sonido clic", variable=self.sound_click_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checks_frame, text="Sonido stop", variable=self.sound_stop_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checks_frame, text="Animación", variable=self.animation_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checks_frame, text="Overlay", variable=self.overlay_var, command=self.toggle_overlay).pack(side=tk.LEFT, padx=5)

        # ══ SECCIÓN 5: MACRO ═══════════════════════════════════
        macro_frame = ttk.LabelFrame(main_frame, text="🎬 Macro", padding=5)
        macro_frame.pack(fill=tk.X, pady=(0, 10))

        macro_btns = ttk.Frame(macro_frame)
        macro_btns.pack(fill=tk.X)

        self.rec_btn = ttk.Button(macro_btns, text="● REC", command=self.toggle_record)
        self.rec_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(macro_btns, text="▶ PLAY", command=self.play_macro).pack(side=tk.LEFT, padx=5)
        ttk.Button(macro_btns, text="💾 Guardar", command=self.save_macro).pack(side=tk.LEFT, padx=5)
        ttk.Button(macro_btns, text="📂 Cargar", command=self.load_macro).pack(side=tk.LEFT, padx=5)

        self.macro_label = ttk.Label(macro_btns, text="0 eventos", foreground=COLORS["accent_blue"])
        self.macro_label.pack(side=tk.RIGHT, padx=5)

        # ══ SECCIÓN 6: CONTROLES PRINCIPALES ═══════════════════
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_btn = tk.Button(ctrl_frame, text="▶ START", bg=COLORS["accent_green"],
                                   fg="#000000", font=("DejaVu Sans", 12, "bold"),
                                   command=self.toggle_start, width=10)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(ctrl_frame, text="❌ Salir", command=self.on_exit).pack(side=tk.RIGHT, padx=5)

        # Always on top y opacidad
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X)

        ttk.Checkbutton(options_frame, text="Always on top", variable=self.always_on_top_var,
                       command=self.toggle_always_on_top).pack(side=tk.LEFT, padx=5)

        ttk.Label(options_frame, text="Opacidad:").pack(side=tk.LEFT, padx=(10, 5))
        self.opacity_slider = ttk.Scale(options_frame, from_=30, to=100,
                                        variable=self.opacity_var, orient=tk.HORIZONTAL,
                                        command=self.on_opacity_change)
        self.opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ══ SECCIÓN 7: ESTADÍSTICAS ════════════════════════════
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Estadísticas", padding=5)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.stats_label = ttk.Label(stats_frame, text="Clics: 0 | CPS: 0.0 | Tiempo: 00:00:00 | Última: (0, 0)",
                                     foreground=COLORS["fg"])
        self.stats_label.pack(anchor=tk.W)

        # ══ SECCIÓN 8: PERFILES ════════════════════════════════
        profile_frame = ttk.Frame(main_frame)
        profile_frame.pack(fill=tk.X)

        ttk.Button(profile_frame, text="Guardar perfil", command=self.save_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(profile_frame, text="Cargar perfil", command=self.load_profile).pack(side=tk.LEFT, padx=5)

        # ══ BARRA DE ESTADO ════════════════════════════════════
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

    def build_watermark(self) -> None:
        """Construye la marca de agua en la ventana principal."""
        watermark = tk.Label(self.root, text=WATERMARK_TEXT, font=("Helvetica", 8),
                            foreground=COLORS["watermark"], bg=COLORS["bg"])
        watermark.place(relx=1.0, rely=1.0, anchor=tk.SE, x=-10, y=-10)

    def build_multi_points(self) -> None:
        """Construye la sección de multi-puntos."""
        for widget in self.multi_frame.winfo_children():
            widget.destroy()
        self.multi_point_vars.clear()

        for i in range(5):
            row_frame = ttk.Frame(self.multi_frame)
            row_frame.pack(fill=tk.X, pady=2)

            ttk.Label(row_frame, text=f"P{i+1}:").pack(side=tk.LEFT, padx=5)

            x_var = tk.StringVar(value="")
            y_var = tk.StringVar(value="")
            self.multi_point_vars.append((x_var, y_var))

            ttk.Entry(row_frame, textvariable=x_var, width=5).pack(side=tk.LEFT, padx=2)
            ttk.Label(row_frame, text=",").pack(side=tk.LEFT)
            ttk.Entry(row_frame, textvariable=y_var, width=5).pack(side=tk.LEFT, padx=2)

            ttk.Button(row_frame, text="📌", width=2,
                      command=lambda idx=i: self.capture_multi_point(idx)).pack(side=tk.LEFT, padx=5)

            if i < len(self.multi_points):
                x_var.set(str(self.multi_points[i][0]))
                y_var.set(str(self.multi_points[i][1]))

    def build_overlay(self) -> None:
        """Construye el overlay de marca de agua en pantalla."""
        if self.overlay_window is not None:
            return

        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.overrideredirect(True)
        self.overlay_window.attributes("-alpha", 0.15)
        self.overlay_window.attributes("-topmost", True)

        # Posicionar en esquina inferior derecha
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        canvas = tk.Canvas(self.overlay_window, width=300, height=100, bg=COLORS["bg"], highlightthickness=0)
        canvas.pack()

        # Texto diagonal simulado
        canvas.create_text(150, 50, text=WATERMARK_TEXT, font=("Helvetica", 14, "bold"),
                          fill=COLORS["watermark"], angle=25)

        self.overlay_window.geometry(f"+{screen_width - 310}+{screen_height - 110}")

    def toggle_overlay(self) -> None:
        """Muestra u oculta el overlay."""
        if self.overlay_var.get():
            self.build_overlay()
            if self.overlay_window:
                self.overlay_window.deiconify()
        else:
            if self.overlay_window:
                self.overlay_window.withdraw()

    def toggle_always_on_top(self) -> None:
        """Activa o desactiva always on top."""
        self.root.attributes("-topmost", self.always_on_top_var.get())

    def on_opacity_change(self, *args) -> None:
        """Cambia la opacidad de la ventana."""
        opacity = self.opacity_var.get() / 100.0
        self.root.attributes("-alpha", opacity)

    def set_interval(self, value: int) -> None:
        """Establece el intervalo desde los botones preset."""
        self.interval_var.set(value)
        self.current_interval = value

    def on_slider_change(self, *args) -> None:
        """Sincroniza el slider con el campo numérico."""
        value = int(self.interval_var.get())
        self.current_interval = value

    def capture_coords(self) -> None:
        """Captura las coordenadas actuales del cursor."""
        if self.mouse:
            x, y = self.mouse.position
            self.fixed_x_var.set(str(int(x)))
            self.fixed_y_var.set(str(int(y)))
            self.status_var.set(f"Coordenadas capturadas: ({x}, {y})")

    def capture_multi_point(self, index: int) -> None:
        """Captura un punto multi-punto."""
        if self.mouse:
            x, y = self.mouse.position
            x_var, y_var = self.multi_point_vars[index]
            x_var.set(str(int(x)))
            y_var.set(str(int(y)))

            # Actualizar lista interna
            while len(self.multi_points) <= index:
                self.multi_points.append((0, 0))
            self.multi_points[index] = (int(x), int(y))

            self.status_var.set(f"Punto {index + 1} capturado: ({x}, {y})")

    def start_keyboard_listener(self) -> None:
        """Inicia el listener de teclado para hotkeys."""
        def on_press(key) -> None:
            try:
                if key == KeyCode.from_vk(117):  # F6
                    self.toggle_start()
                elif key == KeyCode.from_vk(118):  # F7
                    self.capture_coords()
            except Exception:
                pass

        self.keyboard_listener = KeyboardListener(on_press=on_press)
        self.keyboard_listener.start()

    def toggle_start(self) -> None:
        """Alterna entre iniciar y detener."""
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self) -> None:
        """Inicia el auto-clicker."""
        if not PYNPUT_AVAILABLE:
            messagebox.showerror("Error", "⚠ pynput no disponible.\nInstale: pip install pynput")
            return

        # Validar intervalo
        interval = self.interval_var.get()
        if interval < 1:
            messagebox.showerror("Error", "El intervalo debe ser ≥ 1 ms")
            return

        # Countdown
        countdown = self.countdown_var.get()
        if countdown > 0:
            self.status_var.set(f"Iniciando en {countdown}...")
            for i in range(countdown, 0, -1):
                self.status_var.set(f"Iniciando en {i}...")
                self.root.update()
                time.sleep(1)

        self.running = True
        self.paused = False
        self.session_start = time.time()
        self.start_btn.config(text="■ STOP", bg=COLORS["accent_red"])
        self.status_var.set("Ejecutando...")

        # Iniciar hilo de clics
        thread = threading.Thread(target=self.click_loop, daemon=True)
        thread.start()

        # Iniciar sonido si está activado
        if PYGAME_AVAILABLE and self.sound_click_var.get():
            try:
                pygame.mixer.init()
            except Exception:
                pass

    def stop(self) -> None:
        """Detiene el auto-clicker."""
        self.running = False
        self.start_btn.config(text="▶ START", bg=COLORS["accent_green"])
        self.status_var.set("Detenido")

        if self.sound_stop_var.get():
            self.play_sound("stop")

        # Resetear turbo
        self.turbo_counter = 0
        self.current_interval = self.interval_var.get()

    def click_loop(self) -> None:
        """Bucle principal de clics."""
        burst_count = self.burst_count_var.get()
        burst_pause = self.burst_pause_var.get()
        burst_index = 0

        while self.running:
            try:
                # Verificar límite de 1M clics
                if self.click_count >= 1_000_000:
                    self.status_var.set("Pausa automática (1M clics)")
                    time.sleep(1)
                    self.click_count = 0

                # Obtener coordenadas según modo
                x, y = self.get_click_position()

                # Hacer clic
                self.perform_click(x, y)

                # Actualizar contador
                self.click_count += 1
                self.last_click_time = time.time()

                # Mostrar animación si está activada
                if self.animation_var.get():
                    self.show_click_animation(x, y)

                # Ajustar turbo
                if self.turbo_var.get():
                    self.turbo_adjust()

                # Manejar ráfaga
                burst_index += 1
                if burst_index >= burst_count:
                    burst_index = 0
                    if burst_pause > 0:
                        # Pausa entre ráfagas
                        for _ in range(burst_pause // 10):
                            if not self.running:
                                break
                            time.sleep(0.01)

                # Esperar intervalo
                for _ in range(self.current_interval // 10):
                    if not self.running:
                        break
                    time.sleep(0.01)

            except Exception as e:
                self.status_var.set(f"Error: {str(e)}")
                time.sleep(0.1)

    def get_click_position(self) -> Tuple[int, int]:
        """Obtiene la posición donde hacer clic."""
        mode = self.click_mode_var.get()

        if mode == "current":
            return self.mouse.position if self.mouse else (0, 0)
        elif mode == "fixed":
            try:
                x = int(self.fixed_x_var.get())
                y = int(self.fixed_y_var.get())
                return (x, y)
            except ValueError:
                return self.mouse.position if self.mouse else (0, 0)
        elif mode == "multi":
            # Ciclo por los puntos guardados
            if self.multi_points:
                index = self.click_count % len(self.multi_points)
                return self.multi_points[index]
            return self.mouse.position if self.mouse else (0, 0)

        return self.mouse.position if self.mouse else (0, 0)

    def perform_click(self, x: int, y: int) -> None:
        """Realiza el clic en la posición especificada."""
        if not self.mouse:
            return

        # Mover el cursor si es necesario
        click_type = self.click_type_var.get()

        if click_type == "double":
            self.mouse.position = (x, y)
            self.mouse.click(Button.left, 2)
        elif click_type == "right":
            self.mouse.position = (x, y)
            self.mouse.click(Button.right, 1)
        elif click_type == "middle":
            self.mouse.position = (x, y)
            self.mouse.click(Button.middle, 1)
        else:  # left
            self.mouse.position = (x, y)
            self.mouse.click(Button.left, 1)

        # Sonido de clic
        if self.sound_click_var.get():
            self.play_sound("click")

    def play_sound(self, sound_type: str) -> None:
        """Reproduce un sonido de feedback."""
        if sound_type == "click":
            # Tick corto
            if PYGAME_AVAILABLE:
                try:
                    # Generar tono simple
                    sample_rate = 44100
                    duration = 0.05
                    frequency = 800
                    samples = [int(127 + 127 * 0.5 * 
                             __import__('math').sin(2 * __import__('math').pi * frequency * i / sample_rate))
                              for i in range(int(sample_rate * duration))]
                    sound = pygame.mixer.Sound(buffer=bytes(samples))
                    sound.play()
                except Exception:
                    pass
            else:
                os.system("printf '\\a'")
        elif sound_type == "stop":
            # Beep de confirmación
            if PYGAME_AVAILABLE:
                try:
                    sample_rate = 44100
                    duration = 0.15
                    frequency = 600
                    samples = [int(127 + 127 * 0.5 * 
                             __import__('math').sin(2 * __import__('math').pi * frequency * i / sample_rate))
                              for i in range(int(sample_rate * duration))]
                    sound = pygame.mixer.Sound(buffer=bytes(samples))
                    sound.play()
                except Exception:
                    pass
            else:
                os.system("printf '\\a'")

    def turbo_adjust(self) -> None:
        """Ajusta el intervalo en modo turbo."""
        self.turbo_counter += 1
        if self.turbo_counter >= 100:
            self.turbo_counter = 0
            min_interval = max(1, self.config.get("turbo_min_interval", 10))
            new_interval = max(min_interval, int(self.current_interval * 0.95))
            if new_interval < self.current_interval:
                self.current_interval = new_interval

    def show_click_animation(self, x: int, y: int) -> None:
        """Muestra una animación de clic en la posición."""
        try:
            # Crear toplevel transparente
            if self.anim_toplevel is None:
                self.anim_toplevel = tk.Toplevel(self.root)
                self.anim_toplevel.overrideredirect(True)
                self.anim_toplevel.attributes("-topmost", True)
                self.anim_toplevel.attributes("-alpha", 0.7)
                self.anim_canvas = tk.Canvas(self.anim_toplevel, width=40, height=40,
                                            bg=COLORS["bg"], highlightthickness=0)
                self.anim_canvas.pack()

            self.anim_toplevel.geometry(f"+{x - 20}+{y - 20}")
            self.anim_canvas.delete("all")
            self.anim_canvas.create_oval(0, 0, 40, 40, outline=COLORS["accent_blue"], width=3)

            self.root.after(200, lambda: self.anim_canvas.delete("all"))
        except Exception:
            pass

    def toggle_record(self) -> None:
        """Activa o desactiva la grabación de macro."""
        if self.recording:
            self.recording = False
            self.rec_btn.config(text="● REC")
            self.status_var.set(f"Macro grabada: {len(self.macro_events)} eventos")
        else:
            self.recording = True
            self.macro_events.clear()
            self.rec_btn.config(text="■ STOP REC")
            self.status_var.set("Grabando macro... (haz clics)")

            # Iniciar listener de grabación
            thread = threading.Thread(target=self.record_macro_thread, daemon=True)
            thread.start()

    def record_macro_thread(self) -> None:
        """Hilo de grabación de macro."""
        from pynput.mouse import Listener as MouseListener

        def on_click(x, y, button, pressed) -> None:
            if self.recording and pressed:
                event = {
                    "x": int(x),
                    "y": int(y),
                    "button": str(button).split(".")[-1],
                    "time": time.time()
                }
                self.macro_events.append(event)
                self.root.after(0, lambda: self.macro_label.config(text=f"{len(self.macro_events)} eventos"))

            return not self.recording  # Detener cuando recording=False

        with MouseListener(on_click=on_click) as listener:
            listener.join()

    def play_macro(self) -> None:
        """Reproduce la macro grabada."""
        if not self.macro_events:
            messagebox.showinfo("Info", "No hay macro grabada")
            return

        if not self.running:
            thread = threading.Thread(target=self.play_macro_thread, daemon=True)
            thread.start()

    def play_macro_thread(self) -> None:
        """Hilo de reproducción de macro."""
        if not self.mouse:
            return

        base_time = self.macro_events[0]["time"] if self.macro_events else time.time()

        for event in self.macro_events:
            if not self.running:
                break

            delay = event["time"] - base_time
            time.sleep(max(0, delay))

            button_map = {
                "left": Button.left,
                "right": Button.right,
                "middle": Button.middle
            }
            btn = button_map.get(event["button"], Button.left)

            self.mouse.position = (event["x"], event["y"])
            self.mouse.click(btn, 1)

            self.click_count += 1

    def save_macro(self) -> None:
        """Guarda la macro en archivo JSON."""
        if not self.macro_events:
            messagebox.showwarning("Advertencia", "No hay macro para guardar")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json")])
        if filepath:
            with open(filepath, "w") as f:
                json.dump(self.macro_events, f, indent=2)
            self.status_var.set(f"Macro guardada en {filepath}")

    def load_macro(self) -> None:
        """Carga una macro desde archivo JSON."""
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filepath:
            try:
                with open(filepath, "r") as f:
                    self.macro_events = json.load(f)
                self.macro_label.config(text=f"{len(self.macro_events)} eventos")
                self.status_var.set(f"Macro cargada desde {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la macro: {e}")

    def save_profile(self) -> None:
        """Guarda la configuración actual como perfil."""
        name = tk.simpledialog.askstring("Guardar perfil", "Nombre del perfil:")
        if not name:
            return

        profile = {
            "interval_ms": self.interval_var.get(),
            "click_type": self.click_type_var.get(),
            "click_mode": self.click_mode_var.get(),
            "fixed_coords": (int(self.fixed_x_var.get()) if self.fixed_x_var.get() else 0,
                           int(self.fixed_y_var.get()) if self.fixed_y_var.get() else 0),
            "multi_points": self.multi_points,
            "burst_count": self.burst_count_var.get(),
            "burst_pause": self.burst_pause_var.get(),
            "turbo_enabled": self.turbo_var.get()
        }

        profiles = self.load_profiles()
        profiles[name] = profile

        if len(profiles) > 5:
            messagebox.showwarning("Límite", "Máximo 5 perfiles permitidos")
            return

        self.save_profiles(profiles)
        self.status_var.set(f"Perfil '{name}' guardado")

    def load_profile(self) -> None:
        """Carga un perfil guardado."""
        profiles = self.load_profiles()
        if not profiles:
            messagebox.showinfo("Info", "No hay perfiles guardados")
            return

        # Diálogo simple para seleccionar perfil
        dialog = tk.Toplevel(self.root)
        dialog.title("Cargar perfil")
        dialog.geometry("250x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Selecciona un perfil:").pack(pady=10)

        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10)

        for name in profiles.keys():
            listbox.insert(tk.END, name)

        def on_select(event=None) -> None:
            selection = listbox.curselection()
            if selection:
                name = listbox.get(selection[0])
                profile = profiles[name]

                self.interval_var.set(profile.get("interval_ms", 100))
                self.click_type_var.set(profile.get("click_type", "left"))
                self.click_mode_var.set(profile.get("click_mode", "current"))

                fixed_coords = profile.get("fixed_coords", (0, 0))
                self.fixed_x_var.set(str(fixed_coords[0]))
                self.fixed_y_var.set(str(fixed_coords[1]))

                self.multi_points = profile.get("multi_points", [])
                self.build_multi_points()

                self.burst_count_var.set(profile.get("burst_count", 10))
                self.burst_pause_var.set(profile.get("burst_pause", 2000))
                self.turbo_var.set(profile.get("turbo_enabled", False))

                self.status_var.set(f"Perfil '{name}' cargado")
                dialog.destroy()

        listbox.bind("<Double-Button-1>", on_select)

        ttk.Button(dialog, text="Cancelar", command=dialog.destroy).pack(pady=5)

    def load_profiles(self) -> Dict[str, Any]:
        """Carga los perfiles desde archivo."""
        try:
            if PROFILES_FILE.exists():
                with open(PROFILES_FILE, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_profiles(self, profiles: Dict[str, Any]) -> None:
        """Guarda los perfiles en archivo."""
        with open(PROFILES_FILE, "w") as f:
            json.dump(profiles, f, indent=2)

    def load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde archivo."""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    # Fusionar con defaults
                    merged = DEFAULT_CONFIG.copy()
                    merged.update(config)
                    return merged
        except Exception:
            pass
        return DEFAULT_CONFIG.copy()

    def save_config(self) -> None:
        """Guarda la configuración en archivo."""
        config = {
            "interval_ms": self.interval_var.get(),
            "click_type": self.click_type_var.get(),
            "click_mode": self.click_mode_var.get(),
            "fixed_coords": (int(self.fixed_x_var.get()) if self.fixed_x_var.get() else 0,
                           int(self.fixed_y_var.get()) if self.fixed_y_var.get() else 0),
            "multi_points": self.multi_points,
            "burst_count": self.burst_count_var.get(),
            "burst_pause": self.burst_pause_var.get(),
            "countdown_seconds": self.countdown_var.get(),
            "turbo_enabled": self.turbo_var.get(),
            "sound_click": self.sound_click_var.get(),
            "sound_stop": self.sound_stop_var.get(),
            "show_animation": self.animation_var.get(),
            "overlay_enabled": self.overlay_var.get(),
            "always_on_top": self.always_on_top_var.get(),
            "opacity": self.opacity_var.get()
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    def apply_config(self) -> None:
        """Aplica la configuración cargada."""
        self.always_on_top_var.set(self.config.get("always_on_top", False))
        self.toggle_always_on_top()

        self.opacity_var.set(self.config.get("opacity", 100))
        self.on_opacity_change()

        if self.config.get("overlay_enabled", False):
            self.overlay_var.set(True)
            self.build_overlay()

    def update_stats(self) -> None:
        """Actualiza las estadísticas en tiempo real."""
        if self.running:
            elapsed = time.time() - self.session_start
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)

            # Calcular CPS
            if elapsed > 0:
                cps = self.click_count / elapsed
            else:
                cps = 0.0

            # Última coordenada
            last_pos = "(0, 0)"
            if self.mouse and self.running:
                x, y = self.mouse.position
                last_pos = f"({x}, {y})"

            self.stats_label.config(
                text=f"Clics: {self.click_count} | CPS: {cps:.1f} | Tiempo: {hours:02d}:{minutes:02d}:{seconds:02d} | Última: {last_pos}"
            )

        self.root.after(100, self.update_stats)

    def on_exit(self) -> None:
        """Maneja la salida de la aplicación."""
        self.running = False

        # Detener listeners
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        # Guardar configuración
        self.save_config()

        # Destruir ventanas
        if self.overlay_window:
            self.overlay_window.destroy()
        if self.anim_toplevel:
            self.anim_toplevel.destroy()

        self.root.destroy()

        if PYGAME_AVAILABLE:
            pygame.quit()


# ═══════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Configurar estilo ttk
    style = ttk.Style()
    style.theme_use("clam")

    # Configurar colores
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["fg"])
    style.configure("TButton", background=COLORS["button_bg"], foreground=COLORS["fg"])
    style.configure("TEntry", fieldbackground=COLORS["entry_bg"], foreground=COLORS["fg"])
    style.configure("TLabelframe", background=COLORS["bg"], foreground=COLORS["fg"])
    style.configure("TLabelframe.Label", background=COLORS["bg"], foreground=COLORS["fg"])

    app = AutoClickerPro()
    app.root.mainloop()
