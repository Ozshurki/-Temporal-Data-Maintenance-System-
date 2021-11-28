import psycopg2.extras
import datetime
from loinc_to_lcn import get_inc


def find_latest_date(is_with_time):
    query = " SELECT first_name, value " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s" \
                   " AND loinc_num = %s " \
                   " AND valid_start_time IN (SELECT MAX(valid_start_time) " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s AND " \
                   " valid_start_time{date_symbol} = %s " \
                   " AND transaction_time::DATE < %s) ".format(date_symbol="::DATE" if is_with_time else "")

    return query


def first_name_is_valid(first_name, cursor):
    query = " SELECT first_name " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s"

    cursor.execute(query, (first_name,))
    records = cursor.fetchall()

    if not records:
        return False
    return True


def select_query(cursor, cursor_inc):

    [first_name, last_name] = input("Enter patient full name\n").strip().split()
    wanted_date = input("Enter wanted date (year/mm/dd  hh/mm/ss)\n").strip().split()
    my_date = input("Enter your date\n").strip()
    examination_num = input("Enter loinc\n").strip()

    # Verify if first_name exists
    if not first_name_is_valid(first_name, cursor):
        print("No such name, please try again.")
        return

    # Use current time if not entered
    if not my_date:
        my_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get Long Common Name
    lcn_query = get_inc()
    cursor_inc.execute(lcn_query, (examination_num,))
    long_common_name = cursor_inc.fetchone()['lcn'].lower()

    # Init variable
    is_with_time = False
    date = ""

    # Date is without time
    if len(wanted_date) == 1:
        is_with_time = True
        date = wanted_date[0]
    else:
        date = wanted_date[0] + " " + wanted_date[1]

    query = find_latest_date(is_with_time)
    cursor.execute(query, (first_name, examination_num, first_name, date, my_date,))
    records = cursor.fetchall()

    # Query didnt return any result
    if not records:
        print(f"{first_name} didnt take a {long_common_name} examination at {date}")
        return

    # Get the value of the examination
    value = records[0][1]
    print(f"{first_name} {long_common_name} is: {value}\n")
