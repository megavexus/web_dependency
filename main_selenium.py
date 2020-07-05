from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from browsermobproxy import Server
import psutil
import time
from pprint import pprint

def clean_opened_processes():
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == "browsermob-proxy":
            proc.kill()

url = 'https://www.google.com/'

clean_opened_processes()
server = Server("browsermob-proxy/bin/browsermob-proxy")
server.start()
time.sleep(1)

proxy = server.create_proxy()
time.sleep(1)

options = Options()
options.headless = True

profile  = webdriver.FirefoxProfile()
profile.set_proxy(proxy.selenium_proxy())

driver = webdriver.Firefox(options=options, firefox_profile=profile)
proxy.new_har("captured_elems")
driver.get(url)
time.sleep(5)

resources = [elem["request"]["url"] for elem in proxy.har["log"]["entries"]]
#print (proxy.har) # returns a HAR JSON blob
pprint (resources) # returns a HAR JSON blob

server.stop()
driver.quit()