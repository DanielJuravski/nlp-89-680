import sys


def removeTags(file):
    data = []
    with open(file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        for line in content:
            clean_sen = []
            pairs = line.split(" ")
            for pair in pairs:
                arr = pair.rsplit("/", 1)
                clean_sen.append(arr[0])
            data.append(clean_sen)

    return data


def writeToFile(file, data):
    with open(file, 'w') as f:
        for i in range(len(data)):
            f.write("%s" % data[i][0])
            for k in range(1, len(data[i])):
                f.write(" %s" % data[i][k])
            f.write("\n")



if __name__ == '__main__':
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]

    clean_data = removeTags(input_file_name)
    writeToFile(output_file_name, clean_data)
    pass