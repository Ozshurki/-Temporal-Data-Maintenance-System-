import psycopg2.extras
import sys
sys.path.append("C:\\Users\\shurk\\PycharmProjects\\AI_Project\queries")
sys.path.append("C:\\Users\\shurk\\PycharmProjects\\AI_Project\\validators")
from queries.select_query import select_query
from queries.delete_query import delete_record

EXIT = 5


def input_invalid():
    print("Input is invalid, please try again.")


def add_columns(cursor):
    add_column = 'ALTER TABLE PATIENTS' \
                 'ADD COLUMN deleted_time timestamp without time zone' \
                 'ADD COLUMN last_modified timestamp without time zone' \
                 'ADD COLUMN old_value timestamp without time zone'

    cursor.execute(add_column)


connection = None
chooseAction = "Please enter your query:\n" \
               "1. Select\n" \
               "2. Retrieving history\n" \
               "3. Update\n" \
               "4. Delete\n" \
               "5. Exit\n" \

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


def select_action(_str):
    print(_str)
    action = int(input().strip())
    return action


def main():
    input_dict = {
        1: select_query,
        2: input_invalid,
        4: delete_record
    }

    # Connect to mapping loinc DB
    try:
        with psycopg2.connect(
                host=hostname_inc,
                dbname=database_inc,
                user=username_inc,
                password=pwd_inc,
                port=port_id_inc) as conn_inc:

            with conn_inc.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor_inc:
                with psycopg2.connect(
                        host=hostname,
                        dbname=database,
                        user=username,
                        password=pwd,
                        port=port_id) as conn:
                    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        # add_columns(cursor)

                        user_input = select_action(chooseAction)
                        # while user_input is not EXIT:
                        input_dict.get(user_input, input_invalid)(cursor, cursor_inc)
    except Exception as error:
        print(error)
    finally:
        if conn_inc is not None:
            conn_inc.close()
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()
