# -*- coding: UTF-8 -*-
# dependencies: zhon, xml
import xml.etree.ElementTree as ET
import os, sys
from zhon import hanzi
import string
import re
from collections import OrderedDict
import json
import time
import argparse
from ConlluProcessor import Word, Sent

def adv_collocate(sent):
    collocates = []
    for word in sent:
        if word.attrib["upos"] in ["ADJ", "ADV"] and word.attrib["relate"] == "advmod":
            collocates.append([word.attrib])
    if collocates:
        for collocate in collocates:
            rely_id = int(collocate[0]["govern"])
            rely_word = sent[rely_id].attrib
            for word in sent[int(collocate[0]["id"])+1:]:
                if word.attrib["relate"] in ["cop", "ccomp"] and int(word.attrib["govern"]) == rely_id:
                    if word.attrib["text"] in ["为", "是", "非"]:
                        rely_id = word.attrib["id"]
                        rely_word == word.attrib
            if rely_word["upos"] in ["VERB", "ADJ", "DET"]:
                if "被" not in rely_word["text"] and "一点" not in rely_word["text"]:
                    collocate.append(rely_word)
                if rely_id == int(collocate[0]["id"]) + 2 and sent[rely_id-1].attrib["text"] == "地":
                    collocate.insert(1, sent[rely_id-1].attrib)
    return collocates

def obj_collocate(sent):
    collocates = []
    indirect_objs = []
    for word in sent:
        if word.attrib["relate"] == "obj":
            collocates.append([word.attrib])
        elif word.attrib["relate"] == "iobj":
                indirect_objs.append(word.attrib)
    if collocates:
        for collocate in collocates:
            rely_id = int(collocate[0]["govern"])
            rely_word = sent[rely_id].attrib
            if "被" not in rely_word["text"]:
                collocate.insert(0, rely_word)
            if len(collocate) == 2:
                for iobj_word in indirect_objs:
                    if int(iobj_word["govern"]) == rely_id:
                        if int(iobj_word["id"]) < int(collocate[1]["id"]):
                            collocate.insert(1, iobj_word)
                        else:
                            collocate.append(iobj_word)
    return collocates


def sub_collocate(sent):
    collocates = []
    for word in sent:
        if word.attrib["relate"] == "nsubj":
            collocates.append([word.attrib])
    if collocates:
        for collocate in collocates:
            rely_id = int(collocate[0]["govern"])
            rely_word = sent[rely_id].attrib
            if rely_word["upos"] in ["VERB", "ADJ", "NOUN"]:
                collocate.append(rely_word)
    return collocates

def adj_collocate(sent):
    collocates = []
    for word in sent:
        if word.attrib["relate"] in ["amod", "nmod"]:
            collocates.append([word.attrib])
    if collocates:
        for collocate in collocates:
            rely_id = int(collocate[0]["govern"])
            rely_word = sent[rely_id].attrib
            de_exist = False
            if sent[rely_id - 1].attrib["text"] == "的" and sent[rely_id - 1].attrib["govern"] == collocate[0]["id"]:
                de_word = sent[rely_id - 1].attrib
                de_exist = True
            if collocate[0]["relate"] == "amod":
                if de_exist and de_word["relate"] == "mark:relcl":
                    collocate.append(de_word)
                collocate.append(rely_word)
            elif collocate[0]["relate"] == "nmod":
                if de_exist and de_word["relate"] == "case:dec":
                    collocate.append(de_word)
                collocate.append(rely_word)
    return collocates


def clf_collocate(sent):
    collocates = []
    for word in sent:
        if word.attrib["relate"] in ["clf", "nummod"]:
            collocates.append([word.attrib])
    if collocates:
        for collocate in collocates: 
            rely_id = int(collocate[0]["govern"])
            rely_word = sent[rely_id].attrib
            if collocate[0]["relate"] == "clf":
                collocate.append(rely_word)
            elif collocate[0]["relate"] == "nummod":
                for word in sent[rely_id:]:
                    if word.attrib["text"] == "的" and int(word.attrib["govern"]) == rely_id and word.attrib["relate"] == "case":
                        head_noun = sent[int(rely_word["govern"])].attrib
                        collocate[0] = rely_word
                        collocate.append(head_noun)
                        break
    return collocates

def loc_collocate(sent):
    collocates = []
    for word in sent:
        if word.attrib["relate"] == "case" and sent[int(word.attrib["govern"])].attrib["relate"] == "obl":
            collocates.append([word.attrib])
    if collocates:
        for collocate in collocates: 
            rely_id = int(collocate[0]["govern"])
            rely_word = sent[rely_id].attrib
            if len(sent) > rely_id + 1:
                if int(sent[rely_id + 1].attrib["govern"]) == rely_id and sent[rely_id + 1].attrib["relate"] == "acl":
                    loc_case = sent[rely_id + 1].attrib
                    collocate.append(rely_word)
                    collocate.append(loc_case)
    return collocates

def prep_collocate(sent):
    collocates = []
    for word in sent:
        if word.attrib["relate"] == "obl:patient":
            collocates.append([word.attrib])
    if collocates:
        for collocate in collocates:
            rely_id = int(collocate[0]["govern"])
            rely_word = sent[rely_id].attrib
            for word in sent[rely_id:int(collocate[0]["id"])]:
                if word.attrib["relate"] == "case" and word.attrib["govern"] == collocate[0]["id"]:
                    collocate.insert(0, word.attrib)
                    collocate.append(rely_word)
    return collocates



def read_related_pattern(pattern_file):
    patterns = []
    with open(pattern_file, "r", encoding="utf8") as fr:
        for line in fr:
            line = line.strip()
            if line and line != "\n" and not line.startswith("#"):
                pattern = line.split(" ")
                for idx, i in enumerate(pattern):
                    pattern[idx] = set(i.split("/"))
                patterns.append(pattern)
    return patterns

def related_collocate(sent):
    related_patterns = read_related_pattern(args.pattern_file)
    collocates = []
    collocates = []
    for word in sent:
        for pattern in related_patterns:
            collocate = []
            if word.attrib["text"] in pattern[0]:
                for word2 in sent[int(word.attrib["id"])+1:]:
                    if word2.attrib["text"] in pattern[1]:
                        collocate = [word.attrib, word2.attrib]
                        break
            if len(pattern) == 3 and collocate:
                for word3 in sent[int(word2.attrib["id"])+1:]:
                    if word3.attrib["text"] in pattern[2]:
                        collocate.append(word3.attrib)
                        break
            if len(collocate) == len(pattern):
                collocates.append(collocate)
    return collocates


def comp_collocate(sent):
    collocates = []
    for word in sent:
        if word.attrib["relate"] in ["mark", "mark:comp", "nummod"]:
            collocates.append([word.attrib])
    if collocates:
        for collocate in collocates:
            rely_id = int(collocate[0]["govern"])
            rely_word = sent[rely_id].attrib
            if collocate[0]["relate"] == "mark":
                if rely_word["upos"] == "VERB" and rely_id < int(collocate[0]["id"]):
                    if rely_word["text"] not in ["在", '时']:
                        collocate.insert(0, rely_word)
                        for word in sent[rely_id:int(collocate[1]["id"])]:
                            if word.attrib["relate"] == "advmod" and word.attrib["upos"] == "ADV" and word.attrib["text"] == "不":
                                collocate.insert(1, word.attrib)
            elif collocate[0]["relate"] == "mark:comp":
                if collocate[0]["text"] == "得":
                    de_id = int(collocate[0]["id"])
                    if sent[de_id-1].attrib["upos"] == "AUX" and sent[de_id-1].attrib["relate"] == "cop":
                        collocate.insert(0, sent[de_id-1].attrib)
                        collocate.append(rely_word)
            # elif collocate[0]["relate"] == "nummod": 
    return collocates

# post process

def print_result(collocates):
    if collocates:
        for collocate in collocates:
            if len(collocate) > 1:
                for i in collocate:
                    print(i["text"], end=" ")
                print("\n")


def word_check(input_str):
    punct_set = set()
    punct_set.add(hanzi.punctuation + string.punctuation)
    punct_set = "".join(punct_set)
    if re.search(f"[{punct_set}A-Za-z]", input_str):
        return True
    else:
        return False

def clean_useless(collocates):
    useless_ids = set()
    for idx, collocate in enumerate(collocates):
        if len(collocate) < 2:
            useless_ids.add(idx)
        else:
            for item_id,item in enumerate(collocate):
                collocate[item_id] = {"id": item["id"], "text": item["text"]}
                if word_check(item["text"]):
                    useless_ids.add(idx)
    counter = 0
    for i in useless_ids:
        del collocates[i-counter]
        counter += 1
    return collocates

def write2json():
    result_collocates = {}
    with open(args.parsed_file, "r", encoding="utf8") as fr:
        for line in fr:
            if line.startswith("# sent_id"):
                sent_text = ""
                sent_idx = int(re.search("\d+", line).group())
            elif line != "\n" and not line.startswith("# sent_id"):
                sent_text += line
            elif line == "\n":
                sent = Sent(sent_text)
                adv_collocates = adv_collocate(sent)
                obj_collocates = obj_collocate(sent)
                sub_collocates = sub_collocate(sent)
                adj_collocates = adj_collocate(sent)
                clf_collocates = clf_collocate(sent)
                loc_collocates = loc_collocate(sent)
                # related_collocates = related_collocate(sent)
                # prep_collocates = prep_collocate(sent)
                comp_collocates = comp_collocate(sent)
                sent_collocates = {
                    "状中": adv_collocates, "动宾": obj_collocates, "主谓": sub_collocates,
                    "定中": adj_collocates, "量名": clf_collocates, "介方": loc_collocates,
                    "动补": comp_collocates
                }
                for key, collocates in sent_collocates.items():
                    if collocates:
                        processed_collocates = clean_useless(collocates)
                        if processed_collocates:
                            if sent_idx not in result_collocates:
                                result_collocates[sent_idx] = {}
                            result_collocates[sent_idx][key] = processed_collocates
                if sent_idx % 100 == 0:
                    print(f"{sent_idx+1} lines have been processed.")
    with open(args.output_file, "w", encoding="utf8") as fw:
        fw.write(json.dumps(result_collocates, ensure_ascii=False, sort_keys=True, separators=(',', ':')))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--parsed_file", help="parsed corpus file by stnaza")
    parser.add_argument("--pattern_file", help="pattern file for collocation")
    parser.add_argument("--output_file", help="output json file")
    args = parser.parse_args()
    start = time.time()
    write2json()
    end = time.time()
    print("Total cost %.2f s" %(end - start))
