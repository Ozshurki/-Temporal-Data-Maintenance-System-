import psycopg2.extras
import datetime
from validators.name_validator import first_name_is_valid
from validators.date_validator import date_exists
from queries.select_query import get_inc


def valid_range_date(start_date, end_date):
    if not start_date:
        start = "1900-01-01 00:00:00"
    elif len(start_date) == 1:
        start = start_date[0] + " " + "00:00:00"
    else:
        start = start_date[0] + " " + start_date[1]

    if not end_date:
        end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif len(end_date) == 1:
        end = end_date[0] + " " + "23:59:00"
    else:
        end = end_date[0] + " " + end_date[1]

    return [start, end]


def check_last_modified_database(last_modified_cursor, first_name,last_name, loinc_num, valid_date, start_date, end_date, long_common_name):
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
        print(f"{first_name} {last_name} loinc_num: {record['loinc_num']} ({long_common_name}) with value: {record['value']} last modified at {record['modified_date']}")


def find_specific_exams():
    query = " SELECT * " \
            " FROM PATIENTS " \
            " WHERE first_name = %s AND " \
            " loinc_num = %s AND " \
            " valid_start_time = %s"
    return query


def find_all_exams():
    query = " SELECT *" \
            " FROM PATIENTS " \
            " WHERE first_name = %s " \
            " AND valid_start_time::DATE = %s " \
            " AND loinc_num = %s " \
            " AND transaction_time >= %s " \
            " AND transaction_time <= %s "
    return query


def history_query(patients_cursor, inc_cursor, last_modified_cursor):
    [first_name, last_name] = input("Enter patient full name\n").strip().split()
    loinc_num = input("Enter loinc number\n").strip()
    valid_date = input("Enter valid date (year/mm/dd  hh/mm/ss)\n").strip().split()
    start_date = input("Enter start range date (year/mm/dd  hh/mm/ss)\n").strip().split()
    end_date = input("Enter end range date (year/mm/dd  hh/mm/ss)\n").strip().split()

    # Verify if first_name exists
    if not first_name_is_valid(first_name, patients_cursor):
        print("No such name, please try again.")
        return

    # Init variable
    valid_date_with_time = False

    if len(valid_date) == 1:
        valid_date_with_time = True
        date = valid_date[0]
    else:
        date = valid_date[0] + " " + valid_date[1]

    if not date_exists(date, patients_cursor, valid_date_with_time):
        print("No such date, please try again.")
        return

    [start, end] = valid_range_date(start_date, end_date)

    if valid_date_with_time:
        query = find_all_exams()
        patients_cursor.execute(query, (first_name, date, loinc_num, start, end))
    else:
        query = find_specific_exams()
        patients_cursor.execute(query, (first_name, loinc_num, date))

    records = patients_cursor.fetchall()

    # Query didnt returned any result
    if not records:
        print(f"{first_name} didnt take a examination at {date}")
        return

    long_common_name = get_inc(inc_cursor, loinc_num)

    print(f"\nThe records that in the range of {start} - {end} are:\n")
    # For each record
    for record in records:

        # If the record has been update
        if record['last_modified']:
            check_last_modified_database(last_modified_cursor, first_name, last_name, loinc_num, date, start, end, long_common_name)
        else:
            print(f"{first_name} {last_name} loinc_num: {record['loinc_num']} ({long_common_name}) with value: {record['value']} last modified at {record['transaction_time']}")


