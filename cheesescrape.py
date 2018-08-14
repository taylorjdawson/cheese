from cheesey_dir.simple_request import simple_get
from bs4 import BeautifulSoup as bs
from urllib.parse import urlencode
import yaml
from multiprocessing.dummy import Pool as ThreadPool

import logging
log = logging.getLogger("cheese-logger")

url_base = 'https://www.cheese.com'
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

'https://www.cheese.com/alphabetical/?per_page=100&i=a&page=1'

def download_html():
    with open('cheesey_dir/cheese_a.html', 'w') as f:
        f.write(simple_get(url_base + urlencode()))


def load_cheese_file():
    with open('cheese_db', 'r') as f:
        return yaml.load(f.read())


# def get_parsed_html():
#     return bs(get_saved_html(), 'html.parser')

def get_name(cheese):
    return cheese.h3.a.text

def save_to_file(cheese_data):
    with open('cheese_db', 'w') as f:
        yaml.dump(cheese_data, f, default_flow_style=False)

def save_cheese_entry(cheese_entry):
    with open('test_cheese_db', 'a') as f:
        yaml.dump(cheese_entry, f, default_flow_style=False)

def get_cheese_img_url(cheese):
    return url_base + cheese.find('div', 'cheese-image-border').a.img['src']

def get_cheese_attrs(cheese):
    cheese_data = {}
    icon_to_attr = {
       'fa-flask': 'made',
       'fa-flag': 'country_origin',
       'fa-globe': 'region',
       'fa-child': 'family',
       'fa-folder-o': 'type',
       'fa-sliders': 'fat',
       'fa-pie-chart': 'texture',
       'fa-paint-brush': 'rind',
       'fa-tint': 'colour',
       'fa-spoon': 'flavour',
       'fa-leaf': 'vegetarian',
       'fa-industry': 'producers',
       'fa-cutlery': 'aroma',
       'fa-language': 'synonyms',
    }

    attrs = cheese.find('ul', 'summary-points').find_all('li')

    for attr in attrs:

        # Get icon
        icon = attr.i['class'][1]
        text = attr.text.strip()
        cheese_data[icon_to_attr[icon]] = text.split(':')[1].strip() if ':' in text else text

    return cheese_data


def get_cheese_page(letter, number):

    params = {
        'per_page': 100,
        'i': letter,
        'page': number
    }
    return bs(simple_get(url_base + '/alphabetical/?' + urlencode(params)),
              'html.parser')


def create_cheese_entry(cheese):
    cheese_entry = {}

    icon_to_attr = {
        'fa-flask': 'made',
        'fa-flag': 'country_origin',
        'fa-globe': 'region',
        'fa-child': 'family',
        'fa-folder-o': 'type',
        'fa-sliders': 'fat',
        'fa-pie-chart': 'texture',
        'fa-paint-brush': 'rind',
        'fa-tint': 'colour',
        'fa-spoon': 'flavour',
        'fa-leaf': 'vegetarian',
        'fa-industry': 'producers',
        'fa-cutlery': 'aroma',
        'fa-language': 'synonyms',
        'fa-cc': 'alt_spell',
        'fa-eyedropper': 'calcium'
    }

    attrs = cheese.find('ul', 'summary-points').find_all('li')

    for attr in attrs:

        # Get icon
        icon = attr.i['class'][1]
        text = attr.text.strip()
        try:
            attr_text = icon_to_attr[icon]
            cheese_entry[attr_text] = text.split(':')[
                1].strip() if ':' in text else text
        except KeyError as e:
            print(f'Error: {e}\nIcon: {icon}\nText: {text}')

    cheese_entry['img-url'] = get_cheese_img_url(cheese)
    cheese_entry['info'] = cheese.find('div', 'description').text.replace(
        '\n', '')

    return cheese_entry

def get_cheese_html(cheese_item):
    cheese_item_url = cheese_item.a['href']
    return bs(simple_get(url_base + cheese_item_url), 'html.parser')

def create_cheese_list():
    cheese_list = {}
    cheese_pages = {}
    for letter in alphabet:
        page_num = 1
        cheese_pages[page_num] = get_cheese_page(letter, page_num)

        # Get the number of pages (if more than one page exists)
        num_pages = 1
        if cheese_pages[page_num].find(id='id_page'):
            num_pages = len(cheese_pages[page_num].find(id='id_page').find_all('li'))

            while page_num < num_pages:
                page_num += 1
                cheese_pages[page_num] = get_cheese_page(letter, page_num)

        for (num, cheese_page) in cheese_pages.items():
            log.info(f"Processing -- Letter: {letter} Page: {num} of {num_pages}")
            print(f"Processing -- Letter: {letter} Page: {num} of {num_pages}")
            cheese_num = 1
            num_cheeses = len(cheese_page.find_all('div','cheese-item'))

            for cheese_item in cheese_page.find_all('div','cheese-item'):
                name = get_name(cheese_item)

                # Print and log process
                log.info(
                    f"\tProcessing -- Cheese: {name} {cheese_num} of {num_cheeses}")
                print(f"\tProcessing -- Cheese: {name} {cheese_num} of {num_cheeses}")

                cheese = get_cheese_html(cheese_item)
                cheese_list[name] = create_cheese_entry(cheese)

                cheese_num += 1


def create_cheese_list_threaded():

    # Make the Pool of workers
    pool = ThreadPool(6)
    # Open the urls in their own threads
    # and return the results
    pool.map(process_letter, alphabet)
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()

def process_letter(letter):
        cheese_pages = {}
        page_num = 1
        cheese_pages[page_num] = get_cheese_page(letter, page_num)

        # Get the number of pages (if more than one page exists)
        num_pages = 1
        if cheese_pages[page_num].find(id='id_page'):
            num_pages = len(cheese_pages[page_num].find(id='id_page').find_all('li'))

            while page_num < num_pages:
                page_num += 1
                cheese_pages[page_num] = get_cheese_page(letter, page_num)

        for (num, cheese_page) in cheese_pages.items():
            log.info(f"Processing -- Letter: {letter} Page: {num} of {num_pages}")
            print(f"Processing -- Letter: {letter} Page: {num} of {num_pages}")

            # Make the Pool of workers
            pool = ThreadPool(6)
            # Open the urls in their own threads
            # and return the results
            pool.map(process_cheese_item, cheese_page.find_all('div','cheese-item'))
            # close the pool and wait for the work to finish
            pool.close()
            pool.join()


def process_cheese_item(cheese_item):
    cheese = {}
    name = get_name(cheese_item)
    cheese_html = get_cheese_html(cheese_item)
    cheese[name] = create_cheese_entry(cheese_html)
    save_cheese_entry(cheese)

create_cheese_list_threaded()
