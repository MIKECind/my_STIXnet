import csv
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag


def preprocess_text(text):
    processed_text = text.lower()
    return processed_text


IOCs = ['vulnerability', 'url', 'sha256s', 'domain-name', 'file_paths']
TTPs = ['tactic', 'attack-pattern', 'campaign']
pos = {}
annotations = json.load(open('../../Dataset/Annotations.json', 'r', encoding='utf-8'))

for instance in annotations:
    results = instance['annotations'][0]['result']
    labels = {}
    txt = instance['data']['text']
    for obj in results:
        try:
            if obj['type'] == 'labels':
                if obj['value']['labels'][0] not in IOCs:
                    #  and obj['value']['labels'][0] not in TTPs
                    labels.setdefault(obj['value']['labels'][0], set()).add(obj['value']['text'])
        except:
            continue

    print(labels)

    processed_text = preprocess_text(txt)
    sentences = nltk.sent_tokenize(processed_text)
    keys = list(labels.keys())

    for sentence in sentences:
        words = word_tokenize(sentence)
        pos_tags = pos_tag(words)

        for key in keys:
            entities = labels.get(key)
            for i in range(len(words)):
                for entity in entities:
                    if words[i] == entity.lower():
                        pos.setdefault(key, set()).add(pos_tags[i][1])

    with open('../Knowledge-Base/instance_kb.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        for key in keys:
            for entity in labels.get(key):
                writer.writerow([entity, key])

print(pos)
