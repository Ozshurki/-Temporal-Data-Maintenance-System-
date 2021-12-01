import datetime
from validators.name_validator import first_name_is_valid
from validators.date_validator import date_exists
from queries.select_query import get_inc


def insert_new_record():
    query = " INSERT INTO last_modified (first_name, last_name, loinc_num, valid_date, value, modified_date)" \
            " VALUES (%s, %s, %s, %s, %s, %s) " \

    return query


def update_record():
    update = " UPDATE PATIENTS " \
                   " SET last_modified = %s " \
                   " WHERE first_name = %s AND" \
                   " loinc_num = %s AND " \
                   " valid_start_time = %s "

    select = " SELECT * " \
             " FROM PATIENTS " \
             " WHERE first_name = %s AND" \
             " loinc_num = %s AND " \
             " valid_start_time = %s "

    return [update, select]


def update_latest_record():
    update = " UPDATE PATIENTS" \
             " SET last_modified = %s" \
             " WHERE first_name = %s" \
             " AND loinc_num = %s" \
             " AND valid_start_time::DATE = %s " \
             " AND transaction_time IN (SELECT MAX(transaction_time)" \
             " FROM PATIENTS " \
             " WHERE first_name = %s " \
             " AND valid_start_time::DATE = %s)"

    select = " SELECT * " \
             " FROM PATIENTS" \
             " WHERE first_name = %s" \
             " AND loinc_num = %s" \
             " AND valid_start_time::DATE = %s " \
             " AND transaction_time IN (SELECT MAX(transaction_time)" \
             " FROM PATIENTS " \
             " WHERE first_name = %s " \
             " AND valid_start_time::DATE = %s)"

    return [update, select]


def update_query(patients_cursor, inc_cursor, last_modified_cursor):
    [first_name, last_name] = input("Enter patient full name\n").strip().split()
    valid_date = input("Enter valid date you wish to delete (year/mm/dd  hh/mm/ss)\n").strip().split()
    modified_date = input("Enter your date (year/mm/dd  hh/mm/ss)\n").strip()
    loinc_num = input("Enter loinc number\n").strip()
    new_value = input("Enter a new value\n").strip()

    # Verify if first_name exists
    if not first_name_is_valid(first_name, patients_cursor):
        print("No such name, please try again.")
        return

    # Get Long Common Name
    long_common_name = get_inc(inc_cursor, loinc_num)

    # If user didnt enter date, use current date
    if not modified_date:
        modified_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not date_exists(valid_date, patients_cursor):
        print(f"No such date {valid_date} in the database, please try again.")
        return

    if len(valid_date) == 1:
        [update_query, select_query] = update_latest_record()
        valid_date = valid_date[0]
        patients_cursor.execute(update_query, (modified_date, first_name, loinc_num, valid_date, first_name, valid_date,))
        patients_cursor.execute(select_query, (modified_date, first_name, loinc_num, valid_date, first_name, valid_date,))
    else:
        [update_query, select_query] = update_record()
        valid_date = valid_date[0] + " " + valid_date[1]
        patients_cursor.execute(update_query, (modified_date, first_name, loinc_num, valid_date,))
        patients_cursor.execute(select_query, (modified_date, first_name, loinc_num, valid_date,))

    records = patients_cursor.fetchall()
    print("The records that has been updates are:\n")
    for record in records:
        print(f"{first_name} {last_name} loinc_num: {record['loinc_num']} ({long_common_name}) at {valid_date}")

    print("Record has been update")
    # Insert new record to modified database
    query = insert_new_record()
    insert_values = (first_name, last_name, loinc_num, valid_date, new_value, modified_date)
    last_modified_cursor.execute(query, insert_values)
