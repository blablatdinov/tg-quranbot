"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import ast
import os
from difflib import ndiff
from itertools import count
from pathlib import Path

from sqlfluff import fix


def file_paths():
    for dirpath, dirnames, filenames in os.walk('src'):
        for filename in filenames:
            if filename.endswith('.py') and filename != '__init__.py':
                path = (Path(dirpath) / filename)
                yield path


def normalize_query(query):
    lines = query.split('\n')
    for first_sql_line_idx, line in enumerate(lines):
        if line != '':
            break
    for indent in count():
        if lines[first_sql_line_idx][indent] != ' ':
            break
    return '\n'.join([
        line[indent:] for line in lines
    ]).strip() + '\n'


def rec(ast_elem, file_path):
    ignore_rules = ['LT01']
    if isinstance(ast_elem, ast.Assign):
        # if isinstance(ast_elem.value, ast.List | ast.Call | ast.ListComp):
        #         return
        if isinstance(ast_elem.value, ast.Str) and 'query' in ast_elem.targets[0].id:
            normalized_query = normalize_query(ast_elem.value.value)
            # errors = lint(normalized_query, 'postgres', exclude_rules=ignore_rules)
            fixed_query = fix(normalized_query, 'postgres', exclude_rules=ignore_rules)
            diff = ''.join(ndiff(
                normalized_query.splitlines(keepends=True),
                fixed_query.splitlines(keepends=True),
            ))
            if fixed_query == normalized_query:
                return
            print('--------------------')
            print(file_path)
            print(ast_elem.lineno)
            print(diff, end='')
            print('--------------------')
            # print(normalize_query(ast_elem.value.value))
            # pprint(errors)
    if isinstance(ast_elem, ast.ClassDef | ast.AsyncFunctionDef):
        [rec(elem, file_path) for elem in ast_elem.body]


def process_tree(tree, file_path):
    for elem in tree.body:
        rec(elem, file_path)


for file_path in file_paths():
    process_tree(ast.parse(file_path.read_text()), file_path)
