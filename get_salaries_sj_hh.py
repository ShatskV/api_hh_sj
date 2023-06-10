import json
import os
from datetime import datetime, timedelta

import requests
# from requests.exceptions import HTTPError
from dotenv import load_dotenv
from terminaltables import AsciiTable

PROGRAM_LANGUAGES = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'CSS', 'C#', 'GO']


def predict_salary(salary_from, salary_to):
    if salary_from:
        if salary_to:
            return int((salary_from + salary_to) / 2)
        return int(salary_from * 1.2)

    return int(salary_to *  0.8)
        

def predict_rub_salary_hh(vacancy):
    salary = vacancy.get("salary")
    if not salary:
        return
    salary_from = salary.get('from')
    salary_to = salary.get('to')
    currency = salary.get('currency')
    if currency != "RUR":
        return
    salary = predict_salary(salary_from, salary_to)

    return salary


def predict_rub_salary_sj(vacancy):
    salary_from = vacancy.get("payment_from")
    salary_to = vacancy.get("payment_to")
    if vacancy.get('currency') != 'rub' or not(salary_from or salary_to):
        return
    salary = predict_salary(salary_from, salary_to)
    return salary


def get_sj_vacancies(code, token):
    vacancies_per_page = 100
    page = 0
    moscow_id = 4
    it_catalogue_id = 33
    more_results = True
    vacancies = []
    timestamp_1_month_ago = (datetime.now() - timedelta(days=31)).timestamp()
    params = {
        'keyword': 'программист',
        'count': vacancies_per_page,
        'catalogues': it_catalogue_id,
        'date_published_from': timestamp_1_month_ago,
        'town': moscow_id
    }
    headers = {'X-Api-App-Id': code,
               'Authorization':  f'Bearer {token}'
               'Content-Type:' 'application/json'}
    while more_results:
        params['page'] = page
        response = requests.get('https://api.superjob.ru/2.0/vacancies/', params=params, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        vacancies += response_json.get('objects', [])
        more_results = response_json.get('more')
    return vacancies


def get_sj_salaries(language, vacancies):
    sorted_vacancies = [vacancy for vacancy in vacancies if language.lower() in vacancy.get('candidat', '')]
    vacancies_processed = 0
    all_vacancies = len(sorted_vacancies)
    sum_salary = 0
    for vacancy in sorted_vacancies:
        salary = predict_rub_salary_sj(vacancy)
        if salary:
            sum_salary += salary
            vacancies_processed += 1
    avg_salary = int(sum_salary / vacancies_processed) if vacancies_processed else 0
    return { 
        "vacancies_found": all_vacancies,
        "vacancies_processed": vacancies_processed,
        "average_salary": avg_salary
    }


def get_hh_salaries(language):
    moscow_id = 1
    vacancies_per_page = 100
    days = 31
    params = {
        'area': moscow_id,        
        'page': 0,
        'per_page': vacancies_per_page,
        'text': language,
        'vacancy_search_fields': {'id': 'name'},
        'period': days
    }
    response = requests.get('https://api.hh.ru/vacancies', params=params)
    response.raise_for_status()
    vacancies_from_page = response.json()
 
    num_pages = vacancies_from_page.get('pages')
    vacancies_from_page = vacancies_from_page.get('items')
    all_vacancies = vacancies_from_page
    for page in range(1, num_pages):
        params['page'] = page
        response = requests.get('https://api.hh.ru/vacancies', params=params)
        response.raise_for_status()
        vacancies_from_page = response.json().get('items')
        all_vacancies += vacancies_from_page
    vacancies_processed = 0
    sum_salary = 0
    for vacancy in all_vacancies:
        salary = predict_rub_salary_hh(vacancy)
        if salary:
            sum_salary += salary
            vacancies_processed += 1
    avg_salary = int(sum_salary / vacancies_processed) if vacancies_processed else 0
    
    return { 
        "vacancies_found": len(all_vacancies),
        "vacancies_processed": vacancies_processed,
        "average_salary": avg_salary
    }


def main():
    stats_hh = {}
    http_error = False
    try:
        for language in PROGRAM_LANGUAGES:
            stats_hh[language] = get_hh_salaries(language)
    except requests.exceptions.HTTPError as e:
        http_error = True
        print(f'Ошибка получения данных от HH, перезапустите скрипт:\n{e}')
    
    load_dotenv()
    token_sj = os.getenv('SJ_TOKEN')
    secret_code = os.getenv('SJ_SECRET_CODE')
    try:
        vacancies_sj = get_sj_vacancies(secret_code, token_sj)
    except requests.exceptions.HTTPError as e:
        http_error = True
        print(f'Ошибка получения данных от SJ, перезапустите скрипт:\n{e}')
    stats_sj = {}
  
    if not http_error:
        for language in PROGRAM_LANGUAGES:
            stats_sj[language] = get_sj_salaries(language, vacancies_sj)
        table_headers = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
        table_stats_hh = table_headers.copy()
        table_stats_hh += [[language, *language_stats.values()] for language, language_stats in stats_hh.items()]
        table_instance_hh = AsciiTable(table_stats_hh, 'HeadHunter Moscow')
        table_stats_sj = table_headers.copy()
        table_stats_sj += [[language, *language_stats.values()] for language, language_stats in stats_sj.items()]
        table_instance_sj = AsciiTable(table_stats_sj, 'SuperJob Moscow')

        print('\n', table_instance_hh.table, '\n\n', table_instance_sj.table)
    else:
        print('Невозможно построить таблицы, недостаточно данных!')

if __name__ == '__main__':
    main()