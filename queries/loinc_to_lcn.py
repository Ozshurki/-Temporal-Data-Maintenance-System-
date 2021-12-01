def get_inc(inc_cursor, loinc_num):
    query = " SELECT lcn " \
            " FROM LOINC_TO_LCN " \
            " WHERE loinc_num = %s"

    inc_cursor.execute(query, (loinc_num,))
    long_common_name = inc_cursor.fetchone()['lcn'].lower()
    return long_common_name
