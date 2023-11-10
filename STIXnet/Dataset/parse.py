import json


def find_apt3_file_upload_objects(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        annotations = json.load(file)
        apt3_objects = None

        for annotation in annotations:
            file_upload = str(annotation['file_upload'])
            if file_upload.endswith('APT3.txt'):
                apt3_objects = annotation
                break

        return apt3_objects


def find_all_labels(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        STIXs = json.load(file)
        labels = set()

        for STIX in STIXs:
            for annotation in STIX['annotations']:
                for result in annotation['result']:
                    try:
                        value = result['value']
                        label = value['labels']
                        label = label[0]
                        labels.add(label)
                    except:
                        break

    return labels

# 调用示例
# file_path = 'Annotations.json'
# apt3_file_uploads = find_apt3_file_upload_objects(file_path)
# with open('APT3.json', 'w') as f:
#     json.dump(apt3_file_uploads, f)

file_path = 'Annotations.json'
labels = find_all_labels(file_path)
for label in labels:
    open('labels.txt', 'a').write(label+'\n')
