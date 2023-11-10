from training import predict_new, NAME_TACTICS, NAME_TECHNIQUES


def pred_tactics(text, post_processing_parameters='HN'):
    pred_tactics_new, predprob_tactics_new, pred_techniques_new, predprob_techniques_new = predict_new(text,
                                                                                                       post_processing_parameters)
    tactics = {'tactic': [], 'technique': []}

    for i, tact in enumerate(pred_tactics_new[0]):
        if tact == 1:
            tactic = NAME_TACTICS[tact]
            tactics['tactic'] = tactic

    for i, tact in enumerate(pred_techniques_new[0]):
        if tact == 1:
            technique = NAME_TECHNIQUES[tact]
            tactics['technique'] = technique

    return tactics

if __name__ == '__main__':
    text = open('../../Dataset/Data/APT3.txt', 'r', encoding='utf-8').read()
    tactics = pred_tactics(text, 'HN')
    print(tactics)