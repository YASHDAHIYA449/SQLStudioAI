from .base_rule import BaseRule

class DomainRule(BaseRule):
    @property
    def name(self): return "Out-of-Domain Values"
    
    @property
    def issue_type(self): return "content"

    def evaluate(self, conn, table_name: str):
        query = f"""
            SELECT COUNT(*) FROM {table_name} 
            WHERE LOWER(segment) NOT IN ('retail', 'premium', 'enterprise')
               OR LOWER(is_active) NOT IN ('true', 'false')
        """
        violations = conn.execute(query).fetchone()[0]
        return {"violations": violations, "description": "Found unexpected values in 'segment' or 'is_active'."}

    def get_sql_transformation(self):
        return """
        -- Standardize domain values for segment and is_active
        standardized_domains AS (
            SELECT 
                * EXCLUDE(segment, is_active),
                CASE 
                    WHEN LOWER(segment) IN ('primium', 'premium ') THEN 'premium'
                    WHEN LOWER(segment) IN ('enterprize', 'enterprise ') THEN 'enterprise'
                    WHEN LOWER(segment) = 'retail ' THEN 'retail'
                    ELSE LOWER(segment) 
                END AS segment,
                CASE 
                    WHEN LOWER(is_active) IN ('true', 'y', 'yes', '1') THEN 'TRUE'
                    ELSE 'FALSE'
                END AS is_active
            FROM deduplicated
        )"""