import psycopg2.extras
import datetime
from validators.name_validator import first_name_is_valid
from validators.date_validator import date_exists
from queries.select_query import get_inc


def check_last_modified_database(last_modified_cursor, first_name, loinc_num, valid_date, start_date, end_date):
    query = " SELECT * " \
            " FROM last_modified " \
            " WHERE first_name = %s " \
            " AND loinc_num = %s  " \
            " AND valid_date::DATE = %s " \
            " AND modified_date > %s " \
            " AND modified_date < %s "

    last_modified_cursor.execute(query, (first_name, loinc_num, valid_date, start_date, end_date))
    records = last_modified_cursor.fetchall()
    for record in records:
        print(f"{record}")


def find_specific_exams():
    query = " SELECT * " \
            " FROM PATIENTS " \
            " WHERE first_name = %s AND " \
            " valid_start_time = %s"
    return query


def find_all_exams():
    query = " SELECT *" \
            " FROM PATIENTS " \
            " WHERE first_name = %s " \
            " AND valid_start_time::DATE = %s " \
            " AND transaction_time::DATE > %s " \
            " AND transaction_time::DATE < %s "
    return query


def history_query(patients_cursor, inc_cursor, last_modified_cursor):
    [first_name, last_name] = input("Enter patient full name\n").strip().split()
    valid_date = input("Enter wanted date (year/mm/dd  hh/mm/ss)\n").strip().split()
    start_date = input("Enter start range date (year/mm/dd  hh/mm/ss)\n").strip().split()
    end_date = input("Enter end range date (year/mm/dd  hh/mm/ss)\n").strip().split()

    # Verify if first_name exists
    if not first_name_is_valid(first_name, patients_cursor):
        print("No such name, please try again.")
        return

    if not date_exists(valid_date, patients_cursor):
        print("No such date, please try again.")
        return

    if len(start_date) == 1:
        start_date = start_date[0] + " " + "00:00:00"
    if not start_date:
        start_date = "1900-01-01 00:00:00"
    if len(end_date) == 1:
        end_date = end_date[0] + " " + "23:59:00"
    if not end_date:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if len(valid_date) == 1:
        valid_date = valid_date[0]
        query = find_all_exams()
        patients_cursor.execute(query, (first_name, valid_date, start_date, end_date))
    else:
        valid_date = valid_date[0] + " " + valid_date[1]
        query = find_specific_exams()
        patients_cursor.execute(query, (first_name, valid_date))

    records = patients_cursor.fetchall()

    # Query didnt returned any result
    if not records:
        print(f"{first_name} didnt take a examination at {valid_date}")
        return

    # For each record
    for record in records:

        # If the record has been update
        if record['last_modified']:
            check_last_modified_database(last_modified_cursor, first_name, record['loinc_num'], valid_date, start_date, end_date)
        else:
            print(f"{record}")


