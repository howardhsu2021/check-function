import re
import os
import sys
import subprocess

def analyze_script(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Function keyword
    function_keywords = [
        'sc.textFile()', 'saveAs()', 'ImpalaAccess()', 'HBaseConfiguration()',
        'DriverManager()', 'HDFS()', 'Hadoop()', 'sqoop()'
    ]
    # Shell keyword
    shell_keywords = ['subprocess', 'os.popen', 'os.system']
    # SQL keyword
    sql_pattern = re.compile(r'\b(CREATE TABLE|SELECT|INSERT|UPDATE|DELETE|DROP TABLE)\b', re.IGNORECASE)
    
    methods_with_targets = {}
    sql_statements = []
    shell_lines = []
    keyword_counts = {kw: 0 for kw in function_keywords + shell_keywords}
    sql_count = 0
    total_keyword_count = 0
    
    current_method = None
    method_pattern = re.compile(r'\bdef\s+(\w+)\s*\(')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line.startswith('#'):
            continue  # 忽略註解行
        
        method_match = method_pattern.search(line)
        if method_match:
            current_method = method_match.group(1)
        
        for keyword in function_keywords:
            if keyword in line:
                keyword_counts[keyword] += 1
                total_keyword_count += 1
                if current_method:
                    methods_with_targets.setdefault(current_method, []).append((i, keyword))
        
        for keyword in shell_keywords:
            if keyword in line:
                keyword_counts[keyword] += 1
                shell_lines.append((i, line))
        
        sql_match = sql_pattern.search(line)
        if sql_match:
            sql_count += 1
            sql_statements.append((i, line))
    
    print(f"\nAnalysis of {file_path}:")
    print("Methods using Function keywords and SQL statements:")
    for method, occurrences in methods_with_targets.items():
        print(f"  {method}:")
        for line_num, keyword in occurrences:
            print(f"    - Line {line_num}: {keyword}")
    
    print("\nSQL Statements:")
    for line_num, statement in sql_statements:
        print(f"  Line {line_num}: {statement}")
    
    print("\nLines executing shell commands:")
    for line_num, content in shell_lines:
        print(f"  Line {line_num}: {content} (shell)")
    
    print("\nKeyword occurrences:")
    for keyword, count in keyword_counts.items():
        print(f"  {keyword}: {count}")
    
    print(f"\nTotal Function keyword occurrences: {total_keyword_count}")
    print(f"SQL statements count: {sql_count}")

def analyze_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                analyze_script(os.path.join(root, file))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 check_function \"directory_path\"")
        sys.exit(1)
    
    directory_path = os.path.expanduser(sys.argv[1])
    analyze_directory(directory_path)
