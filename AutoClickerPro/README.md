# ⚡ AutoClicker Pro v1.0 — by Qwen

Auto-clicker completo para Linux Mint Cinnamon (X11) con marca de agua, macros, perfiles y estadísticas en vivo.

---

## 📋 Características

### Funcionalidades Core
- ✅ Intervalo ajustable (1 ms – 600 000 ms) con slider y botones preset
- ✅ Tipos de clic: izquierdo, derecho, doble, medio
- ✅ Modos: posición actual, coordenadas fijas, multi-punto (hasta 5 puntos)
- ✅ Hotkeys globales: F6 (start/stop), F7 (capturar coordenadas)
- ✅ Contador de clics en tiempo real

### Funcionalidades Pro
- 🚀 **Modo Ráfaga**: N clics rápidos + pausa configurable
- ⏱ **Temporizador de inicio**: Countdown antes del primer clic
- ⚡ **Modo Turbo**: El intervalo se reduce un 5% cada 100 clics
- 🎬 **Grabación de Macros**: Registra y reproduce secuencias de clics
- 🔊 **Sonido Feedback**: Beep al hacer clic y al detener
- 📊 **Estadísticas en vivo**: Clics totales, CPS, tiempo activo, última coordenada
- 💾 **Perfiles**: Guarda y carga hasta 5 configuraciones personalizadas

### Marca de Agua
- 🏷️ Visible en la ventana principal (esquina inferior derecha)
- 🏷️ Overlay opcional en pantalla (semitransparente, diagonal)
- 🏷️ Incluida en el título de la ventana
- 🏷️ Texto: "AutoClicker Pro v1.0 — by Qwen"

### Apariencia
- 🎨 Tema oscuro con paleta Catppuccin (#1e1e2e fondo)
- 🎨 Widgets modernos con ttk
- 🎨 Opacidad ajustable (30%–100%)
- 🎨 Always on top opcional
- 🎨 Animación de clic efímera (círculo en la coordenada)

---

## 📦 Instalación (3 pasos)

### Paso 1: Clonar o descargar el proyecto
```bash
cd /workspace/AutoClickerPro
```

### Paso 2: Ejecutar el script de construcción
```bash
chmod +x build.sh
./build.sh
```

El script:
1. Crea un entorno virtual
2. Instala dependencias (pynput, pyinstaller, pygame)
3. Empaqueta la aplicación con PyInstaller
4. Copia el binario a `~/AutoClickerPro/`
5. Genera el archivo `.desktop` en el menú de aplicaciones

### Paso 3: Ejecutar la aplicación
```bash
~/AutoClickerPro/AutoClickerPro
```

O busque **"AutoClicker Pro"** en el menú de Cinnamon.

---

## 🚀 Uso rápido

1. **Configurar intervalo**: Use el slider o los botones preset (10, 50, 100, 250, 500, 1000 ms)
2. **Seleccionar tipo de clic**: Izquierdo, derecho, doble o medio
3. **Elegir modo**:
   - *Posición actual*: Clickea donde esté el cursor
   - *Coordenadas fijas*: Clickea en X,Y específicas (use "📌 Capturar")
   - *Multi-punto*: Ciclo por hasta 5 puntos capturados
4. **Opciones avanzadas** (opcional):
   - Activar ráfaga, countdown, turbo, sonido, animación u overlay
5. **Presionar START ▶** o **F6** para iniciar
6. **Presionar STOP ■** o **F6** para detener

---

## ⚙ Configuración por defecto

La configuración se guarda automáticamente en `~/.autoclicker_config.json`.

| Parámetro | Valor por defecto |
|-----------|-------------------|
| Intervalo | 100 ms |
| Tipo de clic | Izquierdo |
| Modo | Posición actual |
| Ráfaga | 10 clics + 2000 ms |
| Countdown | 3 segundos |
| Turbo | Desactivado |
| Sonido | Desactivado |
| Overlay | Desactivado |
| Opacidad | 100% |

---

## 🔧 Solución de problemas

### ⚠ Error: "Permiso denegado" o pynput no funciona
```bash
xhost +local:
```
Luego reintente ejecutar la aplicación.

### ⚠ La aplicación no aparece en el menú
Ejecute manualmente:
```bash
update-desktop-database ~/.local/share/applications
```

### ⚠ Error al importar pynput
Asegúrese de estar en sesión X11 (no Wayland). Cinnamon usa X11 por defecto.

### ⚠ El sonido no funciona
Instale pygame:
```bash
pip install pygame
```

O el sonido fallback usará el beep del sistema (`printf '\a'`).

---

## 📁 Estructura de archivos

```
AutoClickerPro/
├── autoclicker_pro.py      # Código fuente principal (~980 líneas)
├── build.sh                # Script de empaquetado
├── AutoClickerPro.desktop  # Archivo de acceso directo
├── README.md               # Este archivo
└── icon.ico                # Ícono de la aplicación (opcional)
```

Archivos generados tras la construcción:
```
~/AutoClickerPro/
└── AutoClickerPro          # Binario ejecutable único
```

Archivos de configuración (ocultos en home):
```
~/.autoclicker_config.json   # Configuración general
~/.autoclicker_profiles.json # Perfiles guardados
~/.autoclicker_macros.json   # Macros (si se guardan externamente)
```

---

## 🎯 Hotkeys

| Tecla | Acción |
|-------|--------|
| **F6** | Iniciar / Detener auto-clicker |
| **F7** | Capturar coordenadas actuales |

---

## 📖 Créditos y marca

**Desarrollado por:** Qwen  
**Versión:** 1.0  
**Licencia:** Uso personal  
**Plataforma:** Linux Mint 21+ Cinnamon (X11)  

**Marca de agua:** "AutoClicker Pro v1.0 — by Qwen"  
Visible en:
- Ventana principal (esquina inferior derecha)
- Overlay de pantalla (opcional)
- Título de la ventana
- Archivo `.desktop`
- Este README

---

## 🛑 Restricciones técnicas

- ✗ No compatible con Wayland (solo X11)
- ✗ No requiere sudo en tiempo de ejecución
- ✗ No abre terminal visible al lanzar el binario
- ✗ Tamaño empaquetado < 20 MB
- ✓ Python 3.10+ requerido (preinstalado en Linux Mint 21+)

---

## 💡 Consejos de uso

1. **Para gaming**: Use modo ráfaga con 5-10 clics y pausa corta
2. **Para testing**: Use coordenadas fijas con intervalo preciso
3. **Para automatización**: Grabe una macro y guárdela en JSON
4. **Para sesiones largas**: Active el modo turbo progresivo
5. **Para visibilidad**: Active el overlay de marca de agua

---

**⚡ AutoClicker Pro v1.0 — by Qwen**
