import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

from PIL import Image
from io import BytesIO

def get_page_urls():
    file_path = "./urls.txt"
    with open(file_path) as f:
        page_urls = f.readlines()
    return page_urls

def create_folder_path(viewtype, domain):
    folder_path = "./" + str(domain) + "/screenshots-" + str(viewtype)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def open_firefox(width):
    driver = webdriver.Firefox()
    driver.set_window_size(width,768)
    return driver

def get_page_dimensions_og(driver):
    return driver.execute_script("return {width: document.body.scrollWidth, height: document.documentElement.scrollHeight};")

def get_page_dimensions(driver, page_url):
    driver.get(page_url)
    footer = driver.find_element("css selector", ".elementor-location-footer")
    dimensions_og = driver.execute_script("return {width: document.body.scrollWidth, height: document.documentElement.scrollHeight};")
    driver.execute_script("arguments[0].style.marginBottom = '768px';", footer)
    return driver.execute_script("return {width: document.body.scrollWidth, height: document.documentElement.scrollHeight};")

def get_header_image(driver):
    header = driver.find_element("css selector", ".elementor-location-header")
    return Image.open(BytesIO(driver.get_screenshot_as_png()))

def hide_header_image(driver):
    header = driver.find_element("css selector", ".elementor-location-header")
    driver.execute_script("arguments[0].style.opacity = 0;", header)
    return driver

def take_screenshot(driver, dimensions):
    image = Image.new("RGB", (dimensions["width"], dimensions["height"]))
    visible_height = driver.execute_script("return window.innerHeight;")
    y = 0
    while y < dimensions["height"]:
        driver.execute_script("window.scrollTo(0, {});".format(y))
        screenshot = Image.open(BytesIO(driver.get_screenshot_as_png()))
        image.paste(screenshot, (0, y))
        y += visible_height
    return image

def crop_screenshot(image, dimensions, width):
    left = 0
    top = 0
    right = width
    bottom = dimensions_og["height"] - 768
    return image.crop((left, top, right, bottom))

def save_screenshot(image, folder_path, page_url):
    filename = page_url.replace("/", "_").replace(":", "") + ".png"
    image.save(os.path.join(folder_path, filename))

if __name__ == "__main__":
    page_urls = get_page_urls()
    for viewtype in ['desktop', 'mobile', 'tablet']:
        width = 1920 if viewtype == 'desktop' else (420 if viewtype == 'mobile' else 768)
        driver = open_firefox(width)
        for page_url in page_urls:

            regex = r"(http[s]?://)([\w.-]+)"
            match = re.search(regex, page_url)
            domain = match.group(2)
            folder_path = create_folder_path(viewtype, domain)
            
            dimensions = get_page_dimensions(driver, page_url)
            header_image = get_header_image(driver)
            hide_header_image(driver)
            image = take_screenshot(driver, dimensions)
            image.paste(header_image, (0, 0))
            dimensions_og = get_page_dimensions_og(driver)
            image = crop_screenshot(image, get_page_dimensions_og, width)
            save_screenshot(image, folder_path, page_url)
