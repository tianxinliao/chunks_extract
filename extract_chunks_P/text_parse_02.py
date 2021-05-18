# -*- coding:UTF-8 -*-
import os, sys
import argparse
import stanza
from ConlluProcessor import ConlluWriter
from pyhanlp import HanLP
from collections import OrderedDict

# 'processors': 'tokenize, lemma, pos, depparse',  # Comma-separated list of processors to use
# 'lang': 'zh',  # Language code for the language to build the Pipeline in
# 'dir': "/Users/fang/stanza_resources",
# 'tokenize_pretokenized': True,  # Use pre_tokenized text as input and disable tokenization
# 'no_ssplit': True


def read_doc(filename):  
    with open(filename, "r", encoding="utf8") as fr:
        line_exist = True
        while line_exist:
            line = fr.readline()
            if not line:
                line_exist = False
                line = "$$<EOD>$$"
            else:
                if line == "\n":
                    continue
                line = line.strip()
                line = line.split(" ")
            yield line


def get_attrs(parse_result):
    sent_attrs = []
    for word in parse_result:
        attrs = OrderedDict()
        attrs["id"] = str(int(word.id) - 1)
        attrs["text"] = word.text
        attrs["upos"] = word.upos
        attrs["govern"] = str(int(word.head) - 1)
        attrs["relate"] = word.deprel
        sent_attrs.append(attrs)
    return sent_attrs

def write2conllu(text_content):
    text_batch = []
    sent_ids = []
    fw = open(args.parsed_output, "w", encoding="utf8")
    for sent_idx, sent_content in enumerate(text_content):
        if sent_idx % int(args.batch_size) != 1 and sent_content != "$$<EOD>$$":
            sent_ids.append(sent_idx)
            text_batch.append(sent_content)
        else:
            if sent_content != "$$<EOD>$$":
                sent_ids.append(sent_idx)
                text_batch.append(sent_content)
            print(sent_idx)
            processed_sents = nlp(text_batch)
            for idx, processed_sent in enumerate(processed_sents.sentences):
                parse_result = processed_sent.words
                sent_id = str(sent_ids[idx])
                sent_text = processed_sent.text
                sent_attrs = get_attrs(parse_result)
                sent_writer = ConlluWriter(sent_id, sent_text, sent_attrs)
                sent_writer.format_output()
                sent_writer.write_file(fw)
            sent_ids = []
            text_batch = []
    fw.close()

if __name__ == "__main__":
    parser =argparse.ArgumentParser()
    parser.add_argument("--tokenized_file",help="pretokenized corpus filepath")
    parser.add_argument("--parsed_output", help="output parsed file")
    parser.add_argument("--batch_size", help="batch size for parsing")
    args = parser.parse_args()
    stanza.download("zh")
    nlp = stanza.Pipeline('zh',use_gpu=True,processors='tokenize,lemma,pos,depparse',tokenize_no_ssplit=True,tokenize_pretokenized=True)
    text_content = read_doc(args.tokenized_file)
    write2conllu(text_content)
    
    
