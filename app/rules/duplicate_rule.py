from .base_rule import BaseRule

class DuplicateRule(BaseRule):
    @property
    def name(self): return "Duplicate Keys"
    
    @property
    def issue_type(self): return "content"

    def evaluate(self, conn, table_name: str):
        query = f"""
            SELECT COUNT(*) FROM (
                SELECT customer_id FROM {table_name} 
                GROUP BY customer_id HAVING COUNT(*) > 1
            )
        """
        violations = conn.execute(query).fetchone()[0]
        return {"violations": violations, "description": "Multiple records share the same customer_id."}

    def get_sql_transformation(self):
        return """
        -- Deduplicate based on customer_id, keeping the earliest signup
        deduplicated AS (
            SELECT * FROM clean_nulls
            QUALIFY ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY signup_date ASC) = 1
        )"""