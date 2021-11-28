def date_exists(valid_date, cursor):
    query = ' SELECT valid_start_time' \
            ' FROM PATIENTS' \
            ' WHERE valid_start_time = %s'

    cursor.execute(query, (valid_date,))
    records = cursor.fetchall()

    if not records:
        return False
    return True
