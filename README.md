# Web Scraping Project - Jockey Plaza

Proyecto de web scraping en Python para extraer información de comercios de Jockey Plaza Perú.

## 📋 Descripción

Sistema de scraping que extrae información de comercios del sitio https://jockeyplaza.com.pe/tiendas

**Datos extraídos:**
- Nombre del comercio
- Descripción del comercio
- Sitio web oficial

## 📁 Estructura del Proyecto

```
WebScrappingStores/
├── scrapers/              # Scripts de scraping para diferentes webs
│   ├── __init__.py
│   └── jockeyplaza_scraper.py   # Scraper para Jockey Plaza
├── output/                # Resultados en CSV
│   └── jockeyplaza_tiendas.csv
├── venv/                  # Entorno virtual (se crea con setup)
├── main.py               # Punto de entrada principal
├── requirements.txt      # Dependencias del proyecto
├── setup_venv.bat        # Script para configurar el entorno
└── README.md            # Este archivo
```

## 🚀 Guía de Inicio Rápido

### 1. Configuración Inicial (Primera vez)

En PowerShell o Command Prompt, ejecuta:

```bash
cd d:\1ALVARO\YAPE\WebScrappingStores
setup_venv.bat
```

Esto:
- Crea un entorno virtual Python
- Instala todas las dependencias necesarias

### 2. Activar el Entorno Virtual

Cada vez que trabajes en el proyecto:

```bash
venv\Scripts\activate.bat
```

Verás `(venv)` en el prompt cuando esté activo.

### 3. Ejecutar el Scraper

```bash
python main.py
```

## 📦 Dependencias Principales

- **selenium 4.15.2** - Automatización de navegador, maneja JavaScript
- **beautifulsoup4 4.12.2** - Parsing de HTML
- **requests 2.31.0** - Peticiones HTTP
- **pandas 2.1.3** - Manipulación de datos
- **webdriver-manager 4.0.1** - Gestión de ChromeDriver

## 🔧 Detalles Técnicos

### JockeyPlazaScraper

El scraper utiliza Selenium por dos razones principales:
1. La página es una aplicación Angular que carga contenido dinámicamente
2. Necesita esperar a que el JavaScript se ejecute para obtener el HTML

**Metodología:**
1. Abre la página de tiendas (https://jockeyplaza.com.pe/tiendas)
2. Extrae todos los enlaces de las cards de tiendas
3. Para cada tienda:
   - Accede a su página individual
   - Extrae el nombre, descripción y URL web
   - Busca específicamente el link con el icono "code.svg" para la web

### Salida

El archivo CSV generado (`output/jockeyplaza_tiendas.csv`) contiene:

| comercio | descripcion | web | url_origen |
|----------|-----------|-----|-----------|
| SIFRAH - NAVE CENTRAL | Somos una compañía de moda... | https://www.besifrah.com/ | https://jockeyplaza.com.pe/tiendas/... |

## 📝 Extensión del Proyecto

Para agregar un nuevo scraper:

1. Crea un nuevo archivo en `scrapers/nuevo_scraper.py`:

```python
class NuevoScraper:
    def scrape(self, output_path):
        # Tu lógica de scraping
        pass
```

2. Importa y ejecuta en `main.py`:

```python
from scrapers.nuevo_scraper import NuevoScraper
scraper = NuevoScraper()
scraper.scrape(output_path="output/nuevo_resultado.csv")
```

## ⚠️ Consideraciones Importantes

- **Comportamiento ético**: El scraper incluye delays entre requests
- **User-Agent**: Se configura un user-agent realista
- **Headless**: Por defecto ejecuta Chrome sin interfaz gráfica
- **Timeouts**: Incluye manejo de timeouts para conexiones lentas

## 🐛 Solución de Problemas

### Chrome no se abre
- El script descarga automáticamente ChromeDriver compatible
- Si hay problemas, instala Chrome versión reciente

### Timeout esperando elementos
- Aumenta los valores de timeout en el scraper si la web es lenta
- Verifica tu conexión a internet

### CSV vacío
- Verifica que la estructura HTML de la web no haya cambiado
- Abre https://jockeyplaza.com.pe/tiendas en navegador para inspeccionar

## 📧 Notas de Desarrollo

- Los datos se guardan con encoding UTF-8 para soportar caracteres especiales
- Hay esperas de 1-2 segundos entre acciones para evitar bloqueos
- El scraper es resistente a errores individuales (si falla una tienda, continúa)

## ✅ Próximos Pasos

- [ ] Agregar logging más detallado
- [ ] Implementar reintentos automáticos
- [ ] Agregar validación de datos
- [ ] Crear scrapers adicionales para otras webs
- [ ] Agregar tests unitarios
