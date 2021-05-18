import os
import re


def main():
    # 待统计的文件路径
    path = "./result/label/"

    dict = {'BC': 0, 'BD': 0, 'GS': 0, 'GI': 0,
            'GC': 0, 'BJD': 0, 'BJF': 0, 'MP': 0, 'WP': 0}
    files = os.listdir(path)
    files.sort()
    fout = open("result/statistics.txt", "w")
    for file in files:
        file_name = file.split("_")[0]
        print("processing " + file)
        # print("mistake:")
        num = 0
        dict_chunk = {'BC': 0, 'BD': 0, 'GS': 0, 'GI': 0,
                      'GC': 0, 'BJD': 0, 'BJF': 0, 'MP': 0, 'WP': 0}
        with open(path + file, "r") as f:
            lines = f.readlines()
        for line in lines:
            if line == "\n":
                continue
            chunks = line.strip().split()
            for chunk in chunks:
                chunk = chunk.strip()
                try:
                    text = re.search('[\u4E00-\u9FA5]+', chunk).group()
                    label = re.search('[A-Z]+', chunk).group()
                    # print(text, label)
                    num += len(text)
                    dict_chunk[label] += 1
                except:
                    print("mistake: " + chunk)

        for key in dict_chunk.keys():
            dict[key] += dict_chunk[key]

        fout.write(file_name + "\n")
        # fout.write("总字数：\n")
        fout.write("总语块字数：" + str(num) + "\n")
        fout.write("总语块数：" + str(sum(dict_chunk.values())) + "\n")
        fout.write(str(dict_chunk) + "\n")
        fout.write("\n")

    fout.close()

    print(dict)


if __name__ == "__main__":
    main()