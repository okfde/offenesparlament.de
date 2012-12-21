import sqlaload as sl

def fetch_row(engine, table_name, **kw):
    table = sl.get_table(engine, table_name)
    return sl.find_one(engine, table, **kw)


