import openpyxl, sys, traceback, io
try:
    wb = openpyxl.load_workbook(r'C:\Users\yu\Desktop\耳机品牌统计.xlsx', data_only=True)
    ws = wb['蓝牙耳机品牌']
    for row in ws.iter_rows(values_only=True):
        if row[0] and 'Newyu' in str(row[0]):
            print(f'Row: {list(row)}')
except Exception as e:
    with open(r'C:\Users\yu\Desktop\earbuds-review\_excel_error.txt', 'w') as f:
        traceback.print_exc(file=f)
