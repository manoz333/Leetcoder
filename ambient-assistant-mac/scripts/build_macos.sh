#!/bin/bash
# Build script for Ambient Assistant macOS application

set -e  # Exit on error

# Configuration
APP_NAME="Ambient Assistant"
APP_IDENTIFIER="com.ambient.assistant"
APP_VERSION=$(python -c "import ambient; print(ambient.__version__)")
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
ICON_PATH="resources/icons/app_icon.icns"
OUTPUT_DIR="dist"

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller is not installed. Installing..."
    pip install pyinstaller
fi

# Check if create-dmg is installed (for DMG creation)
if ! command -v create-dmg &> /dev/null; then
    echo "create-dmg is not installed. Please install it with:"
    echo "brew install create-dmg"
    echo "Continuing without DMG creation..."
    CREATE_DMG=false
else
    CREATE_DMG=true
fi

# Create clean build directory
echo "Cleaning build directories..."
rm -rf build dist

# Create resources directory if it doesn't exist
mkdir -p resources/icons

# Check if icon exists
if [ ! -f "$ICON_PATH" ]; then
    echo "Warning: Icon file not found at $ICON_PATH"
    echo "Using default icon..."
    ICON_PATH=""
fi

# Create spec file for PyInstaller
echo "Creating PyInstaller spec file..."
cat > ambient_assistant.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.datastruct import Tree
from PyInstaller.building.osx import BUNDLE

block_cipher = None

a = Analysis(
    ['ambient/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('resources/icons', 'resources/icons'),
        ('resources/sounds', 'resources/sounds'),
        ('resources/models', 'resources/models'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtQuick',
        'django.db.models.sql.compiler',
        'structlog.processors',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'notebook', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AmbientAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='$ICON_PATH' if '$ICON_PATH' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AmbientAssistant',
)

app = BUNDLE(
    coll,
    name='Ambient Assistant.app',
    icon='$ICON_PATH' if '$ICON_PATH' else None,
    bundle_identifier='$APP_IDENTIFIER',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '$APP_VERSION',
        'CFBundleVersion': '$APP_VERSION',
        'LSUIElement': True,  # Run as agent (no dock icon)
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        'NSAppleEventsUsageDescription': 'Ambient Assistant needs to access other applications to provide context-aware assistance.',
        'NSCameraUsageDescription': 'Ambient Assistant does not use the camera.',
        'NSMicrophoneUsageDescription': 'Ambient Assistant does not use the microphone.',
        'NSScreenCaptureUsageDescription': 'Ambient Assistant needs to capture your screen to provide context-aware assistance.',
    },
)
EOF

# Build the application
echo "Building application with PyInstaller..."
pyinstaller --clean ambient_assistant.spec

# Create entitlements file for code signing
echo "Creating entitlements file..."
cat > entitlements.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.automation.apple-events</key>
    <true/>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.device.audio-input</key>
    <false/>
    <key>com.apple.security.device.camera</key>
    <false/>
    <key>com.apple.security.personal-information.photos-library</key>
    <false/>
    <key>com.apple.security.screen-recording</key>
    <true/>
</dict>
</plist>
EOF

# Check if we have a valid signing identity
IDENTITY=$(security find-identity -p codesigning -v | grep "Developer ID Application" | head -1 | awk -F '"' '{print $2}')

if [ -n "$IDENTITY" ]; then
    echo "Found signing identity: $IDENTITY"
    echo "Signing application..."
    
    # Sign all executables and libraries first
    find "dist/Ambient Assistant.app/Contents/MacOS" -type f -name "*.so" -o -name "*.dylib" | while read file; do
        codesign --force --sign "$IDENTITY" --timestamp --options runtime "$file"
    done
    
    # Sign main executable
    codesign --force --sign "$IDENTITY" --timestamp --options runtime "dist/Ambient Assistant.app/Contents/MacOS/AmbientAssistant"
    
    # Sign the app bundle with entitlements
    codesign --force --sign "$IDENTITY" --timestamp --options runtime --entitlements entitlements.plist "dist/Ambient Assistant.app"
    
    # Verify signature
    codesign --verify --verbose "dist/Ambient Assistant.app"
    
    echo "Application signed successfully"
else
    echo "No valid signing identity found. Skipping code signing."
    echo "Note: Unsigned applications may be blocked by Gatekeeper."
fi

# Create DMG if create-dmg is available
if [ "$CREATE_DMG" = true ]; then
    echo "Creating DMG..."
    create-dmg \
        --volname "Ambient Assistant" \
        --volicon "$ICON_PATH" \
        --window-pos 200 120 \
        --window-size 800 450 \
        --icon-size 100 \
        --icon "Ambient Assistant.app" 200 190 \
        --hide-extension "Ambient Assistant.app" \
        --app-drop-link 600 190 \
        "dist/Ambient Assistant.dmg" \
        "dist/Ambient Assistant.app"
    
    echo "DMG created at dist/Ambient Assistant.dmg"
fi

echo "Build completed successfully!"
echo "Application bundle is located at: dist/Ambient Assistant.app"
