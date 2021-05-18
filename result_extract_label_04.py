from collections import defaultdict
import os
import re


def main():
    input_path = "./result/complete_format/"
    output_path = "./result/label/"
    files = os.listdir(input_path)
    # print()
    # print(len(files))
    # print()
    for file in files:
        dict = defaultdict(int)
        # 总字数
        t_num = 0
        # 总语块字数
        c_num = 0
        file_name = file.split("_")[0]
        with open(input_path + file, "r") as f:
            lines = f.readlines()
        chunks = []
        with open(output_path + file_name + "_labels.txt", "w") as f:
            for line in lines:
                if line.startswith("# length"):
                    t_num += int(line.split("=")[1].strip())
                elif not line.startswith("#") and line != "\n":
                    ret = re.findall('\[([^\[\]]*)\]', line)
                    c = ""
                    for p in ret:
                        c += p.split(" ")[0]
                        try:
                            tag = p.split(" ")[1]
                        except:
                            print(p)
                    c = c + tag
                    chunks.append(c)
                    dict[tag] += 1
                elif line == "\n":
                    for chunk in chunks:
                        c_num += len(chunk)
                        f.write(chunk + " ")
                    f.write("\n")
                    chunks = []
        print(file_name + "\n总字数：" + str(t_num) + "\n总语块字数：" + str(c_num))
        print(dict)


if __name__ == "__main__":
    main()