class SchemaProfiler:
    """Handles Schema-level issues like column mismatches"""
    def __init__(self, conn):
        self.conn = conn

    def profile(self):
        raw_cols = [col[0] for col in self.conn.execute("DESCRIBE raw_data").fetchall()]
        ref_cols = [col[0] for col in self.conn.execute("DESCRIBE ref_data").fetchall()]
        
        extra_cols = set(raw_cols) - set(ref_cols)
        missing_cols = set(ref_cols) - set(raw_cols)
        
        issues = []
        if extra_cols:
            issues.append(f"Extra columns found in raw data: {', '.join(extra_cols)}")
        if missing_cols:
            issues.append(f"Missing columns in raw data: {', '.join(missing_cols)}")
            
        return {
            "status": "Failed" if issues else "Passed",
            "issues": issues,
            "ref_columns": ref_cols
        }