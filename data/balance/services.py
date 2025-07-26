from django.db import connection


def mutual_settlements(
        self,
        customer_id: int,
        last_one: bool = False,
):
    query = """
        WITH balance_cte_f AS (
            SELECT 
                id,
                customer_id,
                created_at,
                amount AS change,
                SUM(amount) OVER (PARTITION BY customer_id ORDER BY created_at) AS final_balance,
                reason,
                comment
            FROM balance_balance
            WHERE customer_id = %s
        ),
        balance_cte_s AS (
            SELECT 
                id,
                customer_id,
                COALESCE(LAG(final_balance) OVER (PARTITION BY customer_id ORDER BY created_at), 0) AS start_balance,
                change,
                final_balance,
                created_at,
                reason,
                comment
            FROM balance_cte_f
        )
        SELECT * FROM balance_cte_s
        ORDER BY created_at;
    """

    params = [customer_id]

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in results]

    if not data:
        return None if last_one else []

    if last_one:
        return data[-1]

    return data
