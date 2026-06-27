import openpyxl

wb = openpyxl.load_workbook(r'C:\Users\yu\Desktop\耳机品牌统计.xlsx')
ws = wb['蓝牙耳机品牌']

for row in ws.iter_rows(min_row=1, values_only=True):
    brand = str(row[0]) if row[0] else ''
    if '塞那' in brand or 'Sanag' in brand or 'sanag' in brand:
        print('||'.join([str(c) if c else '' for c in row]))
