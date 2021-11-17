import psycopg2.extras
import datetime


def getINC(loinc):
    select_query = " SELECT lcn " \
                   " FROM LOINC_TO_LCN " \
                   " WHERE loinc_num = %s"

    return select_query

def find_latest_date(first_name, last_name, date, prespective_date, loinc, is_with_time):
    select_query = " SELECT first_name, value " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s" \
                   " AND loinc_num = %s " \
                   " AND valid_start_time IN (SELECT MAX(valid_start_time) " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s AND " \
                   " valid_start_time{dateSymbol} = %s " \
                   " AND transaction_time::DATE < %s) ".format(dateSymbol="::DATE" if is_with_time else "")

    return select_query


def first_name_is_valid(first_name, cursor):
    select_query = " SELECT first_name " \
                   " FROM PATIENTS " \
                   " WHERE first_name = %s"

    cursor.execute(select_query, (first_name,))
    records = cursor.fetchall()

    if not records:
        return False
    return True


def selectQuery(cursor, cursor_inc):

    select_query = ""
    records = []
    is_with_time = False
    date =""

    [first_name, last_name] = input("Enter patient full name\n").split()
    wanted_date = input("Enter wanted date (year/mm/dd  hh/mm/ss)\n").split()
    prespective_date = input("Enter your date\n")
    loinc = input("Enter loinc\n")

    # Valid if first_name exists
    if not first_name_is_valid(first_name, cursor):
        print("No such name, please try again.")
        return

    # Use current time if not entered
    if not prespective_date:
        prespective_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get Long Common Name
    lcn_query = getINC(loinc)
    cursor_inc.execute(lcn_query, (loinc,))
    long_common_name = cursor_inc.fetchone()['lcn'].lower()

    # Date is without time
    if len(wanted_date) == 1:
        is_with_time = True
        date = wanted_date[0]
    else:
        date = wanted_date[0] + " " + wanted_date[1]

    select_query = find_latest_date(first_name, last_name, date, prespective_date, loinc, is_with_time)
    cursor.execute(select_query, (first_name, loinc, first_name, date, prespective_date,))
    records = cursor.fetchall()

    # Query didnt return any result
    if not records:
        print(f"{first_name} didnt take a {long_common_name} examination at {date}")
        return

    # Get the value of the examination
    value = records[0][1]
    print(f"{first_name} {long_common_name} is: {value}\n")
