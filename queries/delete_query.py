import psycopg2.extras
import datetime
from validators.name_validator import first_name_is_valid
from validators.date_validator import date_exists
from queries.select_query import get_inc


def find_latest_record():
    query = " UPDATE PATIENTS" \
            " SET deleted_date = %s" \
            " WHERE first_name = %s AND" \
            " loinc_num = %s AND" \
            " valid_start_time IN (SELECT MAX(valid_start_time)" \
            " FROM PATIENTS " \
            " WHERE first_name = %s AND" \
            " loinc_num = %s AND" \
            " valid_start_time::DATE = %s)"

    return query


def find_record():
    query = " UPDATE PATIENTS" \
            " SET deleted_date = %s" \
            " WHERE first_name = %s AND" \
            " loinc_num = %s" \
            " valid_start_time = %s"
    return query


def delete_record(cursor, cursor_inc):
    [first_name, last_name] = input("Enter patient full name\n").strip().split()
    valid_date = input("Enter valid date you wish to delete (year/mm/dd  hh/mm/ss)\n").strip().split()
    delete_date = input("Enter your date (year/mm/dd  hh/mm/ss)\n").strip().split()
    examination_num = input("Enter loinc\n").strip()

    # Verify if first_name exists
    if not first_name_is_valid(first_name, cursor):
        print("No such name, please try again.")
        return

    # Get Long Common Name
    lcn_query = get_inc()
    cursor_inc.execute(lcn_query, (examination_num,))
    long_common_name = cursor_inc.fetchone()['lcn'].lower()

    if not delete_date:
        delete_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not date_exists(valid_date, cursor):
        print("No such date, please try again.")
        return

    without_time = False
    if len(valid_date) == 1:
        without_time = True

    if without_time:
        query = find_latest_record()
    else:
        query = find_record()

    cursor.execute(query, (delete_date, first_name, examination_num, first_name, examination_num, valid_date))
    records = cursor.fetchall()

    # Query didnt return any result
    if not records:
        print(f"{first_name} didnt take a {long_common_name} examination at {delete_date}")
        return

    # Get the value of the examination
    value = records[0][1]
    print(f"{first_name} {long_common_name} at {delete_date} is deleted\n")
