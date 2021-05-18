import json
import re
from copy import deepcopy
import os


def load_data(path):
    sents = []
    with open(path, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        sent = {}
        sent["Sent_ID"] = i
        sent["Text"] = line.strip()
        sent["length"] = len(line.strip())
        sent["chunks_num"] = 0
        sent["chunks"] = []
        sents.append(sent)
    return sents


def process(path):
    ret = []
    with open(path, "r") as f:
        lines = f.readlines()
    for line in lines:
        s = []
        words = line.strip().split()
        for word in words:
            s.append(word.split("_")[0])
        ret.append(s)
    return ret


def main():

    # 读入保存语块信息的json文件
    with open('./result/chunks.json', 'r', encoding='utf8')as fp:
        json_data = json.load(fp)

    # 待标注的语料
    input_path = "./data_preprocessed/"
    # 输出结果保存路径
    output_path = "./result/complete_format/"

    files_ssplit = os.listdir(input_path + "ssplit/")
    files_ssplit.sort()
    for i, file in enumerate(files_ssplit):
        file_name = file.split("_")[0]
        sents = load_data(input_path + "ssplit/" + file)
        sents_tokenized = process(input_path + "tokenized/" + file_name + "_tokenized.txt")
        file_sents_out = output_path + file_name + "_result.txt"
        item = str(i)
        # 每个sent是一个句子
        for id, sent in json_data[item].items():
            chunk_num = 0
            # 每个chunks是一类标签的所有语块（list）
            for label, chunks in sent.items():
                chunk_num += len(chunks)
                for chunk in chunks:
                    if label == "GC" or label == "GI" or label == "GS":
                        position = chunk[0]['position']
                        s = sents[int(id)]['Text']
                        s = list(s)
                        s.insert(position[0], "^[")
                        s.insert(position[1] + 1, ' ' + label + ']^')
                        s = ''.join(s)
                        sents[int(id)]["chunks"].append(s)
                    else:
                        s = deepcopy(sents_tokenized[int(id)])
                        for part in chunk:
                            s[part["id"]] = "^[" + s[part["id"]] + " " + label + "]^"
                        s = ''.join(s)
                        sents[int(id)]["chunks"].append(s)
            sents[int(id)]["chunks_num"] = chunk_num

        # 导入自由搭配结构P
        with open(input_path + "chunks_P/" + file_name + "/" + file_name + "_02.txt", 'r', encoding='utf8') as f:
            a = {}
            for line in f:
                if line.startswith('# sent_id'):
                    sent_text = ''
                    sent_id = re.search("\d+", line).group()
                elif line.startswith('# text'):
                    s = line.split("=")[1].strip()
                    sent_text = s.split()
                elif line == "\n":
                    a[sent_id] = sent_text

        with open(input_path + "chunks_P/" + file_name + "/" + file_name + ".json", 'r', encoding='utf8') as fp:
            json_data_P = json.load(fp)

        # every item is a sentence(dic)
        for item in json_data_P:
            # every key is a kind of chunk(list) like "定中"
            for key in json_data_P[item].keys():
                if key == "定中" or key == "量名" or key == "介方":
                    tag = "MP"
                else:
                    tag = "WP"
                sents[int(item)]["chunks_num"] += len(json_data_P[item][key])
                # every chunk is a list including several parts(dict with id and text as keys)
                for chunk in json_data_P[item][key]:
                    f = True
                    s = ''
                    t_sent = deepcopy(a[item])
                    for part in chunk:
                        if part["text"] == "嘛" or part["text"] == "呢":
                            f = False
                        else:
                            t_sent[int(part["id"])] = "^[" + part["text"] + " " + tag + "]^"
                    for w in t_sent:
                        s += w
                    if f:
                        sents[int(item)]["chunks"].append(s)

        # 将结果写入文件
        with open(file_sents_out, "w") as f:
            for sent in sents:
                for k, v in sent.items():
                    if k != "chunks":
                        f.write("# " + k + " = " + str(v) + "\n")
                    else:
                        f.write("# " + k + "\n")
                        for s in v:
                            f.write(s + "\n")
                f.write("\n")


if __name__ == "__main__":
    main()
