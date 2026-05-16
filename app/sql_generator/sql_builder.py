def generate_repair_sql(schema_ref_cols, active_rules):
    """
    Stitches together the CTEs from the triggered rules into a final 
    ANSI/DuckDB compliant SQL query
    """
    sql_script = "-- ==========================================\n"
    sql_script += "-- AUTO-GENERATED SQL REPAIR SCRIPT\n"
    sql_script += "-- ==========================================\n\n"
    
    sql_script += "WITH "
    
    ctes = []
    for rule in active_rules:
        # Strip the 'WITH ' or generic names, just grab the CTE body
        cte_body = rule.get_sql_transformation().replace("WITH ", "").strip()
        ctes.append(cte_body)
        
    sql_script += ",\n\n".join(ctes)
    
    # Final SELECT to fix schema drift (drop extra columns, align order)
    select_cols = ", ".join(schema_ref_cols)
    sql_script += f"""
    
    -- Final Projection aligning with Reference Schema
    SELECT 
        {select_cols}
    FROM cleaned_formats
    ORDER BY customer_id;
    """
    
    return sql_script