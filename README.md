# chunks_extract

## 数据

- 数据保存在`data`文件夹下

## 数据预处理

```
python data_preprocess_01.py
```

- 分句结果保存在`data_preprocessed/ssplit`文件夹下
- 分词结果保存在`data_preprocessed/segmentation`文件夹下
- 词性标注结果保存在`data_preprocessed/tokenized`文件夹下

## 提取自由搭配结构

```
# 分词
python data_preprocess_01.py --corpus_path=../data_preprocessed/ssplit/toy_ssplit.txt --output_path=../data_preprocessed/chunks_P/toy/toy_01.txt --batch_size=1

# 句法分析
python text_parse_02.py --tokenized_file=../data_preprocessed/ssplit/toy_ssplit.txt --parsed_output=../data_preprocessed/chunks_P/toy/toy_02.txt --batch_size=1

# 提取自由搭配结构
python collocate_extract_03.py --parsed_file=../data_preprocessed/chunks_P/toy/toy_02.txt --pattern_file=pattern.txt --output_file=../data_preprocessed/chunks_P/toy/toy.json
```

- 自由搭配保存在`data_preprocessed/chunks_P/toy`文件夹下

## 提取其他语块

```
# 提取语块保存在json格式中
python chunk_extract_02.py
```

- 结果保存在`result/chunks.json`

## 结果输出

```
# 将语块在句子中标记出来
python chunk_label_03.py
```

- 结果表示形式

![](.\img\result_1.png)

****

```
# 将所有语块按句子顺序直接输出
python result_extract_label_04.py
```

![](.\img\result_3.png)

- 结果表示形式

![](.\img\result_2.png)