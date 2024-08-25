import logging
import os
import sys
import time
from io import BytesIO
from dotenv import find_dotenv, load_dotenv
import re

from typing import List, Dict, Union

import pandas as pd
import requests
from PIL import Image
from fake_useragent import UserAgent

from utills.consts import NOT_FOUND_STRING, NOT_FOUND_INT, PHOTO_FIRST_ID, PHOTO_LAST_ID
from utills.url_generator import ImageUrlGenerator

load_dotenv(find_dotenv())


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

proxies = {
    'http': 'http://isaqkhag4k-res-country-DE-state-2905330-city-2925533-hold-session-session-66ad06ae31eab:tMWKuVShlInBw2OY@93.190.138.107:9999'
}


# Parsing product information on vendor code
def parse_product(vendor_codes: List[int] = None, delay: float = 0.5):
    results = {
        'Brand': [],
        'Product name': [],
        'Vendor code': [],
        'Description': [],
        'Price': [],
        'Amount of discount': [],
        'Product URL': [],
        'Number of reviews': [],
        'Rating': [],
        'Images': Dict[str, List[str]],
    }

    if vendor_codes is None or len(vendor_codes) == 0:
        vendor_codes = load_vendor_codes()

    if vendor_codes:
        for vendor_code in vendor_codes:
            time.sleep(delay)
            logger.info(f'Trying to find information on the vendor code: {vendor_code}')
            headers = {'user-agent': UserAgent(use_external_data=True).chrome}
            wb_response = requests.get(url=f'https://card.wb.ru/cards/detail'
                                           f'?appType=1&curr=rub&dest=-366541&spp=30&ab_testing=false'
                                           f'&nm={vendor_code}',
                                       headers=headers,
                                       proxies=proxies)

            wb_pics_response = requests.get(url=f'https://wildbee.pics/site/wb?id={vendor_code}',
                                            headers=headers,
                                            proxies=proxies)

            try:
                wb_response.raise_for_status()
                wb_pics_response.raise_for_status()
                wb_json_data = wb_response.json().get('data')
                if wb_json_data:
                    for product in wb_json_data.get('products'):
                        results['Brand'].append(product.get('brand', NOT_FOUND_STRING).strip("'"))
                        results['Product name'].append(product.get('name', NOT_FOUND_STRING).strip("'"))
                        results['Vendor code'].append(vendor_code)
                        results['Price'].append(process_price_number(product.get('priceU', NOT_FOUND_INT) // 100))
                        results['Amount of discount'].append(
                            process_price_number(product.get('salePriceU', NOT_FOUND_INT) // 100))
                        results['Product URL'].append(f'https://www.wildberries.ru/catalog/{vendor_code}/detail.aspx')
                        results['Number of reviews'].append(product.get('feedbacks', NOT_FOUND_INT))
                        results['Rating'].append(product.get('rating', NOT_FOUND_INT))
                results['Description'].append(wb_pics_response.json().get('description', NOT_FOUND_STRING))
            except requests.exceptions.HTTPError:
                logger.warning(f'Failed to get info from vendor code: {vendor_code}')
            except AttributeError as e:
                logger.error(f'Failed to parse vendor code {vendor_code} cause of: {e}')
        # write_to_xlsx(results)
        results['Images'] = download_and_unzip_files(vendor_codes, headers)
    else:
        logger.critical('Failed to load data!')

    return results


def process_price_number(price: int) -> str:
    result = ""
    while price != 0:
        a = price % 1000
        result = f" {'000' if a == 0 else a}" + result
        price //= 1000
    return result.strip()


def replace_sensitive_symbols(text: str) -> str:
    return re.sub(r"([-_*\[\]()~>#+=|{}.!])", r"\\\1", text)


# Loading vendor codes from file
def load_vendor_codes(file_path: str = f"{os.getenv('ROOT_PATH')}{os.getenv('VENDOR_CODES_FILE')}") -> \
        List[int]:
    try:
        with open(file_path, 'r') as open_file:
            lines = [int(result.strip()) for result in open_file.readlines()]
        if lines:
            return lines
        raise ValueError('Failed to get vendor codes from file. File "vendor_codes.txt" is empty')
    except FileNotFoundError:
        logger.critical(f'File "vendor_codes.txt" is not found!')
    except ValueError:
        logger.critical('Failed to parce vendor codes in "vendor_codes.txt". It have to be a number values')


# Writing parsed datas to xlsx file
def write_to_xlsx(data: Dict[str, List[Union[int, str, float]]],
                  file_name: str = f'{os.getenv('ROOT_PATH')}{os.getenv('PRODUCT_INFO_PATH')}{os.getenv('PRODUCT_INFO_TABLE')}',
                  sheet_name: str = 'wildberries') -> None:
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False, sheet_name=sheet_name)


def download_and_unzip_files(vendor_codes: List[int], headers) -> Dict[str, List[str]]:
    result = {}

    for vendor_code in vendor_codes:

        # Создаем директорию для vendor_code, если ее нет
        directory = f'{os.getenv('ROOT_PATH')}{os.getenv('PRODUCT_INFO_PATH')}\\{vendor_code}'
        os.makedirs(directory, exist_ok=True)

        imageGenerator = ImageUrlGenerator(nmId=vendor_code)
        imageGenerator.generate_url()

        images_urls = []

        for i in range(PHOTO_FIRST_ID, PHOTO_LAST_ID):

            generatedUrl = imageGenerator.change_photo_number(i)

            try:
                response = requests.get(url=generatedUrl, headers=headers, proxies=proxies)
                response.raise_for_status()

                image = Image.open(BytesIO(response.content))
                filename = f'{os.getenv('ROOT_PATH')}{os.getenv('PRODUCT_INFO_PATH')}\\{vendor_code}\\{i}.jpg'
                images_urls.append(filename)
                rgb_im = image.convert('RGB')
                rgb_im.save(filename)

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download image by id {i} of vendor's code {vendor_code}: {e}")
                break

        result[f'{vendor_code}'] = images_urls

        logger.info(f"All images of vendor code {vendor_code} was successfully downloaded")

        return result


def create_product_info(vendor_codes: List[int]):
    return parse_product(vendor_codes)


if __name__ == "__main__":
    parse_product()
