import os

import nltk
from nltk.tokenize import MWETokenizer, TreebankWordTokenizer
from nltk.tag import pos_tag
from ahocorasick import Automaton

from settings import preprocess_text, base_types, base_entities, base_nations, base_nationalities, types_pos
from novel_entity_finder import extract_novel_entities

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

assert len(base_types) == len(base_entities)
assert len(base_nations) == len(base_nationalities)

tokenizer = TreebankWordTokenizer()

# 词汇表补充
voc = []
for entity in base_entities:
    if ' ' in entity:
        voc.append(tuple(entity.split()))

mwe_tokenizer = MWETokenizer(voc, separator=' ')

# Aho-Corasick algorithm
automaton = Automaton()
for i in range(len(base_entities)):
    automaton.add_word(base_entities[i], (base_types[i], base_entities[i]))
for i in range(len(base_nations)):
    automaton.add_word(base_nationalities[i], ('location', base_nationalities[i]))
for i in range(len(base_nations)):
    automaton.add_word(base_nations[i], ('location', base_nations[i]))
automaton.make_automaton()


def _find_tag(target_word, tagged_words):
    for (word, tag) in tagged_words:
        if word == target_word:
            return tag


"""直接调用这个方法即可"""
def extract_entities(text):
    extract_novel_entities(text)
    pos_map = {}        # 提取出的实体及其位置
    entities = {}       # 提取出的实体
    found_entities = set() # 提取出的实体
    processed_text = preprocess_text(text)
    sentences = nltk.sent_tokenize(processed_text)

    for sentence in sentences:
        words = tokenizer.tokenize(sentence)
        words = mwe_tokenizer.tokenize(words)
        tagged_words = pos_tag(words)

        for end_index, (TYPE, entity) in automaton.iter(processed_text):
            start_index = end_index - len(entity) + 1
            pos = _find_tag(entity, tagged_words)
            target_pos = types_pos.get(TYPE)

            if pos is None or target_pos is None:
                continue

            if pos in target_pos:
                if TYPE not in pos_map:
                    pos_map[TYPE] = {}
                if entity not in pos_map[TYPE]:
                    pos_map[TYPE][entity] = []
                pos_map[TYPE][entity].append([start_index, end_index])

                if entities.get(TYPE) is None:
                    entities[TYPE] = [entity]
                    found_entities.add(entity)
                else:
                    entities.get(TYPE).append(entity)
                    found_entities.add(entity)

    return entities, pos_map, found_entities


if __name__ == '__main__':
    directory = 'D:/code/python/STIXnet/STIXnet/Dataset/Data/'
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
            entities, pos_map, found_entities = extract_entities(text)
            with open('try/entity_finder/' + filename, 'w') as fp:
                fp.write(str(entities) + '\n')
                fp.write(str(pos_map))
