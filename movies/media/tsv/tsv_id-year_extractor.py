import csv

dataset = {}
iterator = 0
out = open("data.txt", 'w', encoding="utf8")
with open('data.tsv', encoding="utf8") as tsvfile:
    tsvfile.seek(0)
    reader = csv.DictReader(tsvfile, dialect='excel-tab')
    for row in reader:
        if row['titleType'] == "movie":
            id = str(row["tconst"]).replace("tt","")
            year = row["startYear"]
            dataset[id] = year
            tmp_to_write = str(id) + "," + str(year) + "\n"
            out.write(tmp_to_write)
            print(iterator)
            iterator += 1

out.close()
tsvfile.close()



