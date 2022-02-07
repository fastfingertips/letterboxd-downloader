csvPath = input('CSV NAME: ')
csvfile = open(csvPath, 'r', encoding="utf8").readlines() #: lines list
filename = 1
split = 1500
for i in range(len(csvfile)):
    if i % split == 0:
        csvfile.insert(i+split,csvfile[0]) #: keep header
        open(str(filename) + '.csv', 'w+', encoding="utf8").writelines(csvfile[i:i+split])
        filename += 1