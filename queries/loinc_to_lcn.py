import sys
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)


def get_inc():
    query = " SELECT lcn " \
                   " FROM LOINC_TO_LCN " \
                   " WHERE loinc_num = %s"

    return query
