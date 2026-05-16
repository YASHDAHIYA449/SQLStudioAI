from .base_rule import BaseRule

class FormatRule(BaseRule):
    @property
    def name(self): return "Format Inconsistencies"
    
    @property
    def issue_type(self): return "content"

    def evaluate(self, conn, table_name: str):
        # Using a raw string (r"") prevents Python from escaping our regex backslashes.
        # We replace __TABLE_NAME__ safely to avoid curly brace clashes in f-strings.
        query = r"""
            SELECT COUNT(*) FROM __TABLE_NAME__ 
            WHERE 
                NOT REGEXP_MATCHES(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
                OR LENGTH(REGEXP_REPLACE(phone, '[^0-9]', '', 'g')) < 10
                OR full_name != array_to_string(list_transform(string_split(regexp_replace(trim(full_name), '\s+', ' ', 'g'), ' '), x -> upper(substr(x, 1, 1)) || lower(substr(x, 2))), ' ')
                OR LOWER(country) IN ('india', 'united states', 'u.k.', 'usa')
                OR signup_date NOT LIKE '%/%/%';
        """.replace("__TABLE_NAME__", table_name)
        
        violations = conn.execute(query).fetchone()[0]
        return {
            "violations": violations, 
            "description": "Found unstandardized names, invalid emails, short phones, or bad date/location formats."
        }

    def get_sql_transformation(self):
        return r"""
        -- Format standardization for names, emails, phones, dates, and locations
        cleaned_formats AS (
            SELECT 
                * EXCLUDE(full_name, email, phone, signup_date, country, city),
                
                -- 1. Full Name: DuckDB alternative to INITCAP (Splits by space, capitalizes each word, joins back)
                array_to_string(
                    list_transform(
                        string_split(regexp_replace(trim(full_name), '\s+', ' ', 'g'), ' '), 
                        x -> upper(substr(x, 1, 1)) || lower(substr(x, 2))
                    ), 
                    ' '
                ) AS full_name,
                
                -- 2. Email: Basic regex validation. If invalid, label as 'missing'
                CASE 
                    WHEN REGEXP_MATCHES(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') THEN email 
                    ELSE 'missing' 
                END AS email,
                
                -- 3. Phone: Keep last 10 digits. If fewer than 10 total digits, label as 'missing'
                CASE 
                    WHEN LENGTH(REGEXP_REPLACE(phone, '[^0-9]', '', 'g')) >= 10 
                    THEN RIGHT(REGEXP_REPLACE(phone, '[^0-9]', '', 'g'), 10) 
                    ELSE 'missing' 
                END AS phone,
                
                -- 4. Signup Date: Attempt to parse multiple possible raw formats, then output strictly as DD/MM/YYYY
                STRFTIME(
                    COALESCE(
                        TRY_STRPTIME(signup_date, '%d-%m-%Y'),
                        TRY_STRPTIME(signup_date, '%m/%d/%Y'),
                        TRY_STRPTIME(signup_date, '%d.%m.%Y'),
                        TRY_STRPTIME(signup_date, '%d-%b-%y')
                    ), 
                    '%d/%m/%Y'
                ) AS signup_date,
                
                -- 5a. Country: Standardize known variants to 2-letter codes natively
                CASE 
                    WHEN LOWER(REGEXP_REPLACE(country, '[^a-zA-Z]', '', 'g')) IN ('india', 'in', 'ind') THEN 'IN'
                    WHEN LOWER(REGEXP_REPLACE(country, '[^a-zA-Z]', '', 'g')) IN ('unitedstates', 'us', 'usa') THEN 'US'
                    WHEN LOWER(REGEXP_REPLACE(country, '[^a-zA-Z]', '', 'g')) IN ('unitedkingdom', 'uk') THEN 'UK'
                    WHEN LOWER(REGEXP_REPLACE(country, '[^a-zA-Z]', '', 'g')) = 'ae' THEN 'AE'
                    WHEN LOWER(REGEXP_REPLACE(country, '[^a-zA-Z]', '', 'g')) = 'sg' THEN 'SG'
                    ELSE UPPER(TRIM(country))
                END AS country,
                
                -- 5b. City: Title case for cities using the same transformation (handles multi-word cities like "New York")
                array_to_string(
                    list_transform(
                        string_split(regexp_replace(trim(city), '\s+', ' ', 'g'), ' '), 
                        x -> upper(substr(x, 1, 1)) || lower(substr(x, 2))
                    ), 
                    ' '
                ) AS city

            FROM standardized_domains
        )"""