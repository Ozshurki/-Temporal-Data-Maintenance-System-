import psycopg2.extras
import datetime
from loinc_to_lcn import get_inc
from validators.date_validator import date_exists
from validators.name_validator import first_name_is_valid


def get_last_modified(valid_date_without_time):
    query = " SELECT * " \
            " FROM last_modified " \
            " WHERE modified_date IN (SELECT MAX(modified_date) " \
            " FROM last_modified " \
            " WHERE first_name = %s AND " \
            " valid_date{date_symbol} = %s AND " \
            " loinc_num = %s AND " \
            " modified_date < %s)".format(date_symbol="::DATE" if valid_date_without_time else "")

    return query


def find_latest_date(valid_date_without_time):
    query = " SELECT * " \
            " FROM PATIENTS " \
            " WHERE first_name = %s" \
            " AND loinc_num = %s " \
            " AND transaction_time < %s " \
            " AND valid_start_time IN (SELECT MAX(valid_start_time) " \
            " FROM PATIENTS " \
            " WHERE first_name = %s " \
            " AND loinc_num = %s " \
            " AND valid_start_time{date_symbol} = %s " \
            " AND deleted_date > %s " \
            " AND transaction_time < %s) ".format(date_symbol="::DATE" if valid_date_without_time else "")

    return query


def select_query(patients_cursor, inc_cursor, last_modified_cursor):

    try:
        [first_name, last_name] = input("Enter patient full name\n").strip().split()
        valid_date = input("Enter valid date (year/mm/dd  hh/mm/ss)\n").strip().split()
        my_date = input("Enter your date\n")
        loinc_num = input("Enter loinc number\n").strip()

        # Verify if first_name exists
        if not first_name_is_valid(first_name, patients_cursor):
            raise NameError(f"No such name {first_name} {last_name}, please try again.")

        # Use current time if not entered
        if not my_date:
            my_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Init variable
        valid_date_without_time = False
        date = ""

        # Valid_date without time
        if len(valid_date) == 1:
            valid_date_without_time = True
            date = valid_date[0]
        elif len(valid_date) == 2:
            date = valid_date[0] + " " + valid_date[1]

        if not date_exists(date, patients_cursor, valid_date_without_time):
            raise NameError(f"No such date {valid_date} in the database, please try again.")

        # Get Long Common Name
        long_common_name = get_inc(inc_cursor, loinc_num)

        query = find_latest_date(valid_date_without_time)
        patients_cursor.execute(query, (first_name, loinc_num, my_date, first_name, loinc_num, date, my_date, my_date))
        record = patients_cursor.fetchall()

        # Query didnt returned any result
        if not record:
            print(f"{first_name} didnt take a {long_common_name} examination at {date}")
            return

        if record[0][7]:
            last_modified_query = get_last_modified(valid_date_without_time)
            last_modified_cursor.execute(last_modified_query, (first_name, date, loinc_num, my_date))
            last_modified_record = last_modified_cursor.fetchall()
            value = last_modified_record[0][4]
        else:
            # Get the value of the examination
            value = record[0][3]

        print(f"{first_name} {last_name} {long_common_name} value is: {value}\n")

    except Exception as error:
        print(error)
        return
