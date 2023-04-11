import csv


def writeDictToCSV(csv_file, csv_columns, dict_data):
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    for d in dict_data:
        print(d)
        print("Link objects")
        for l in dict_data[d]:
            print(l)
        if len(dict_data[d]) != 5:
            print("Weird length, skipping")
            continue
        writer.writerow(
            {
                'link': d,
                'title': dict_data[d][0],
                'runtime': dict_data[d][1],
                'language': dict_data[d][2],
                'runtime-perf': dict_data[d][3],
                'memory-perf': dict_data[d][4],
            })


def writeSubmissionsToCSV(dict_data):
    with open('data.csv', 'w', newline='') as csvfile:
        writeDictToCSV(csvfile, ["link", "title",
                       "runtime", "language", "runtime-perf", "memory-perf"], dict_data)
