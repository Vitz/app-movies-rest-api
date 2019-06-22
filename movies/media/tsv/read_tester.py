import csv

dataset = {}
iterator = 0
with open('data.txt', encoding="utf8") as txtfile:
    txtfile.seek(0)
    reader = csv.reader(txtfile)
    for row in reader:
        dataset[row[0]] = row[1]

print(dataset["0000739"])
txtfile.close()



