import data
from data_tools import write_json

from app import GOALS_JSON_PATH, TEACHERS_JSON_PATH, REQUESTS_JSON_PATH


def main():
    write_json(GOALS_JSON_PATH, data.goals)
    write_json(TEACHERS_JSON_PATH, data.teachers)
    with open(REQUESTS_JSON_PATH, 'w', encoding='utf-8') as file:
        pass


if __name__ == '__main__':
    main()
