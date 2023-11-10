# import spacy
#
# # 加载英语语言模型
# nlp = spacy.load('en_core_web_sm')
#
# # 定义要进行命名实体识别的文本
# text = "Wizard Spider is a Russia-based financially motivated threat group originally known for the creation and deployment of TrickBot since at least 2016."
#
# # 处理文本
# doc = nlp(text)
#
# # 遍历每个词并提取出新实体和实体类型
# entity = None
# entity_type = None
#
# for token in doc:
#     if token.dep_ == "nsubj":
#         entity = token.text
#         entity_head = token.head
#         for child in entity_head.children:
#             if child.dep_ == 'attr':
#                 entity_type = child.text
#                 print("Entity:", entity)
#                 print("Entity Type:", entity_type)




# import re
#
# # 示例文本
# text = "APT3 has exploited the Adobe Flash Player vulnerability CVE-2015-3113 and Internet Explorer vulnerability CVE-2014-1776."
#
# # 定义正则表达式模式
# pattern = r'((?:[A-Z][a-zA-Z\s]+) vulnerability)'
#
# # 使用正则表达式进行匹配
# matches = re.findall(pattern, text)
#
# # 打印匹配结果
# for match in matches:
#     print(match.strip())

# import spacy
#
#
# def extract_entities(text):
#     nlp = spacy.load('en_core_web_sm')
#     doc = nlp(text)
#     entities = []
#
#     for entity in doc.ents:
#         entities.append((entity.text, entity.label_))
#
#     return entities
#
#
# text = open('D:/code/python/STIXnet/STIXnet/Dataset/Data/ALLANITE.txt').read()
# entities = extract_entities(text)
#
# for entity in entities:
#     print(entity)

# import pandas as pd
#
# # 读取原始的 nationalities.csv 文件
# df = pd.read_csv('../Knowledge-Base/nationalities.csv')
#
# # 去除空值行
# df = df.dropna()
#
# # 重置索引
# df = df.reset_index(drop=True)
#
# # 去除首尾空格
# df['Nationality'] = df['Nationality'].str.strip()
# df['Nation'] = df['Nation'].str.strip()
#
# # 去除非法字符
# df['Nationality'] = df['Nationality'].apply(lambda x: ''.join(filter(str.isalpha, str(x))))
# df['Nation'] = df['Nation'].apply(lambda x: ''.join(filter(str.isalpha, str(x))))
#
# # 将处理后的数据保存到新的文件中
# df.to_csv('cleaned_nationalities.csv', index=False)

# import ahocorasick
# import pandas as pd
#
#
# def find_matched_positions(text, patterns):
#     # 创建Aho-Corasick自动机
#     automaton = ahocorasick.Automaton()
#
#     # 添加模式到自动机
#     for idx, pattern in enumerate(patterns):
#         automaton.add_word(pattern, (idx, pattern))
#
#     # 构建自动机
#     automaton.make_automaton()
#
#     # 搜索匹配并获取位置
#     matched_positions = []
#     for end_index, (insert_order, original_value) in automaton.iter('apple'):
#         start_index = end_index - len(original_value) + 1
#         matched_positions.append((original_value, start_index, end_index))
#
#     return matched_positions
#
# # 输入文本
# text = "This is a sample text containing keywords such as apple, banana, and orange."
#
# # 匹配模式列表
# patterns = ['apple', 'banana', 'orange']
#
# # 寻找匹配位置
# matched_positions = find_matched_positions(text, patterns)
#
# # 打印匹配位置
# for pattern, start_index, end_index in matched_positions:
#     print(f"Pattern: {pattern}, Start Index: {start_index}, End Index: {end_index}")
#     print(text[50:55])
#
# kb_path = '../Knowledge-Base/kb.csv'
# nationalities_path = '../Knowledge-Base/nationalities.csv'
#
# kb = pd.read_csv(kb_path)
# nationalities = pd.read_csv(nationalities_path)
# kb['entity'] = kb['entity'].str.lower()
# nationalities['Nationality'] = nationalities['Nationality'].str.lower()
#
# base_entities = list(kb['entity'])
# base_types = list(kb['type'])
# base_nationalities = list(nationalities['Nationality'])
# base_nations = list(nationalities['Nation'])
# print(base_nations[0])
# print(type(base_types[0]))