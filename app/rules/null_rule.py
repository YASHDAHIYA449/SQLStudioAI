from .base_rule import BaseRule

class NullRule(BaseRule):
    @property
    def name(self): return "Null Violations"
    
    @property
    def issue_type(self): return "content"

    def evaluate(self, conn, table_name: str):
        # Flags rows missing customer_id, missing BOTH name/email, or missing name (which needs repair)
        query = f"""
            SELECT COUNT(*) FROM {table_name} 
            WHERE customer_id IS NULL 
               OR (full_name IS NULL AND email IS NULL)
               OR full_name IS NULL;
        """
        violations = conn.execute(query).fetchone()[0]
        return {
            "violations": violations, 
            "description": "Missing customer_id, completely missing contact info, or missing names requiring imputation."
        }

    def get_sql_transformation(self):
        return """
        -- Filter missing IDs or completely missing contact info, and impute missing names from email
        clean_nulls AS (
            SELECT 
                * EXCLUDE(full_name),
                
                -- Extract string before '@', strip non-alphabet/non-dot characters (like numbers), 
                -- and then replace the remaining '.' with a space.
                CASE 
                    WHEN (full_name IS NULL OR TRIM(full_name) = '') AND email IS NOT NULL 
                        THEN REPLACE(REGEXP_REPLACE(SPLIT_PART(email, '@', 1), '[^a-zA-Z.]', '', 'g'), '.', ' ')
                    ELSE full_name
                END AS full_name
                
            FROM raw_data 
            WHERE customer_id IS NOT NULL 
              -- Ensure both aren't missing simultaneously
              AND NOT (
                  (email IS NULL OR TRIM(email) = '') AND 
                  (full_name IS NULL OR TRIM(full_name) = '')
              )
        )"""