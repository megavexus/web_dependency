from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from browsermobproxy import Server
from urllib.parse import urlparse

import os
import time
import psutil
import logging
import click
import hashlib

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

class DepencyGetter():
    def __init__(self) -> None:
        self.initialize_mobproxy()
        self.create_webdriver()

    def __exit__(self):
        self.driver.quit()
        self.server.stop()
        self.clean_opened_processes()
        logger.info('salida limpia')

    def clean_opened_processes(self):
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == "browsermob-proxy":
                proc.kill()

    def initialize_mobproxy(self):
        browsermobproxy_location = "browsermob-proxy/bin/browsermob-proxy"
        self.server = Server(browsermobproxy_location)
        logger.info("> Levantando servidor BrowerMobProxy")
        self.server.start()
    
    def create_webdriver(self):
        self.proxy = self.server.create_proxy()
        time.sleep(0.5)

        options = Options()
        options.headless = True
        proxy_host = self.proxy.host.split(":")[1].replace('/','')
        proxy_port = self.proxy.port
        
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
        self.driver = webdriver.Firefox(options=options)

    def get_dependencies(self, url):
        self.proxy.new_har("captured_elems")
        logger.info(f"> Obteniendo URL {url}")
        self.driver.get(url)
        logger.info(f"\t DONE!")
        time.sleep(3)
        resources = dict () 
        for elem in self.proxy.har["log"]["entries"]:
            urldep = elem["request"]["url"]
            resources[urldep] = {
                'date' : elem["startedDateTime"],
                'urlfather' : url,
                'depdomain' : urlparse(urldep).netloc,
                'ip' : elem["serverIPAddress"],
                'status' : elem["response"]["status"],
                'size' : elem["response"]["bodySize"],
                'mimetype' : elem["response"]["content"]["mimeType"],
                'hash_sha1' : self.getHashOfUrl(urldep)
            }
        raise Exception (resources)
        logger.info(f"> Recursos obtenidos {len(resources)}")
        return resources

    def getHashOfUrl(self, url):
        self.driver.get(url)
        content = self.driver.page_source
        h = hashlib.new('sha1')
        h.update(content.encode('utf8'))
        hash = h.hexdigest()
        return hash

@click.command()
@click.option('--url', '-u', required=True, type=str, multiple=True)
@click.option('--output_file', '-o', type=click.Path())
def main(url, output_file):
    depencygetter = DepencyGetter()

    for link in url: 
        dependencies = depencygetter.get_dependencies(link)
        print(f"- Dependencies for [{link}]:")
        for dep in dependencies:
            print(f"\t - {dep}")
            #pprint(dependencies)

if __name__ == "__main__":
    main()
