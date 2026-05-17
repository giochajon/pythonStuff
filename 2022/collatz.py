
num = input('ingrese cualquier numero:')
result = int(num)
while result != 1:
    if result % 2 == 0: 
        result =int( result/2)
    else:
        result =int( (result * 3)+1)
    print (result)

