"""
main.py - Punto de entrada principal del proyecto de Web Scraping
Orquesta la ejecución de todos los scrapers
"""

import os
import sys
from datetime import datetime
from scrapers.jockeyplaza_scraper import JockeyPlazaScraper


def create_output_dir():
    """Crea el directorio output si no existe"""
    if not os.path.exists("output"):
        os.makedirs("output")
        print("Directorio 'output' creado")


def run_scrapers():
    """Ejecuta todos los scrapers disponibles"""
    
    print("\n" + "=" * 70)
    print("SISTEMA DE WEB SCRAPING - JOCKEY PLAZA")
    print("=" * 70)
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Crear directorio de salida
    create_output_dir()
    
    # Ejecutar Jockey Plaza Scraper
    output_file = "output/jockeyplaza_tiendas.csv"
    print(f"\n[*] Iniciando scraper: Jockey Plaza")
    print(f"[*] Archivo de salida: {output_file}")
    
    try:
        scraper = JockeyPlazaScraper(headless=True)
        data = scraper.scrape(output_path=output_file)
        
        print(f"\n[OK] Scraper completado exitosamente")
        print(f"   Total registros: {len(data)}")
        
        # Mostrar vista previa
        print("\n" + "-" * 70)
        print("VISTA PREVIA DE DATOS:")
        print("-" * 70)
        if data:
            for i, store in enumerate(data[:3], 1):  # Mostrar primeros 3
                print(f"\n{i}. {store['comercio']}")
                print(f"   Web: {store['web']}")
                print(f"   Descripción: {store['descripcion'][:60]}...")
            if len(data) > 3:
                print(f"\n... y {len(data) - 3} comercios más")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante el scraping: {str(e)}")
        return False


def main():
    """Función principal"""
    try:
        success = run_scrapers()
        
        print("\n" + "=" * 70)
        if success:
            print("✅ EJECUCIÓN COMPLETADA EXITOSAMENTE")
        else:
            print("❌ EJECUCIÓN COMPLETADA CON ERRORES")
        print("=" * 70)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
