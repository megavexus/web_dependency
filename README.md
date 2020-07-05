Script para explorar las dependencias externas de una web

## Instalación
1. Instalar el geckodriver de firefox y meterlo en el path (https://github.com/mozilla/geckodriver/releases)
2. Instalar el browsermob-proxy (viene ya en el paquete, pero bueno)
3. Instalar las dependencias (aconsejable virtualenv):
```bash
virtualenv venv -p python3
source venv/bin/activate
pip3 install requirements.txt
```

### Ejecutar
Tenemos dos archivos:
- main_request.py: Analiza las dependencias de forma estatica parseando el html
- main_selenium.py: analiza las dependencias de forma dinámica mediante browsermobproxy y selenium.


