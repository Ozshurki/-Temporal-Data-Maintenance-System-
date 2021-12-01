def date_exists(valid_date, patients_cursor, valid_date_with_time):
    query = " SELECT valid_start_time" \
            " FROM PATIENTS" \
            " WHERE valid_start_time{date_symbol} = %s ".format(date_symbol="::DATE" if valid_date_with_time else "")

    patients_cursor.execute(query, (valid_date,))
    records = patients_cursor.fetchall()

    if not records:
        return False
    return True
