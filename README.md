# chunks_extract

## 数据预处理

```
python data_preprocess_01.py
```

## 提取自由搭配结构

```
# 分词
python data_preprocess_01.py --corpus_path=../data_preprocessed/ssplit/toy_ssplit.txt --output_path=../data_preprocessed/chunks_P/toy/toy_01.txt --batch_size=1

# 句法分析
python text_parse_02.py --tokenized_file=../data_preprocessed/ssplit/toy_ssplit.txt --parsed_output=../data_preprocessed/chunks_P/toy/toy_02.txt --batch_size=1

# 提取自由搭配结构
python collocate_extract_03.py --parsed_file=../data_preprocessed/chunks_P/toy/toy_02.txt --pattern_file=pattern.txt --output_file=../data_preprocessed/chunks_P/toy/toy.json
```

## 提取其他语块

```

```

