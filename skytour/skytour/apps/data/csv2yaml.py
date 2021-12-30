import csv

pk = 1
with open('constellation.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        print("- model: utils.constellation")
        print("  pk: {}".format(pk))
        print("  fields:")
        print("    abbreviation: {}".format(row[0]))
        print("    name: {}".format(row[1]))
        print("    genitive: {}".format(row[2]))
        pk += 1