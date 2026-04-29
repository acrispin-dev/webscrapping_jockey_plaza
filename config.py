"""
Utilidades y configuración del proyecto
"""

import os
import sys
from pathlib import Path

# Configuración del proyecto
PROJECT_ROOT = Path(__file__).parent.resolve()
SCRAPERS_DIR = PROJECT_ROOT / "scrapers"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Crear directorios si no existen
OUTPUT_DIR.mkdir(exist_ok=True)

# Logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = OUTPUT_DIR / "scraping.log"

def get_project_root():
    """Retorna la raíz del proyecto"""
    return PROJECT_ROOT

def get_output_dir():
    """Retorna el directorio de output"""
    return OUTPUT_DIR

def get_scrapers_dir():
    """Retorna el directorio de scrapers"""
    return SCRAPERS_DIR
