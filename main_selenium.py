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


def get_dependencies(url):
    browsermobproxy_location = "browsermob-proxy/bin/browsermob-proxy"
    clean_opened_processes()
    server = Server(browsermobproxy_location)
    server.start()
    time.sleep(0.5)

    proxy = server.create_proxy()
    time.sleep(0.5)

    options = Options()
    options.headless = True

    profile  = webdriver.FirefoxProfile()
    profile.set_proxy(proxy.selenium_proxy())

    driver = webdriver.Firefox(options=options, firefox_profile=profile)
    proxy.new_har("captured_elems")
    driver.get(url)
    time.sleep(3)

    resources = [elem["request"]["url"] for elem in proxy.har["log"]["entries"] ]

    server.stop()
    driver.quit()

    resources = list(set(resources)) # eliminamos duplicados
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
