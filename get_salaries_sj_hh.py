import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests
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
    more_results = True
    vacancies = []
    timestamp_1_month_ago = (datetime.now() - timedelta(days=31)).timestamp()
    params = {
        'keyword': 'программист',
        'count': vacancies_per_page,
        'catalogues': 33,
        'date_published_from': timestamp_1_month_ago,
        'town': 4
    }
    headers = {'X-Api-App-Id': code,
               'Authorization':  f'Bearer {token}'
               'Content-Type:' 'application/json'}
    while more_results:
        params['page'] = page
        response = requests.get('https://api.superjob.ru/2.0/vacancies/', params=params, headers=headers)
        vacancies += response.json().get('objects', [])
        more_results = response.json().get('more')
    return vacancies


def get_salaries_sj(language, vacancies):
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


def get_vacancies(language):
    city_id = 1
    params = {
        'area': city_id,        
        'page': 0,
        'per_page': 100,
        'text': language,
        'vacancy_search_fields': {'id': 'name'},
        'period': 31
    }
    response = requests.get('https://api.hh.ru/vacancies', params=params)
    vacancies_from_page = response.json()
 
    num_pages = vacancies_from_page.get('pages')
    vacancies_from_page = vacancies_from_page.get('items')
    all_vacancies = vacancies_from_page
    for i in range(1, num_pages):
        params['page'] = i
        response = requests.get('https://api.hh.ru/vacancies', params=params)
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
    # for language in PROGRAM_LANGUAGES:
    #     stats_hh[language] = get_vacancies(language)
    with open('charts.json', 'r') as file:
        stats_hh = json.load(file)
    table_headers = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    table_data_hh = table_headers.copy()
    table_data_hh += [[language, *language_stats.values()] for language, language_stats in stats_hh.items()]
    table_instance_hh = AsciiTable(table_data_hh, 'HeadHunter Moscow')

    load_dotenv()
    token_sj = os.getenv('TOKEN')
    secret_code = os.getenv('SECRET_CODE')
    vacancies_sj = get_sj_vacancies(secret_code, token_sj)
    stats_sj = {}
    for language in PROGRAM_LANGUAGES:
        stats_sj[language] = get_salaries_sj(language, vacancies_sj)
    table_data_sj = table_headers.copy()
    table_data_sj += [[language, *language_stats.values()] for language, language_stats in stats_sj.items()]
    table_instance_sj = AsciiTable(table_data_sj, 'SuperJob Moscow')

    print('\n', table_instance_hh.table, '\n\n', table_instance_sj.table)
    

if __name__ == '__main__':
    main()