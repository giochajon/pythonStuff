import datetime
import xlsxwriter
import names
import random


##############################################
#############  CREATE   #####################
#############################################

workbook = xlsxwriter.Workbook('invoice2.xlsx')
worksheet = workbook.add_worksheet('sheet 4')
worksheet.write('A1', 'Date')
worksheet.write('B1', 'Client Name')
worksheet.write('C1', 'Invoice #')
worksheet.write('D1', 'Items')
worksheet.write('E1', '$ Amount')


##################################
############  DATE ###############
##################################

start = datetime.datetime.strptime("01-03-2019", "%d-%m-%Y")
end = datetime.datetime.strptime("28-03-2019", "%d-%m-%Y")
date_generated = [
    start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]


##################################
############  ITEMS/NAMES #######
##################################

invoice_number = 400
secure_random = random.SystemRandom()
names_random = []
counter = 15
x = 0
while x < counter:
    names_random.append(names.get_first_name())
    x = x+1


##################################
###########  POPULATE ############
##################################
row = 1
column = 0
for date in date_generated:
    y = 0
    while y < 5:
        worksheet.write(row, column, date.strftime("%d-%m-%Y"))
        worksheet.write(row, column + 1, secure_random.choice(names_random))
        worksheet.write(row, column + 2, invoice_number)
        worksheet.write(row, column + 3, random.randint(1, 5))
        worksheet.write(row, column + 4, random.randint(1, 20000))
        row += 1
        invoice_number += 1
        y += 1
# VALIDATION

worksheet.data_validation('D2:D10000', {
    'validate': 'integer',
    'criteria': '>',
    'value': 0
})

worksheet.data_validation('A2:A10000', {
    'validate': 'date',
    'criteria': 'between',
    'minimum': start,
    'maximum': end
})

worksheet.data_validation('C2:C10000', {
    'validate': 'custom',
    'criteria': '>',
    'value': 0
})


workbook.close()
