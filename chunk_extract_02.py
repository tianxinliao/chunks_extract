import os
from tqdm import tqdm
import json
import re


# 读文件
def read_file(path):
    print()
    path_tokenized = path + "tokenized/"
    path_ssplit = path + "ssplit/"
    files_tokenized = os.listdir(path_tokenized)
    files_ssplit = os.listdir(path_ssplit)
    files_tokenized.sort()
    files_ssplit.sort()
    articles_tokenized = []
    articles_ssplit = []

    for file in files_tokenized:
        print("loading " + str(file))
        a = []
        with open(str(path_tokenized) + str(file), 'r') as f:
            lines = f.readlines()
        for line in lines:
            a.append(line.strip(" "))
        articles_tokenized.append(a)

    for file in files_ssplit:
        print("loading " + str(file))
        a = []
        with open(str(path_ssplit) + str(file), 'r') as f:
            lines = f.readlines()
        for line in lines:
            a.append(line.strip(" "))
        articles_ssplit.append(a)

    print("\nloading finished\n")
    return articles_tokenized, articles_ssplit


# 读取语块
def load_patterns_G(path):
    list = []
    with open(path,"r") as fin:
        lines = fin.readlines()
    for line in lines:
        list.append(line.strip())
    return list

# 读取语块
def load_patterns_B(path):
    list = []
    with open(path, "r") as fin:
        lines = fin.readlines()
    for line in lines:
        if line == "\n":
            continue
        pattern = line.split(":")[1].strip()
        pattern = str(pattern)
        list.append(pattern)
    return list


# 删掉无用的块
# def clean_useless(dict):
#     # 遍历每篇文章
#     for k, v in dict.items():
#         # 遍历每个句子
#         fs = []
#         for id, sent in v.items():
#             # 遍历每个类别
#             flags = []
#             for label, l in sent.items():
#                 print(label, l)
#                 # 如果该类别没有语块，直接删掉
#                 if l == []:
#                     flags.append(label)
#             print(flags)
#             for flag in flags:
#                 del sent[label]
#             if not sent:
#                 fs.append(id)
#         for f in fs:
#             del v[f]


# 匹配

# 未分词类部分
def match_G(pattern, sent):
    # 用于保存该句子匹配出来的语块，每个语块存为一个list，每个语块的各个部分存为一个dict
    p = []
    # 遍历语块集合中的每个语块
    for rule in pattern:
        ret = re.findall(rule, sent)
        if ret != []:
            spans = [i.span() for i in re.finditer(rule, sent)]
            for span in spans:
                l = []
                chunk = {}
                chunk['position'] = span
                chunk['text'] = sent[span[0]:span[1]]
                l.append(chunk)
                p.append(l)
    return p

# 分词类匹配
def match_B(pattern, sent):
    # 用于保存该句子匹配出来的语块，每个语块存为一个dict
    p = []
    # 遍历语块集合中的每个语块
    for rule in pattern:
        words = sent.strip().split(" ")
        ret = re.findall(rule, sent)
        if ret != []:
            # print(rule, ret)
            f0 = 0
            for i in ret:
                # 每个语块存为一个list，每个语块的部分存为一个dict
                l = []
                if type(i) != tuple:
                    chunk = {}
                    try:
                        chunk['id'] = words.index(i, f0)
                        chunk['text'] = i.split('_')[0]
                        f0 = words.index(i, f0) + 1
                        l.append(chunk)
                    except:
                        print(sent)
                        print(rule)
                        print(i)
                else:
                    # 在词列表中查找下一个词的起始位置
                    f = 0
                    for j in i:
                        chunk = {}
                        try:
                            chunk['id'] = words.index(j, f)
                            chunk['text'] = j.split('_')[0]
                            l.append(chunk)
                            # 找到语块的第一部分之后，下一部分从第一部分的下一个词开始找
                            f = words.index(j, f) + 1
                        except:
                            print(sent)
                            print(rule)
                            print(j)
                p.append(l)
    return p


def main():
    # 预处理完成之后的数据路径
    path_data = "./data_preprocessed/"
    # 输出路径
    path_output = "./result/chunks.json"

    # 读取数据
    articles_tokenized, articles_ssplit = read_file(path_data)

    # 读取语块
    pattern_GC = load_patterns_G('./pattern/GC.txt')
    pattern_GI = load_patterns_G('./pattern/GI.txt')
    pattern_GS = load_patterns_G('./pattern/GS.txt')
    pattern_BC = load_patterns_B('./pattern/BC.txt')
    pattern_BD = load_patterns_B('./pattern/BD.txt')
    pattern_BJD = load_patterns_B('./pattern/BJD.txt')
    pattern_BJF = load_patterns_B('./pattern/BJF.txt')

    for i, s in enumerate(pattern_BJF):
        pattern_BJF[i] = re.sub(r'^\\s\*', " ", s)
    for i, s in enumerate(pattern_BD):
        pattern_BD[i] = re.sub(r'^\\s\*', " ", s)
    for i, s in enumerate(pattern_BJD):
        pattern_BJD[i] = re.sub(r'^\\s\*', " ", s)

    # 提取出的语块结果
    result = {}
    # 匹配语块
    for i, article in enumerate(articles_ssplit):
        article_result = {}
        for j, sent in enumerate(tqdm(article)):
            chunks_GC = match_G(pattern_GC, sent)
            chunks_GI = match_G(pattern_GI, sent)
            chunks_GS = match_G(pattern_GS, sent)
            chunks_BC = match_B(pattern_BC, articles_tokenized[i][j])
            chunks_BD = match_B(pattern_BD, articles_tokenized[i][j])
            chunks_BJD = match_B(pattern_BJD, articles_tokenized[i][j])
            chunks_BJF = match_B(pattern_BJF, articles_tokenized[i][j])
            sent_chunks = {'GC': chunks_GC, 'GI': chunks_GI, 'GS': chunks_GS,
                           'BC': chunks_BC, 'BD': chunks_BD, 'BJD': chunks_BJD,
                           'BJF': chunks_BJF}
            # print(sent, sent_chunks)
            article_result[str(j)] = sent_chunks
        result[str(i)] = article_result

    # clean_useless(result)

    # 写入文件
    with open(path_output, "w", encoding="utf8") as f:
        f.write(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()