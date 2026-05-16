from rules.null_rule import NullRule
from rules.duplicate_rule import DuplicateRule
from rules.domain_rule import DomainRule
from rules.format_rule import FormatRule

class ContentProfiler:
    """Iterates through registered rules dynamically"""
    def __init__(self, conn):
        self.conn = conn
        # Register new rules here
        self.rules = [NullRule(), DuplicateRule(), DomainRule(), FormatRule()]

    def profile(self, table_name="raw_data"):
        report = []
        for rule in self.rules:
            result = rule.evaluate(self.conn, table_name)
            report.append({
                "Rule": rule.name,
                "Violations": result["violations"],
                "Description": result["description"],
                "Rule_Obj": rule
            })
        return report