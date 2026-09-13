#!/bin/bash
# 🔨 build.sh — Script de empaquetado completo para AutoClicker Pro
# Ejecutar: bash build.sh

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  ⚡ AutoClicker Pro v1.0 — by Qwen"
echo "  Script de construcción y empaquetado"
echo "═══════════════════════════════════════════════════════════"

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/AutoClickerPro"
APP_NAME="AutoClickerPro"

echo ""
echo "📁 Directorio del proyecto: $PROJECT_DIR"
echo "📦 Directorio de instalación: $INSTALL_DIR"
echo ""

# Paso 1: Crear entorno virtual
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Creando entorno virtual..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "$PROJECT_DIR/venv" ]; then
    python3 -m venv "$PROJECT_DIR/venv"
    echo "✅ Entorno virtual creado en $PROJECT_DIR/venv"
else
    echo "ℹ️  Entorno virtual ya existe"
fi

# Activar entorno virtual
source "$PROJECT_DIR/venv/bin/activate"

# Paso 2: Instalar dependencias
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Instalando dependencias..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pip install --upgrade pip
pip install pynput pyinstaller pygame

echo "✅ Dependencias instaladas"

# Paso 3: Ejecutar PyInstaller
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Empaquetando con PyInstaller..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_DIR"

pyinstaller --onefile \
            --windowed \
            --name "$APP_NAME" \
            --icon="$PROJECT_DIR/icon.ico" \
            --add-data "autoclicker_pro.py:." \
            autoclicker_pro.py

echo "✅ Binario generado en dist/$APP_NAME"

# Paso 4: Copiar a directorio de instalación
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Copiando a directorio de instalación..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p "$INSTALL_DIR"
cp "$PROJECT_DIR/dist/$APP_NAME" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$APP_NAME"

echo "✅ Binario copiado a $INSTALL_DIR/$APP_NAME"

# Paso 5: Generar archivo .desktop
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Generando archivo .desktop..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DESKTOP_FILE="$HOME/.local/share/applications/${APP_NAME}.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=⚡ AutoClicker Pro
Comment=Auto-clicker con marca de agua — by Qwen
Exec=$INSTALL_DIR/$APP_NAME
Icon=utilities-system-monitor
Terminal=false
Type=Application
Categories=Utility;Accessibility;
Keywords=auto;clicker;automation;mouse;
EOF

chmod +x "$DESKTOP_FILE"

echo "✅ Archivo .desktop creado en $DESKTOP_FILE"

# Paso 6: Actualizar base de datos de aplicaciones
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Actualizando base de datos de aplicaciones..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    echo "✅ Base de datos actualizada"
else
    echo "ℹ️  update-desktop-database no disponible (opcional)"
fi

# Limpiar archivos temporales de PyInstaller
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Limpiando archivos temporales..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

rm -rf "$PROJECT_DIR/build"
rm -rf "$PROJECT_DIR/dist"
rm -f "$PROJECT_DIR/$APP_NAME.spec"

echo "✅ Archivos temporales eliminados"

# Desactivar entorno virtual
deactivate

# Mensaje final
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ ¡CONSTRUCCIÓN COMPLETADA!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  📍 Ubicación del ejecutable: $INSTALL_DIR/$APP_NAME"
echo "  🖥️  Acceso desde menú: Busque 'AutoClicker Pro'"
echo "  🚀 Ejecutar directamente: $INSTALL_DIR/$APP_NAME"
echo ""
echo "  Nota: Si hay errores de permisos al ejecutar, ejecute:"
echo "        xhost +local:"
echo ""
echo "  Marca: AutoClicker Pro v1.0 — by Qwen"
echo "═══════════════════════════════════════════════════════════"
