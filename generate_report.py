#!/c/Users/Sin/AppData/Local/Programs/Python/Python314/python.exe
# -*- coding: utf-8 -*-
import subprocess
import os
from datetime import datetime

sqlcmd = r'C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\180\Tools\Binn\sqlcmd.exe'
outdir = r'D:\budget\screenshots'
os.makedirs(outdir, exist_ok=True)

def run_sql(query):
    """Run SQL query and return output as UTF-8 string."""
    cmd = [sqlcmd, '-S', r'.\SQLEXPRESS', '-E', '-C', '-d', 'teaching', '-W', '-Q', query]
    result = subprocess.run(cmd, capture_output=True)
    try:
        return result.stdout.decode('gbk')
    except:
        return result.stdout.decode('utf-8', errors='replace')

def query_to_table(query):
    """Convert SQL results to HTML table."""
    output = run_sql(query)
    lines = [l.strip() for l in output.split('\n') if l.strip()]
    if len(lines) < 3:
        return f"<p>No results</p>"

    # Find the separator line (-----)
    sep_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('---') or line.startswith('－－－'):
            sep_idx = i
            break

    if sep_idx < 1:
        return f"<pre>{output}</pre>"

    # Parse headers
    headers = [h.strip() for h in lines[sep_idx - 1].split() if h.strip()]

    # Parse data rows (after separator, skipping the "(x rows affected)" line
    rows = []
    for line in lines[sep_idx + 1:]:
        if '行受影响' in line or 'rows affected' in line or not line.strip():
            continue
        # Split by whitespace
        parts = line.strip().split()
        if parts and parts[0].isdigit() or (parts and len(parts) == len(headers)):
            rows.append(parts[:len(headers)])

    html = '<table>\n<tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr>\n'
    for row in rows:
        html += '<tr>'
        for val in row:
            html += f'<td>{val}</td>'
        html += '</tr>\n'
    html += '</table>\n'
    return html

def section(title, sql_text, table_html, note=''):
    sql_escaped = sql_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    html = '<div class="section">\n'
    html += f'<h3>{title}</h3>\n'
    html += f'<div class="sql">{sql_escaped}</div>\n'
    if note:
        html += f'<p class="note">{note}</p>\n'
    html += f'<div class="result">{table_html}</div>\n'
    html += '</div>\n'
    return html

# ========== Build HTML ==========
html_parts = []
html_parts.append(f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>数据库理论与技术 实验报告3-4</title>
<style>
body {{ font-family: 'Microsoft YaHei', SimSun, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
h1 {{ color: #1a1a2e; text-align: center; border-bottom: 3px solid #1a1a2e; padding-bottom: 10px; }}
h2 {{ color: #16213e; margin-top: 30px; background: #e8e8e8; padding: 8px 15px; border-left: 5px solid #0f3460; }}
h3 {{ color: #0f3460; margin-top: 20px; }}
.section {{ background: white; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); page-break-inside: avoid; }}
.sql {{ background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 5px; font-family: Consolas, monospace; white-space: pre-wrap; overflow-x: auto; }}
.result {{ margin-top: 15px; }}
table {{ border-collapse: collapse; width: 100%; font-family: Consolas, monospace; font-size: 14px; }}
th {{ background: #0f3460; color: white; padding: 10px 12px; text-align: left; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #ddd; }}
tr:nth-child(even) {{ background: #f8f8f8; }}
tr:hover {{ background: #e8f0fe; }}
.answer {{ background: #fffde7; border-left: 5px solid #fdd835; padding: 15px; margin-top: 15px; border-radius: 5px; }}
.note {{ color: #666; font-style: italic; }}
</style>
</head>
<body>
<h1>数据库理论与技术 实验报告3-4</h1>
<p style="text-align:center;color:#666;">学院：空间安全学院 | 班级：管控22-</p>
''')

# ====== Base Data ======
html_parts.append('<h2>基础数据查看</h2>\n')
html_parts.append(section('学生表 (dbo.student)',
    'SELECT sno, sname, spec, birthday, email, sex, scholarship FROM dbo.student',
    query_to_table('SELECT sno, sname, spec, birthday, email, sex, scholarship FROM dbo.student')))

html_parts.append(section('课程表 (dbo.course)',
    'SELECT cno, cname, credit, teacher FROM dbo.course',
    query_to_table('SELECT cno, cname, credit, teacher FROM dbo.course')))

html_parts.append(section('选课表 (dbo.student_course)',
    'SELECT sno, cno, grade FROM dbo.student_course ORDER BY sno, cno',
    query_to_table('SELECT sno, cno, grade FROM dbo.student_course ORDER BY sno, cno')))

# ====== Experiment 3 ======
html_parts.append('<h2>实验三：SQL Server 数据查询</h2>\n')

# Q1a: Insert
run_sql("INSERT INTO dbo.student_course VALUES ('9912301','010106',90)")
run_sql("INSERT INTO dbo.student_course VALUES ('9912301','010107',90)")
html_parts.append(section('【实验三 第1题a】插入两条记录',
    "INSERT INTO dbo.student_course VALUES ('9912301', '010106', 90);\nINSERT INTO dbo.student_course VALUES ('9912301', '010107', 90);",
    query_to_table("SELECT sno, cno, grade FROM dbo.student_course WHERE sno='9912301' ORDER BY cno"),
    '向 Student_Course 表插入两条记录'))

# Q1b
html_parts.append(section('【实验三 第1题b】查询选修课程超过3门且成绩合格的学生学号',
    "SELECT sno FROM dbo.student_course\nGROUP BY sno\nHAVING COUNT(*) > 3 AND MIN(grade) >= 60;",
    query_to_table("SELECT sno FROM dbo.student_course GROUP BY sno HAVING COUNT(*) > 3 AND MIN(grade) >= 60")))

# Q2: Create S_avggrade
run_sql("IF OBJECT_ID('dbo.S_avggrade','U') IS NOT NULL DROP TABLE dbo.S_avggrade")
run_sql("SELECT sc.sno, s.sname, AVG(sc.grade) as avggrade INTO dbo.S_avggrade FROM dbo.student_course sc JOIN dbo.student s ON sc.sno=s.sno GROUP BY sc.sno, s.sname")
html_parts.append(section('【实验三 第2题】创建S_avggrade表',
    "SELECT sc.sno, s.sname, AVG(sc.grade) as avggrade\nINTO dbo.S_avggrade\nFROM dbo.student_course sc\nJOIN dbo.student s ON sc.sno = s.sno\nGROUP BY sc.sno, s.sname;",
    query_to_table("SELECT sno, sname, avggrade FROM dbo.S_avggrade ORDER BY sno"),
    '将查询结果存储到新表 S_avggrade(sno, sname, avggrade)'))

# Q3
html_parts.append(section('【实验三 第3题】查询每名学生的选课数量和总成绩',
    "SELECT sc.sno, s.sname, COUNT(*) as course_count, SUM(sc.grade) as total_grade\nFROM dbo.student_course sc\nJOIN dbo.student s ON sc.sno = s.sno\nGROUP BY sc.sno, s.sname\nORDER BY sc.sno ASC;",
    query_to_table("SELECT sc.sno, s.sname, COUNT(*) as course_count, SUM(sc.grade) as total_grade FROM dbo.student_course sc JOIN dbo.student s ON sc.sno=s.sno GROUP BY sc.sno, s.sname ORDER BY sc.sno ASC"),
    '按学号升序排列'))

# Q4
html_parts.append(section('【实验三 第4题】查询姓李、陈、张的学生',
    "SELECT sno, sname FROM dbo.student\nWHERE sname LIKE N'李%' OR sname LIKE N'陈%' OR sname LIKE N'张%';",
    query_to_table("SELECT sno, sname FROM dbo.student WHERE sname LIKE N'李%' OR sname LIKE N'陈%' OR sname LIKE N'张%'")))

# Q5
print("Running Q5...")
html_parts.append(section('【实验三 第5题】查询非软件专业成绩<60的学生',
    "SELECT s.sno, s.sname, c.cname, sc.grade\nFROM dbo.student s\nJOIN dbo.student_course sc ON s.sno = sc.sno\nJOIN dbo.course c ON sc.cno = c.cno\nWHERE s.spec != N'软件工程' AND sc.grade < 60;",
    query_to_table("SELECT s.sno, s.sname, c.cname, sc.grade FROM dbo.student s JOIN dbo.student_course sc ON s.sno=sc.sno JOIN dbo.course c ON sc.cno=c.cno WHERE s.spec != N'软件工程' AND sc.grade < 60"),
    '显示学号、姓名、课程名称和成绩'))

# ====== Experiment 4 ======
html_parts.append('<h2>实验四：SQL Server 视图</h2>\n')

# V2
run_sql("IF OBJECT_ID('V2','V') IS NOT NULL DROP VIEW V2")
run_sql("CREATE VIEW V2 AS SELECT c.cno, c.cname, c.teacher FROM dbo.course c JOIN dbo.student_course sc ON c.cno=sc.cno GROUP BY c.cno, c.cname, c.teacher HAVING AVG(sc.grade) < 60")
html_parts.append(section('【实验四 第1题】V2: 课程平均成绩<60的课程信息',
    "CREATE VIEW V2 AS\nSELECT c.cno, c.cname, c.teacher\nFROM dbo.course c\nJOIN dbo.student_course sc ON c.cno = sc.cno\nGROUP BY c.cno, c.cname, c.teacher\nHAVING AVG(sc.grade) < 60;",
    query_to_table("SELECT * FROM V2")))

# V3
run_sql("IF OBJECT_ID('V3','V') IS NOT NULL DROP VIEW V3")
run_sql("CREATE VIEW V3 AS SELECT c.cno, c.cname, c.credit FROM dbo.course c WHERE c.cno NOT IN (SELECT sc.cno FROM dbo.student_course sc WHERE sc.grade < 60)")
html_parts.append(section('【实验四 第2题】V3: 成绩均合格的课程信息',
    "CREATE VIEW V3 AS\nSELECT c.cno, c.cname, c.credit\nFROM dbo.course c\nWHERE c.cno NOT IN (\n    SELECT sc.cno FROM dbo.student_course sc\n    WHERE sc.grade < 60\n);",
    query_to_table("SELECT * FROM V3"),
    '所有学生成绩均>=60的课程（及格课程）'))

# V5
run_sql("IF OBJECT_ID('V5','V') IS NOT NULL DROP VIEW V5")
run_sql("CREATE VIEW V5 AS SELECT v.cno, v.cname, AVG(sc.grade) as avg_grade FROM V3 v JOIN dbo.student_course sc ON v.cno=sc.cno GROUP BY v.cno, v.cname")
html_parts.append(section('【实验四 第3题】V5: 基于V3查询平均成绩',
    "CREATE VIEW V5 AS\nSELECT v.cno, v.cname, AVG(sc.grade) as avg_grade\nFROM V3 v\nJOIN dbo.student_course sc ON v.cno = sc.cno\nGROUP BY v.cno, v.cname;",
    query_to_table("SELECT * FROM V5"),
    '在V3基础上创建，查询成绩均合格的课程的平均成绩'))

# V4
run_sql("IF OBJECT_ID('V4','V') IS NOT NULL DROP VIEW V4")
run_sql("CREATE VIEW V4 AS SELECT s.sno, s.sname, sc.grade FROM dbo.student s JOIN dbo.student_course sc ON s.sno=sc.sno JOIN dbo.course c ON sc.cno=c.cno WHERE c.cname=N'数据库理论与技术'")
html_parts.append(section('【实验四 第4题】V4: 选修数据库理论与技术课程的学生',
    "CREATE VIEW V4 AS\nSELECT s.sno, s.sname, sc.grade\nFROM dbo.student s\nJOIN dbo.student_course sc ON s.sno = sc.sno\nJOIN dbo.course c ON sc.cno = c.cno\nWHERE c.cname = N'数据库理论与技术';",
    query_to_table("SELECT sno, sname, grade FROM V4 ORDER BY grade DESC"),
    '按成绩降序排列'))

# V1
run_sql("IF OBJECT_ID('V1','V') IS NOT NULL DROP VIEW V1")
run_sql("CREATE VIEW V1 AS SELECT c.cno, c.cname, AVG(sc.grade) as avg_grade FROM dbo.course c JOIN dbo.student_course sc ON c.cno=sc.cno GROUP BY c.cno, c.cname")
html_parts.append(section('【实验四 第5题】V1: 课程号、课程名、平均成绩',
    "CREATE VIEW V1 AS\nSELECT c.cno, c.cname, AVG(sc.grade) as avg_grade\nFROM dbo.course c\nJOIN dbo.student_course sc ON c.cno = sc.cno\nGROUP BY c.cno, c.cname;",
    query_to_table("SELECT * FROM V1")))

# Answer for V1
html_parts.append('''
<div class="section">
<h3>【实验四 第5题】V1是否能更新？</h3>
<div class="answer">
<strong>答：</strong>V1视图<strong>不能</strong>更新（即不能进行INSERT、UPDATE、DELETE操作）。<br><br>
<strong>原因：</strong><br>
1. V1视图中包含聚合函数 AVG()，聚合结果是由多行数据计算而来的。<br>
2. V1视图使用了 GROUP BY 子句，每一行代表一组数据的聚合结果。<br>
3. 视图中的每一行并不直接对应基表中的某一行，而是多行数据经过计算（聚合）后的汇总结果。<br>
4. SQL Server规定，包含聚合函数、GROUP BY、DISTINCT等元素的视图为只读视图，系统无法确定如何将更新操作正确地映射回基表的原始行。<br>
5. 因此，V1视图不可更新。
</div>
</div>
''')

# Footer
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
html_parts.append(f'''
<div style="text-align:center;margin-top:40px;padding:20px;color:#999;border-top:1px solid #ddd;">
<p>数据库理论与技术 实验报告3-4 | 空间安全学院 管控22-</p>
<p style="font-size:12px;">Generated on: {now}</p>
</div>
</body>
</html>
''')

# Write the file
output_path = os.path.join(outdir, 'report.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(html_parts))

print(f'Report saved to: {output_path}')
