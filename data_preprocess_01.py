import re
from stanfordcorenlp import StanfordCoreNLP
import os
from tqdm import tqdm


# 分句
def ssplit(line):
    line = re.sub(r'([。！？\?])([^”’])', r"\1\n\2", line)
    line = re.sub(r'(\.{6})([^”’])', r"\1\n\2", line)
    line = re.sub(r'(\…{2})([^”’])', r"\1\n\2", line)
    line = re.sub(r'([。！？\?][”’])([^，。！？\?])', r'\1\n\2', line)
    return line.split("\n")


# 预处理
def preprocess(input_path, output_path):

    # 调用corenlp
    nlptool = StanfordCoreNLP('http://202.112.194.61', port=8085, lang='zh')

    files = os.listdir(input_path)
    files.sort()

    # 如果预处理的三类子文件夹不存在，那就先创建一下
    if not os.path.exists(output_path + "tokenized/"):
        os.mkdir(output_path + "tokenized/")
    if not os.path.exists(output_path + "ssplit/"):
        os.mkdir(output_path + "ssplit/")
    if not os.path.exists(output_path + "segmentation/"):
        os.mkdir(output_path + "segmentation/")

    for file in files:
        # 分句
        res_ssplit = []
        # 分词
        res_seg = []
        # 分词，词性标注
        res_tokenized = []

        print("open file " + file)

        with open(input_path + file, 'r') as f:
            lines = f.readlines()

        for line in tqdm(lines):

            # 去掉每句开头人名(不一定每句开头都有人名)
            try:
                line = line.split(":", 1)[1]
            except:
                pass
            line = line.strip()
            # 把感叹号替换成分句函数能处理的
            line = line.replace("!", "！")
            # 去掉百分号（百分号stanford无法处理）
            line = line.replace("%", "")
            # print(line)

            sents = ssplit(line)
            for sent in sents:
                try:
                    res_ssplit.append(sent)
                    sent = nlptool.pos_tag(sent)
                    s_tokenzied = ""
                    s_seg = ""
                    for t in sent:
                        ret = re.search('[\'|\"](.*)[\'|\"].*\'(.*)\'', str(t))
                        s_tokenzied += ret.group(1) + "_" + ret.group(2) + " "
                        s_seg += ret.group(1) + " "
                    res_tokenized.append(s_tokenzied + "\n")
                    res_seg.append(s_seg + "\n")
                except:
                    print("fail to preprocess: " + sent)

        with open(output_path + "tokenized/" + file.split(".")[0] + "_tokenized.txt", "w") as f:
            for i in res_tokenized:
                f.write(i)
        with open(output_path + "ssplit/" + file.split(".")[0] + "_ssplit.txt", "w") as f:
            for i in res_ssplit:
                f.write(i + "\n")
        with open(output_path + "segmentation/" + file.split(".")[0] + "_segmentation.txt", "w") as f:
            for i in res_seg:
                f.write(i)
        print("file " + file + " processed")


def main():
    # 预处理数据（分句、分词、词性标注）
    # 原语料
    # input_file_path = "./data/"
    input_file_path = "./data_toy/"
    # 预处理数据输出路径
    # output_file_path = "./data_preprocessed/"
    output_file_path = "./data_toy_preprocessed/"
    preprocess(input_file_path, output_file_path)


if __name__ == "__main__":
    main()