from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from browsermobproxy import Server

import os
import time
import psutil
import logging

from pprint import pprint

def create_logger(app_name):
    """Create a logging interface"""
    logging_level = os.getenv('LOGLEVEL', logging.INFO)
    logging.basicConfig(
        level=logging_level,
        format='(%(asctime)s): [%(levelname)s]:%(name)s - %(message)s')
    logger = logging.getLogger(app_name)
    return logger

logger = create_logger("dependency_web_checker")

def clean_opened_processes():
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == "browsermob-proxy":
            proc.kill()


def create_mobproxy():
    browsermobproxy_location = "browsermob-proxy/bin/browsermob-proxy"
    server = Server(browsermobproxy_location)
    logger.info("> Levantando servidor BrowerMobProxy")
    server.start()
    return server


def get_dependencies(url):
    clean_opened_processes()
    time.sleep(0.5)

    server = create_mobproxy()
    proxy = server.create_proxy()
    time.sleep(0.5)

    options = Options()
    options.headless = True
    proxy_host = proxy.host.split(":")[1].replace('/','')
    proxy_port = proxy.port
    
    options.set_preference('dom.file.createInChild', False)
    options.set_preference('browser.download.folderList', False)
    options.set_preference('browser.download.manager.showWhenStarting', False)
    options.set_preference('pdfjs.disabled', False)

    options.set_preference('network.proxy.type', 1)
    options.set_preference('network.proxy.http', proxy_host)
    options.set_preference('network.proxy.http_port', proxy_port)
    options.set_preference('network.proxy.ssl', proxy_host)
    options.set_preference('network.proxy.ssl_port', proxy_port)
    #options.set_preference('network.proxy.socks', proxy_host)
    #options.set_preference('network.proxy.socks_port', proxy_port)
    #options.set_preference('network.proxy.socks_remote_dns', False)

    logger.info(f"> Configurando Selenium para usar de proxy {proxy_host}:{proxy_port}")
    driver = webdriver.Firefox(options=options)

    proxy.new_har("captured_elems")
    logger.info(f"> Obteniendo URL {url}")
    try:
        driver.get(url)
        logger.info(f"\t DONE!")
        time.sleep(3)
    except:
        server.stop()
        driver.quit()
        clean_opened_processes()
        raise


    resources = [elem["request"]["url"] for elem in proxy.har["log"]["entries"] ]

    server.stop()
    driver.quit()
    logger.info(f"> Cerrando server")

    resources = list(set(resources)) # eliminamos duplicados
    logger.info(f"> Recursos obtenidos {len(resources)}")
    return resources

def main():
    url = 'https://www.google.com/'
    dependencies = get_dependencies(url)
    print(f"- Dependencies for [{url}]:")
    for dep in dependencies:
        print(f"\t - {dep}")
        #pprint(dependencies)

if __name__ == "__main__":
    main()
