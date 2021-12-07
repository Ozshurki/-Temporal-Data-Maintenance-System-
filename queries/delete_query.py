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
            " loinc_num = %s AND" \
            " valid_start_time = %s"

    return query


def delete_record(patients_cursor, inc_cursor, last_modified_cursor):

    try:
        [first_name, last_name] = input("Enter patient full name\n").strip().split()
        valid_date = input("Enter valid date you wish to delete (year/mm/dd  hh/mm/ss)\n").strip().split()
        delete_date = input("Enter your date (year/mm/dd  hh/mm/ss)\n").strip().split()
        loinc_num = input("Enter loinc number\n").strip()

        # Verify if first_name exists
        if not first_name_is_valid(first_name, patients_cursor):
            raise NameError(f"No such name {first_name} {last_name}, please try again.")

        # Get Long Common Name
        long_common_name = get_inc(inc_cursor, loinc_num)
        # inc_cursor.execute(lcn_query, (loinc_num))
        # long_common_name = inc_cursor.fetchone()['lcn'].lower()

        if not delete_date:
            delete_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        without_time = False
        date = ""
        if len(valid_date) == 1:
            without_time = True
            date = valid_date[0]
        else:
            date = valid_date[0] + " " + valid_date[1]

        if not date_exists(date, patients_cursor, without_time):
            raise NameError(f"No such date {valid_date} in the database, please try again.")

        if without_time:
            query = find_latest_record()
            patients_cursor.execute(query, (delete_date, first_name, loinc_num, first_name, loinc_num, date))
        else:
            query = find_record()
            patients_cursor.execute(query, (delete_date, first_name, loinc_num, date))

        # Get the value of the examination
        print(f"{first_name} {last_name} {long_common_name} at {date} is deleted\n")

    except Exception as error:
        print(error)
        return
