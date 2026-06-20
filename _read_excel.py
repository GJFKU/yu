import openpyxl, sys, traceback

try:
    wb = openpyxl.load_workbook(r'C:\Users\yu\Desktop\耳机品牌统计.xlsx')
    print('Sheet names:', wb.sheetnames)
    ws = wb[wb.sheetnames[0]]
    print('Header row:', [cell.value for cell in ws[1]])
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        print(row)
except Exception as e:
    traceback.print_exc()
    sys.exit(1)
