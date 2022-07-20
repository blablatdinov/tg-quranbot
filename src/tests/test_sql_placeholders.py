from services.sql_placeholders import generate_sql_placeholders


def test():
    got = generate_sql_placeholders(['a', 'b', 'c'], 4)

    assert got == '($1, $2, $3, $4), ($5, $6, $7, $8), ($9, $10, $11, $12)'
