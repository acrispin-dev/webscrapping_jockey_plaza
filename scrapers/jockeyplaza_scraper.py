"""
Web Scraper para Jockey Plaza - Extrae información de comercios
https://jockeyplaza.com.pe/tiendas

Extrae: Nombre del comercio, Descripción y URL del sitio web
"""

import time
import csv
import os
import sys
import urllib.parse
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from bs4 import BeautifulSoup
import shutil


class JockeyPlazaScraper:
    """Scraper para jockeyplaza.com.pe"""
    
    BASE_URL = "https://jockeyplaza.com.pe"
    TIENDAS_URL = f"{BASE_URL}/tiendas"
    
    def __init__(self, headless=True):
        """
        Inicializa el scraper
        
        Args:
            headless: Si es True, ejecuta Chrome sin interfaz gráfica
        """
        self.headless = headless
        self.driver = None
        self.stores_data = []
        
    def _init_driver(self):
        """Inicializa el driver de Selenium"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            print("Descargando ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Error con webdriver-manager: {str(e)}")
            print("Intentando usar Chrome sin webdriver-manager...")
            
            # Intenta directo con Chrome sin Service
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")  # Usar new headless para mejor compatibilidad
            options.add_argument("--start-maximized")  # Crucial para que Angular renderice bien
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            try:
                self.driver = webdriver.Chrome(options=options)
            except Exception as e2:
                print(f"Error inicializando Chrome: {str(e2)}")
                raise Exception("No se pudo inicializar el navegador Chrome. Asegúrate de tener Chrome instalado.")
        
    def _get_store_links(self) -> List[str]:
        """
        Extrae todos los enlaces de las tiendas desde la página principal con paginación
        Detecta duplicados para evitar loops infinitos
        
        Returns:
            Lista de URLs de tiendas
        """
        print(f"Accediendo a {self.TIENDAS_URL}...")
        self.driver.get(self.TIENDAS_URL)
        
        # Esperar a que carguen las cards
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "card__item"))
            )
        except TimeoutException:
            print("Timeout esperando las cards. Continuando...")
        
        # Esperar adicional para asegurar renderización completa
        time.sleep(2)
        
        all_store_links = []
        seen_links = set()  # Para detectar duplicados
        page = 1
        max_pages = 50  # Límite de seguridad
        consecutive_duplicates = 0  # Contador de páginas con duplicados consecutivos
        
        while page <= max_pages:
            print(f"\n📄 Página {page}")
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Buscar todos los cards en la página actual
            cards = soup.find_all("div", class_="card__item")
            print(f"   Se encontraron {len(cards)} cards en esta página")
            
            if len(cards) == 0:
                print(f"   ✓ No hay más tiendas")
                break
            
            # Rastrear si esta página tiene items nuevos
            page_has_new_items = False
            
            for card in cards:
                # Buscar el link dentro del card
                link_elem = card.find("a", class_="card__container__icons__icon")
                if link_elem and link_elem.get("href"):
                    href = link_elem.get("href")
                    full_url = self.BASE_URL + href
                    
                    # Verificar si es nuevo
                    if full_url not in seen_links:
                        all_store_links.append(full_url)
                        seen_links.add(full_url)
                        page_has_new_items = True
                        print(f"   ✓ {href}")
                    else:
                        print(f"   ⚠ {href} (duplicado)")
            
            # # Si la página solo tiene items que ya vimos, incrementar contador de duplicados
            # if not page_has_new_items:
            #     consecutive_duplicates += 1
            #     print(f"   ⚠ Página con solo duplicados ({consecutive_duplicates} consecutivas)")
            #     if consecutive_duplicates >= 2:
            #         print(f"   ✓ Fin de paginación: Se detectaron 2 páginas consecutivas con solo duplicados")
            #         break
            # else:
            #     consecutive_duplicates = 0  # Reset si encontramos nuevos items
            
            # Buscar y hacer click en botón siguiente
            try:
                # Buscar el botón siguiente usando Selenium
                next_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "a.page-link.icon__stroke"
                )

                next_button = None

                for btn in next_buttons:
                    try:
                        d_attr = btn.find_element(By.TAG_NAME, "path").get_attribute("d") or ""

                        is_next_button = d_attr.startswith("M8.91003") or "L15.43" in d_attr

                        if is_next_button:
                            parent_li = btn.find_element(By.XPATH, "./parent::li")
                            parent_class = parent_li.get_attribute("class") or ""
                            btn_class = btn.get_attribute("class") or ""

                            if "disabled" not in parent_class.lower() and "disabled" not in btn_class.lower():
                                next_button = btn
                                break

                    except Exception:
                        continue
                
                if next_button and next_button.is_enabled():
                    print(f"   ▶ Navegando a página siguiente...")
                    # Scroll a la paginación y click usando JavaScript (más confiable)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(1)
                    
                    # Usar JavaScript click para evitar interceptación
                    self.driver.execute_script("arguments[0].click();", next_button)
                    
                    # Esperar a que carguen las nuevas cards
                    time.sleep(2)
                    try:
                        WebDriverWait(self.driver, 15).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "card__item"))
                        )
                    except TimeoutException:
                        print("   ⚠ Timeout esperando cards después de click")
                    
                    time.sleep(2)
                    
                    page += 1
                else:
                    print(f"   ✓ No hay más páginas (botón siguiente deshabilitado)")
                    break
                    
            except Exception as e:
                print(f"   ✓ Fin de paginación: {str(e)[:60]}...")
                break
        
        print(f"\n{'='*70}")
        print(f"✅ Total de tiendas únicas encontradas: {len(all_store_links)}")
        print(f"{'='*70}")
        
        return all_store_links
    
    def _extract_store_info(self, store_url: str) -> Dict:
        """
        Extrae información de una tienda individual
        
        Args:
            store_url: URL de la tienda
            
        Returns:
            Diccionario con los datos del comercio
        """
        try:
            self.driver.get(store_url)
            
            # Esperar a que cargue el contenido
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "container__detail__info__card"))
                )
            except TimeoutException:
                pass
            
            time.sleep(0.5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # ========== NOMBRE DEL COMERCIO (desde URL) ==========
            store_name = "N/A"
            try:
                url_parts = store_url.split('/tiendas/')
                if len(url_parts) > 1:
                    encoded_name = url_parts[1].strip('/')
                    store_name = encoded_name
                    prev = None
                    while store_name != prev:
                        prev = store_name
                        store_name = urllib.parse.unquote(store_name)
                    store_name = store_name.strip()
            except Exception as e:
                pass
            
            # ========== DESCRIPCIÓN ==========
            store_description = "N/A"
            try:
                # Buscar en spans la descripción (la que dice "Somos", "Marca", etc)
                for span in soup.find_all("span"):
                    text = span.get_text(strip=True)
                    if len(text) > 40:  # Debe ser texto suficientemente largo
                        # Palabras clave para identificar descripción
                        keywords = ["somos", "marca", "tienda", "empresa", "especializado", "dedicado", "ofrece"]
                        if any(kw in text.lower() for kw in keywords):
                            store_description = text
                            break
                
                # Si no encuentra con keywords, tomar primer span largo
                if store_description == "N/A":
                    for span in soup.find_all("span"):
                        text = span.get_text(strip=True)
                        if len(text) > 50:
                            store_description = text
                            break
            except Exception as e:
                pass
            
            # ========== URL DEL COMERCIO (con icono code.svg) ==========
            store_web = "N/A"
            try:
                info_cards = soup.find_all("article", class_="container__detail__info__card")
                for article in info_cards:
                    link = article.find("a", class_="url__element")
                    if link:
                        img = link.find("img")
                        if img and "code.svg" in img.get("src", ""):
                            span = link.find("span")
                            if span:
                                store_web = span.get_text(strip=True)
                                break
            except Exception as e:
                pass
            
            store_info = {
                "comercio": store_name,
                "descripcion": store_description,
                "web": store_web,
                "url_origen": store_url
            }
            
            return store_info
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return {
                "comercio": "Error",
                "descripcion": "Error al extraer datos",
                "web": "N/A",
                "url_origen": store_url
            }
    
    def scrape(self, output_path: str = None) -> List[Dict]:
        """
        Ejecuta el proceso completo de scraping
        
        Args:
            output_path: Ruta donde guardar el CSV resultante
            
        Returns:
            Lista de diccionarios con los datos extraídos
        """
        try:
            print("=" * 70)
            print("INICIANDO SCRAPING DE JOCKEY PLAZA - CON PAGINACIÓN")
            print("=" * 70)
            
            self._init_driver()
            print("✅ Navegador iniciado correctamente\n")
            
            # Obtener enlaces de tiendas (con paginación)
            store_links = self._get_store_links()
            print(f"\n{'='*70}")
            print(f"Total de tiendas a procesar: {len(store_links)}")
            print(f"{'='*70}\n")
            
            # Extraer información de cada tienda
            for i, link in enumerate(store_links, 1):
                print(f"[{i}/{len(store_links)}] Procesando: {link.split('/tiendas/')[-1]}")
                store_info = self._extract_store_info(link)
                self.stores_data.append(store_info)
                
                # Mostrar resumen
                print(f"  ✓ {store_info['comercio']}")
                if store_info['web'] != 'N/A':
                    print(f"    Web: {store_info['web']}")
                
                # Pausa para no sobrecargar
                time.sleep(0.5)
            
            # Guardar resultados
            if output_path:
                self._save_to_csv(output_path)
            
            print("\n" + "=" * 70)
            print("✅ SCRAPING COMPLETADO")
            print("=" * 70)
            print(f"Total de comercios extraídos: {len(self.stores_data)}")
            
            return self.stores_data
            
        except Exception as e:
            print(f"\n❌ Error durante scraping: {str(e)}")
            raise
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def _save_to_csv(self, output_path: str):
        """
        Guarda los datos en un archivo CSV
        
        Args:
            output_path: Ruta del archivo CSV
        """
        if not self.stores_data:
            print("No hay datos para guardar")
            return
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['comercio', 'descripcion', 'web', 'url_origen']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(self.stores_data)
            
            print(f"\nDatos guardados en: {output_path}")
        except Exception as e:
            print(f"Error guardando CSV: {str(e)}")
    
    def get_data(self) -> List[Dict]:
        """Retorna los datos extraídos"""
        return self.stores_data


if __name__ == "__main__":
    scraper = JockeyPlazaScraper(headless=True)
    scraper.scrape(output_path="output/jockeyplaza_tiendas.csv")
