#coding=utf-8
import xlwt

# 创建一个workbook 设置编码
workbook = xlwt.Workbook(encoding = 'utf-8')
# 创建一个worksheet
worksheet = workbook.add_sheet('My Worksheet')


txt_list = list()
with open('/Users/liupeng/Downloads/兴业银行交易明细.txt','r') as fd:
    for item in fd.readlines():
        #print(item)
        line_list = item.split(' ')
        txt_list.append(line_list)

ctype = 1
xf = 0 # 扩展的格式化
for item in range(len(txt_list)):
    row = item
    for item2 in range(len(txt_list[item])):
        col = item2
        # 写入excel
        # 参数对应 行, 列, 值
        worksheet.write(row,col, label = txt_list[item][item2])
        # 保存
workbook.save('Excel_test.xls')

