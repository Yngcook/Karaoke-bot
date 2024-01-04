import json
import csv
import os


print(f"Текущий рабочий каталог: {os.getcwd()}")


def load_links_by_user_id(file_name: str) -> dict:
    with open(file_name) as fi:
        links_by_user_id = json.load(fi)
    return links_by_user_id


def get_unique_links(file_name: str) -> list:
    with open(file_name, encoding='u8') as fi:
        unique_links = set(row['link'] for row in csv.DictReader(fi))
    return list(unique_links)
