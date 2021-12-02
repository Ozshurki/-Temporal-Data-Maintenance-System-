import sys
from os.path import dirname, abspath


def first_name_is_valid(first_name, cursor):
    select_query = " SELECT first_name " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s"

    cursor.execute(select_query, (first_name,))
    records = cursor.fetchall()

    if not records:
        return False
    return True
