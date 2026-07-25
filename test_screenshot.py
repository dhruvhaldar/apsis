from playwright.sync_api import sync_playwright
import time
import subprocess

def run():
    server = subprocess.Popen(["python3", "-m", "http.server", "8010", "-d", "public"])
    time.sleep(1)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8010')
        time.sleep(1)
        page.screenshot(path='screenshot.png')
        browser.close()
    server.terminate()

run()
