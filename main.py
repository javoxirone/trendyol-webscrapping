import json
from pprint import pprint
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

# starting new html session
session = HTMLSession()

# getting web page
r = session.get(
    "https://www.trendyol.com/altinyildiz-classics/erkek-koyu-gri-slim-fit-bisiklet-yaka-pamuklu-kisa-kollu-tisort-p-224009683")

# rendering js rendered elements
r.html.render(timeout=50)
# bs4 html parsing
soup = BeautifulSoup(r.html.html, 'html.parser')
# getting basic info
title = soup.find('h1', class_='pr-new-br').get_text(strip=True)
price = soup.find('span', class_='prc-dsc').get_text(strip=True)
description_text = soup.find('ul', class_='detail-desc-list').get_text(strip=True)
# getting js rendered images in slider
images_block = soup.find_all('a', class_='slc-img')

# creating dict
colors = {
    "title": title,
    "price": price,
    "renk": [],
    "description": description_text,
    "characteristics": {},
    "products": {}
}
pprint(colors)

# getting product's characteristics
characters_list = soup.find_all('ul', class_='detail-attr-container')
for character_list in characters_list:
    details = character_list.find_all('li', class_='detail-attr-item')
    for detail in details:
        # getting key and value from list item
        key, value = detail.find_all('span')
        # setting similar key and value if there is no key text
        if key.text == '':
            colors["characteristics"][value.text] = value.text
        else:
            colors["characteristics"][key.text] = value.text
pprint(colors)

# getting image source and their sizes
for image in images_block:
    # creating link for each product color
    color_link = f"https://www.trendyol.com{image['href']}"
    # creating HTMLSession
    color_session = HTMLSession()
    color = color_session.get(color_link)
    # rendering js elements
    color.html.render(timeout=50)

    # getting html rendered sizes (elements)
    color_html = requests.get(color_link).text
    color_soup = BeautifulSoup(color.html.html, "html.parser")
    color_html_soup = BeautifulSoup(color_html, "html.parser")
    # dict for different colored products with image and size list
    colors["products"][image['title']] = {"images": [], "sizes": []}
    # getting sizes block
    sizes_block = color_html_soup.find('div', class_='variants')
    # getting all sizes
    sizes = sizes_block.find_all('div', class_='sp-itm')

    # parsing all sizes
    for size in sizes:
        if 'so' not in size['class']:
            colors["products"][image['title']]["sizes"].append([size.text, True])
        else:
            colors["products"][image['title']]["sizes"].append([size.text, False])

    # getting all detailed images of one color product
    detailed_images = color_soup.find_all('div', class_='product-slide')
    for detailed_image in detailed_images:
        colors["products"][image['title']]['images'].append(detailed_image.find('img')['src'])
    image_link = image.find('img')['src'] if image.find('img') else ''

    # gathering different colors of one product into the list
    colors['renk'].append(image_link)
pprint(colors)

# saving all info to json
with open(f'trendyol.json', mode='w', encoding='utf-8') as file:
    json.dump(colors, file, ensure_ascii=False, indent=4)
