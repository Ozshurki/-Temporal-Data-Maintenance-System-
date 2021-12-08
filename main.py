import psycopg2.extras
import sys
sys.path.append("queries")
sys.path.append("validators")

from queries.select_query import select_query
from queries.delete_query import delete_record
from queries.update_query import update_query
from queries.retrieving_history import history_query


def input_invalid():
    print("Input is invalid, please try again.")


def add_columns(cursor):
    add_modified_column = " ALTER TABLE PATIENTS" \
                          " ADD COLUMN last_modified TIMESTAMP without time zone NULL"

    add_deleted_column = " ALTER TABLE PATIENTS" \
                         " ADD COLUMN deleted_date TIMESTAMP without time zone NOT NULL DEFAULT '3000-12-12 00:00:00' "

    cursor.execute(add_modified_column)
    cursor.execute(add_deleted_column)


connection = None
chooseAction = "Please choose your action:\n" \
               "1. Select\n" \
               "2. Retrieving history\n" \
               "3. Update\n" \
               "4. Delete\n" \

# Patients DB
hostname = 'localhost'
database = 'postgres'
username = 'postgres'
pwd = 'root'
port_id = 5432

# loinc_to_lcn DB
hostname_inc = 'localhost'
database_inc = 'postgres'
username_inc = 'postgres'
pwd_inc = 'root'
port_id_inc = 5432

# last_modified DB
hostname_last_modified = 'localhost'
database_last_modified= 'postgres'
username_last_modified = 'postgres'
pwd_last_modified = 'root'
port_id_last_modified = 5432


def select_action(_str):
    print(_str)
    action = int(input().strip())
    return action


def main():
    input_dict = {
        1: select_query,
        2: history_query,
        3: update_query,
        4: delete_record
    }

    # Connect to mapping loinc DB
    try:
        with psycopg2.connect(
                host=hostname_inc,
                dbname=database_inc,
                user=username_inc,
                password=pwd_inc,
                port=port_id_inc) as inc_conn:
            with inc_conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as inc_cursor:

                with psycopg2.connect(
                        host=hostname,
                        dbname=database,
                        user=username,
                        password=pwd,
                        port=port_id) as conn:
                    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as patients_cursor:

                        with psycopg2.connect(
                                host=hostname,
                                dbname=database,
                                user=username,
                                password=pwd,
                                port=port_id) as last_modified_conn:
                            with last_modified_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)\
                                    as last_modified_cursor:
                                add_columns(patients_cursor)

                                user_input = select_action(chooseAction)
                                input_dict.get(user_input, input_invalid)(
                                         patients_cursor, inc_cursor, last_modified_cursor)

    except Exception as error:
        print(error)
    finally:
        if inc_conn is not None:
            inc_conn.close()
        if conn is not None:
            conn.close()
        if last_modified_conn is not None:
            last_modified_conn.close()


if __name__ == "__main__":
    main()
