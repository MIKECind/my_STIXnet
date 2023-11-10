import re

import pandas as pd

# 导入knowledge base
kb_path = '../Knowledge-Base/instance_kb.csv'
nationalities_path = '../Knowledge-Base/cleaned_nationalities.csv'

kb = pd.read_csv(kb_path)
nationalities = pd.read_csv(nationalities_path, dtype=str, encoding='utf-8')
kb['entity'] = kb['entity'].str.lower()
nationalities['Nationality'] = nationalities['Nationality'].str.lower()

base_entities = list(kb['entity'])
base_types = list(kb['type'])
base_nationalities = list(nationalities['Nationality'])
base_nations = list(nationalities['Nation'])

"""需要补充其他实体类型及其别名"""
group_alias = {'intrusion set': ['group', 'intrusion set'], 'malware': ['malware', 'software']}

"""需要补充其他实体类型及其POS标签(nltk的标签)"""
types_pos = {
    'intrusion-set': ['JJ', 'VB', 'RB', 'NN', 'NNS'], 'location': ['JJ', 'VB', 'PRP', 'NN', 'FW', 'NNS'], 'identity': ['JJ', 'VBG', 'WP', 'NN', 'NNS'],
    'tool': ['JJ', 'VB', 'RB', 'VBG', 'NN', 'NNS'], 'attack-pattern': ['JJ', 'RP', 'VB', 'RB', 'VBZ', 'VBG', 'NNS', 'NN', 'VBP'],
    'malware': ['JJ', 'RP', 'VB', 'RB', 'NN', 'NNS'], 'indicator': ['NN', 'JJ'], 'campaign': ['NN'], 'threat-actor': ['NN', 'JJ', 'RB', 'VB'],
    'tactic': ['NN', 'VBG']
}

# 文本预处理
file_path_pattern = r'[A-Za-z]:\\(?:[\w]+\\)*\w+\.\w+'
file_path_replace = 'filepath'
vulnerability_pattern = r'((?:[A-Z][a-zA-Z\s]+) vulnerability)'
vulnerability_replace = 'V'


def preprocess_text(text):
    text = re.sub(pattern=file_path_pattern, repl=file_path_replace, string=text)
    text = re.sub(pattern=vulnerability_pattern, repl=vulnerability_replace, string=text)
    processed_text = text.lower()
    return processed_text
