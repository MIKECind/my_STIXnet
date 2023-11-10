import spacy
from settings import preprocess_text, base_entities, kb_path, group_alias
import csv


def update_kb(path, entities: dict):
    if len(entities) == 0:
        return

    with open(path, 'a', encoding='utf-8', newline='') as kb:
        writer = csv.writer(kb)
        for ent_type, ents in entities.items():
            for ent in ents:
                writer.writerow([ent, ent_type])


def extract_novel_entities(text):
    nlp = spacy.load('en_core_web_sm')
    text = preprocess_text(text)
    doc = nlp(text)
    pos_map = {}
    entities = {}
    found_entities = set()
    entity = ''
    entity_type = ''

    for token in doc:
        if token.pos_ == 'PROPN' and token.text not in found_entities:
            if token.dep_ == "nsubj":
                entity = token.text
                entity_head = token.head
                entity_children = token.children
                for child in entity_children:
                    if child.dep_ == 'compound' and child.pos_ == 'PROPN':
                        entity = child.text + ' ' + token.text

                for child in entity_head.children:
                    if child.dep_ == 'attr' and child.pos_ == 'NOUN':
                        if child.text in [alias for alias_list in group_alias.values() for alias in alias_list]:
                            entity_type = [key for key, alias_list in group_alias.items() if child.text in alias_list][
                                0]

                        else:
                            entity_type = child.text
                        print("Entity:", entity)
                        print("Entity Type:", entity_type)

        elif token.text in [alias for alias_list in group_alias.values() for alias in
                            alias_list] and token.dep_ == "nsubj":
            entity_children = token.children

            for child in entity_children:
                if child.dep_ == 'compound' and child.pos_ == 'PROPN' or child.pos_ == 'NOUN':
                    entity = child.text + ' ' + entity
            entity_type = [key for key, alias_list in group_alias.items() if token.text in alias_list][0]

        if entity == '' or  entity_type == '':
            return

        if entity not in base_entities:
            entities.setdefault(entity_type, set()).add(entity)
            pos_map.setdefault(entity_type, {}).setdefault(entity, []).append((token.idx, token.idx + len(entity)))
            found_entities.add(entity)
            print("Entity:", entity)
            print("Entity Type:", entity_type)

        # update_kb(kb_path, entities)

    return entities, pos_map, found_entities


if __name__ == '__main__':
    txt = open('D:/code/python/STIXnet/STIXnet/Dataset/Data/APT3.txt', encoding='utf-8').read()
    entities, pos_map, found_entities = extract_novel_entities(txt)
    print(found_entities)
    print(entities)
    print(pos_map)
