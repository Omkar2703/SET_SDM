import os
from flask import Flask, render_template, request
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlglot import parse, exp 

# Initialization
app = Flask(__name__)

# Initialize the AI model (using GPT-4o-mini as planned)
llm = ChatOpenAI(model="gpt-4o-mini")

def generate_schema_and_diagram(prompt_text):
    """
    PHASE 1: Uses an AI model to generate SQL schema and Mermaid.js diagram.
    """
    print(f"Generating for prompt: {prompt_text}")

    generation_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a database design assistant. You must generate BOTH a complete SQL schema and a valid Mermaid.js ERD diagram. Respond with the SQL first, then the Mermaid.js code inside a 'mermaid' code block."),
        ("user", f"Generate a database model for the following concept: {prompt_text}")
    ])

    chain = generation_prompt | llm

    try:
        response = chain.invoke({"prompt": prompt_text})
        content = response.content

        sql_schema = content.split("```sql")[1].split("```")[0].strip()
        mermaid_code = content.split("```mermaid")[1].split("```")[0].strip()

        return sql_schema, mermaid_code

    except Exception as e:
        print(f"Error generating schema: {e}")
        return f"Error: {e}", "graph TD\n    Error[Error generating diagram]"

def check_schema(sql_schema):
    """
    PHASE 2: Uses SQLGlot to run static checks on the schema.
    Checks for:
    1. Naming Conventions (all lowercase tables)
    2. Missing Primary Keys
    3. Invalid Foreign Keys (referencing non-existent tables)
    """
    report = []
    try:
        parsed_expressions = parse(sql_schema)
        if not parsed_expressions:
            report.append({"type": "error", "message": "SQL schema is empty or could not be parsed."})
            return report

        tables = {}
        # First pass: find all table names
        for expr in parsed_expressions:
            if isinstance(expr, exp.Create) and expr.kind == 'TABLE':
                table_name = expr.this.this.name
                tables[table_name] = {'pk': False}
                
                # 1. Naming Convention Check
                if not table_name.islower():
                    report.append({
                        "type": "warning", 
                        "table": table_name,
                        "message": f"Naming Convention: Table '{table_name}' is not in lowercase."
                    })
                
                # Check for PK in constraints
                for constraint in expr.constraints:
                    if isinstance(constraint, exp.PrimaryKey):
                        tables[table_name]['pk'] = True
                        
                # Check for PK in column definitions (e.g., id INT PRIMARY KEY)
                for col_def in expr.find_all(exp.ColumnDef):
                    if any(isinstance(c, exp.PrimaryKey) for c in col_def.constraints):
                         tables[table_name]['pk'] = True

        # Second pass: check PKs and FKs
        for expr in parsed_expressions:
            if isinstance(expr, exp.Create) and expr.kind == 'TABLE':
                table_name = expr.this.this.name
                
                # 2. Primary Key Check
                if not tables[table_name]['pk']:
                    report.append({
                        "type": "error", 
                        "table": table_name,
                        "message": f"Missing Primary Key: Table '{table_name}' does not have a PRIMARY KEY defined."
                    })
                
                # 3. Foreign Key Check
                for constraint in expr.constraints:
                    if isinstance(constraint, exp.ForeignKey):
                        ref_table = constraint.find(exp.Reference).this.this.name
                        if ref_table not in tables:
                            report.append({
                                "type": "error",
                                "table": table_name,
                                "message": f"Invalid Foreign Key: Table '{table_name}' has a FOREIGN KEY that references a non-existent table '{ref_table}'."
                            })

        if not report:
             report.append({"type": "success", "message": "All static checks passed!"})

        return report

    except Exception as e:
        # This will catch errors in SQLGlot parsing itself
        report.append({"type": "error", "message": f"Schema Parsing Error: {str(e)}"})
        return report

# --- 3. UPDATED INDEX ROUTE ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form['prompt']
        
        # --- Phase 1 Call ---
        sql_schema, mermaid_diagram = generate_schema_and_diagram(prompt)
        
        # --- Phase 2 Call ---
        static_report = None
        if "Error:" not in sql_schema: # Only check if schema generation was successful
            static_report = check_schema(sql_schema)
        
        # --- Render with all results ---
        return render_template('index.html', 
                               sql_schema=sql_schema, 
                               mermaid_diagram=mermaid_diagram,
                               prompt_text=prompt,
                               static_report=static_report) 

    return render_template('index.html', 
                           sql_schema=None, 
                           mermaid_diagram=None, 
                           prompt_text=None, 
                           static_report=None)

if __name__ == '__main__':
    app.run(debug=True)

