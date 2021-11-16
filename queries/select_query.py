import psycopg2.extras
import datetime

def getINC(loinc):
    select_query = " SELECT lcn " \
                   " FROM LOINC_TO_LCN " \
                   " WHERE loinc_num = %s"

    return select_query

def find_latest_date_without_time(first_name, last_name, wanted_date, prespective_date, loinc):
    select_query = " SELECT first_name, value " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s " \
                   " AND loinc_num = %s" \
                   " AND valid_start_time IN (SELECT MAX(valid_start_time) " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s AND " \
                   " valid_start_time::DATE = %s " \
                   " AND transaction_time::DATE < %s) "

    return select_query


def find_latest_date_with_time(first_name, last_name, date, prespective_date, loinc):
    select_query = " SELECT first_name, value " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s" \
                   " AND loinc_num = %s " \
                   " AND valid_start_time IN (SELECT MAX(valid_start_time) " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s AND " \
                   " valid_start_time = %s " \
                   " AND transaction_time::DATE < %s) "

    return select_query


def selectQuery(cursor, cursor_inc):

    [first_name, last_name] = input("Enter patient full name\n").split()
    wanted_date = input("Enter wanted date (year/mm/dd  hh/mm/ss)\n").split()
    prespective_date = input("Enter your date\n")
    loinc = input("Enter loinc\n")

    # Use current time if not entered
    if not prespective_date:
        prespective_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get Long Common Name
    lcn_query = getINC(loinc)
    cursor_inc.execute(lcn_query, (loinc,))
    long_common_name = cursor_inc.fetchone()['lcn']

    # Date is without time
    if len(wanted_date) == 1:
        date = wanted_date[0]
        select_query = find_latest_date_without_time(first_name, last_name, date, prespective_date, loinc)
        cursor.execute(select_query, (first_name, loinc, first_name, date, prespective_date,))
    else:
        date = wanted_date[0] + " " + wanted_date[1]
        select_query = find_latest_date_with_time(first_name, last_name, date, prespective_date, loinc)
        cursor.execute(select_query, (first_name, loinc, first_name, date, prespective_date,))


    value = cursor.fetchone()['value']
    print(f"{first_name} {long_common_name} is: {value}")
