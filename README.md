# Data Quality \& SQL Repair Studio



###### Brightlife Care - Data Engineering Internship Assignment



This is a web application designed to automate the manual loop of data quality checks. It ingests a raw dataset, profiles it against a clean reference schema, identifies data quality issues, generates runnable ANSI/DuckDB compliant SQL transformations to fix them and creates a clean and downloadable .txt file summarizing the issues found and the exact SQL transformations applied to fix them with a short explanation for each CTE.



###### Features

* **Automated Profiling**: Detects schema mismatches, null violations, duplicates, domain discrepancies, and format inconsistencies.
* **Auto-SQL Generation**: Dynamically stitches together Common Table Expressions (CTEs) into a fully runnable SQL script to fix the identified issues.
* **Execution Engine**: Uses DuckDB to test-execute the generated SQL and preview the cleaned dataset instantly.
* **AI Reporting**: Integrates with Gemini 2.5 Flash-Lite to generate and download comprehensive PDF summaries of the data quality pipeline.



###### Setup \& Installation



Prerequisites

\* Python 3.9 or higher installed on your machine.

\* Git installed to clone the repository.



**1. Clone the Repository**

git clone https://github.com/YASHDAHIYA449/SQLStudioAI.git



**2. Navigate inside the file directory**



**3. Download the requirements.txt and run the app**

\# Install the required libraries

pip install -r requirements.txt



\# Navigate to the app directory

cd app



\# Start the Streamlit application

streamlit run main.py



###### Architecture \& Extensibility



This application uses an extensible, object-oriented Rule Engine. A key architectural decision was ensuring that adding a new data quality check does \*\*not\*\* require modifying the core profiling engine (`content\_profiler.py`) or the SQL generation logic.



To Add a New Issue Type



You can add a new custom check in just three steps:



**1. Create a New Rule Class**

Navigate to the `app/rules/` directory and create a new Python file (e.g., `custom\_rule.py`).



**2. Inherit from BaseRule**

Your new class must inherit from `BaseRule` and implement its abstract methods. Here is a template:



```python

from .base\_rule import BaseRule



class CustomRule(BaseRule):

&#x20;   @property

&#x20;   def name(self): return "My Custom Check Name"

&#x20;   

&#x20;   @property

&#x20;   def issue\_type(self): return "content"



&#x20;   def evaluate(self, conn, table\_name: str):

&#x20;       # 1. Run a DuckDB query to count how many rows violate your rule

&#x20;       query = f"SELECT COUNT(\*) FROM {table\_name} WHERE my\_column IS BAD;"

&#x20;       violations = conn.execute(query).fetchone()\[0]

&#x20;       return {"violations": violations, "description": "Description of the issue."}



&#x20;   def get\_sql\_transformation(self):

&#x20;       # 2. Return the SQL CTE that fixes the data

&#x20;       return """

&#x20;       custom\_fix\_cte AS (

&#x20;           SELECT \*, 

&#x20;             CASE WHEN my\_column IS BAD THEN 'FIXED' ELSE my\_column END AS my\_column

&#x20;           FROM previous\_cte\_name

&#x20;       )"""



**3. Register the Rule**

Open app/profiler/content\_profiler.py, import your new rule, and add it to the self.rules list inside the \_\_init\_\_ method:



Python

from rules.custom\_rule import CustomRule



class ContentProfiler:

&#x20;   def \_\_init\_\_(self, conn):

&#x20;       self.conn = conn

&#x20;       # Simply append your new rule to the list!

&#x20;       self.rules = \[

&#x20;           NullRule(), 

&#x20;           DuplicateRule(), 

&#x20;           DomainRule(), 

&#x20;           FormatRule(), 

&#x20;           CustomRule()  # <--- New rule registered here

&#x20;       ]



The application will automatically detect the new rule, run the profiling check, display the results in the UI, and stitch the new SQL transformation into the final auto-generated repair script.

