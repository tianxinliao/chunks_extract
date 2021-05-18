# import stanza
# import jieba
import hanlp
# from pyhanlp import HanLP
import os, sys
import re
import argparse
import time
# nlp = stanza.Pipeline("zh",use_gpu=False, processors="tokenize", tokenize_no_ssplit=True)
def read_doc(filename):  
    with open(filename, "r", encoding="utf8") as fr:
        line_exist = True
        while line_exist:
            line = fr.readline()
            if not line:
                line_exist = False
                line = "$$<EOD>$$"
            else:
                line = line.strip()
                # line = HanLP.convertToSimplifiedChinese(line)
                line = line.replace(" ", "")
            yield line

if __name__ == "__main__":
    start = time.time()
    hanlp_tokenizer = hanlp.load('SIGHAN2005_PKU_CONVSEG')
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus_path", help="input corpus file to precess")
    parser.add_argument("--output_path", help="output filename")
    parser.add_argument("--batch_size", help="batch size for tokenization")
    args = parser.parse_args()
    # nlp = stanza.Pipeline("zh",use_gpu=False, processors="tokenize", tokenize_no_ssplit=True)
    fw = open(args.output_path,"w", encoding="utf8")  
    sent_idx = 0
    text_batch = []
    for sent in read_doc(args.corpus_path):
        if sent_idx % int(args.batch_size) != 1 and sent != "$$<EOD>$$":
            text_batch.append(sent)
        else:
            if sent != "$$<EOD>$$":
                text_batch.append(sent)
            for processed_sent in hanlp_tokenizer(text_batch):
                fw.write(" ".join(processed_sent)+"\n")
            text_batch = []
        sent_idx += 1
        # fw.write(" ".join(list(jieba.cut(sent)))+"\n")
        # processed_sent = nlp(sent)
        # tokenized_sent = [word["text"] for word in processed_sent.to_dict()[0]]
        # fw.write(" ".join(tokenized_sent)+"\n")
    fw.close()
    end = time.time()
    print("Total cost: %.4f s" %(end-start))


