import logging
import sys
import time
from io import BytesIO
import os
from typing import List, Dict, Union

import pandas as pd
import requests
from PIL import Image
from fake_useragent import UserAgent

from constants import NOT_FOUND_STRING, NOT_FOUND_INT
from url_generator import GenerateImgUrl

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
def parse_product(delay: float = 0.5) -> None:
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
    }

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
                        results['Brand'].append(product.get('brand', NOT_FOUND_STRING))
                        results['Product name'].append(product.get('name', NOT_FOUND_STRING))
                        results['Vendor code'].append(vendor_code)
                        results['Price'].append(product.get('priceU', NOT_FOUND_STRING) / 100)
                        results['Amount of discount'].append(product.get('salePriceU', NOT_FOUND_STRING) / 100)
                        results['Product URL'].append(f'https://www.wildberries.ru/catalog/{vendor_code}/detail.aspx')
                        results['Number of reviews'].append(product.get('feedbacks', NOT_FOUND_INT))
                        results['Rating'].append(product.get('rating', NOT_FOUND_INT))
                results['Description'].append(wb_pics_response.json().get('description', NOT_FOUND_STRING))
            except requests.exceptions.HTTPError:
                logger.warning('Failed to get info from vendor code: {vendor_code}')
            except AttributeError as e:
                logger.error('Failed to parse vendor code {vendor_code} cause of: {e}')
        write_to_xlsx(results)
        download_and_unzip_files(vendor_codes, headers)
    else:
        logger.critical('Failed to load data!')


# Loading vendor codes from file
def load_vendor_codes(file_path: str = "C:\\Users\\Youngstanislav\\PycharmProjects\\parsing-wb\\vendor_codes.txt") -> \
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
                  file_name: str = 'C:\\Users\\Youngstanislav\\PycharmProjects\\parsing-wb\\product info\\product_info_table.xlsx',
                  sheet_name: str = 'wildberries') -> None:
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False, sheet_name=sheet_name)


def download_and_unzip_files(vendor_codes: List[int], headers) -> None:
    for vendor_code in vendor_codes:

        # Создаем директорию для vendor_code, если ее нет
        directory = f'C:\\Users\\Youngstanislav\\PycharmProjects\\parsing-wb\\product info\\{vendor_code}'
        os.makedirs(directory, exist_ok=True)

        found_image = False

        for i in range(8):

            generator = GenerateImgUrl(nmId=vendor_code, photoNumber=i)

            generatedUrl = generator.url()

            try:
                response = requests.get(url=generatedUrl,
                                        headers=headers,
                                        proxies=proxies)
                response.raise_for_status()

                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    filename = f'C:\\Users\\Youngstanislav\\PycharmProjects\\parsing-wb\\product info\\{vendor_code}\\{i}.png'
                    image.save(filename)
                    print(f"Изображение {i} для {vendor_code} успешно скачано")
                else:
                    print(f"Изображение {i} для {vendor_code} не найдено")
                    break  # Выходим из цикла, если изображение не найдено

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при загрузке изображения {i} для {vendor_code}: {e}")


if __name__ == "__main__":
    parse_product()
