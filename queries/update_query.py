import datetime
from validators.name_validator import first_name_is_valid
from validators.date_validator import date_exists
from queries.select_query import get_inc


def insert_new_record():
    query = " INSERT INTO last_modified (first_name, last_name, loinc_num, valid_date, value, modified_date)" \
            " VALUES (%s, %s, %s, %s, %s, %s) "

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


def update_latest_record(valid_date_without_time):
    update = " UPDATE PATIENTS" \
             " SET last_modified = %s" \
             " WHERE first_name = %s" \
             " AND loinc_num = %s" \
             " AND valid_start_time{date_symbol} = %s " \
             " AND transaction_time IN (SELECT MAX(transaction_time)" \
             " FROM PATIENTS " \
             " WHERE first_name = %s " \
             " AND valid_start_time{date_symbol} = %s)".format(date_symbol="::DATE" if valid_date_without_time else "")

    select = " SELECT * " \
             " FROM PATIENTS" \
             " WHERE first_name = %s" \
             " AND loinc_num = %s" \
             " AND valid_start_time{date_symbol} = %s " \
             " AND transaction_time IN (SELECT MAX(transaction_time)" \
             " FROM PATIENTS " \
             " WHERE first_name = %s " \
             " AND valid_start_time{date_symbol} = %s)".format(date_symbol="::DATE" if valid_date_without_time else "")

    return [update, select]


def update_query(patients_cursor, inc_cursor, last_modified_cursor):

    try:
        [first_name, last_name] = input("Enter patient full name\n").strip().split()
        valid_date = input("Enter valid date (year/mm/dd  hh/mm/ss)\n").strip().split()
        modified_date = input("Enter modified date (year/mm/dd  hh/mm/ss)\n").strip()
        loinc_num = input("Enter loinc number\n").strip()
        new_value = input("Enter a new value\n").strip()

        # Verify if first_name exists
        if not first_name_is_valid(first_name, patients_cursor):
            raise NameError(f"No such name {first_name} {last_name}, please try again.")

        # Get Long Common Name
        long_common_name = get_inc(inc_cursor, loinc_num)

        # If user didnt enter date, use current date
        if not modified_date:
            modified_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        valid_date_without_time = False
        if len(valid_date) == 1:
            valid_date_without_time = True
            date = valid_date[0]
        else:
            date = valid_date[0] + " " + valid_date[1]

        if not date_exists(date, patients_cursor, valid_date_without_time):
            raise NameError(f"No such date {date} in the database, please try again.")

        #if valid_date_without_time:
        [update_query, select_query] = update_latest_record(valid_date_without_time)
        patients_cursor.execute(update_query, (modified_date, first_name, loinc_num, date, first_name, date,))
        patients_cursor.execute(select_query, (first_name, loinc_num, date, first_name, date,))
        # else:
        #     [update_query, select_query] = update_record()
        #     patients_cursor.execute(update_query, (modified_date, first_name, loinc_num, date,))
        #     patients_cursor.execute(select_query, (first_name, loinc_num, date,))


        record = patients_cursor.fetchone()
        print("The record that has been update is:\n")
        # for record in records:
        print(f"{first_name} {last_name} loinc_num: {record['loinc_num']} ({long_common_name}) at {date}")

        print("Record has been update")
        # Insert new record to modified database
        query = insert_new_record()
        insert_values = (first_name, last_name, loinc_num, record['valid_start_time'], new_value, modified_date)
        last_modified_cursor.execute(query, insert_values)

    except Exception as error:
        print(error)
        return
