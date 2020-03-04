import os

input_file = 'test' + os.sep + 'output' + os.sep + 'klhs_photographs.csv'

with open(input_file, 'r') as f:
    col_names = f.readline().rstrip('\n')

col_names = col_names.split(',')
print('[', end='')
for col_name in col_names:
    print("'%s'," % col_name, end=' ')
print(']')
