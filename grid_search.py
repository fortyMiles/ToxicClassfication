import fasttext
from itertools import product
import config
import os
from preprocessing_training_corpus import get_train_dev_corpus_file_name
from preprocessing_training_corpus import labels


def train(label, model, dim, lr, windows, epoch, record, thread):
    w2v_model_name = '{}/w2v/w2v-{}-{}-{}-{}-{}'.format(config.root, model, dim, lr, windows, epoch)
    if model == 'skip':
        func = fasttext.skipgram
    elif model == 'cbow':
        func = fasttext.cbow

    if not os.path.exists(w2v_model_name + '.vec'):
        print('training embedding')
        func(config.line_corpus,
             w2v_model_name,
             dim=dim, lr=lr, ws=windows, epoch=epoch, thread=thread)

    w2v_model_path = w2v_model_name + '.vec'
    clf_path = '{}/clf/{}-{}-{}-{}-{}_model'.format(config.root, model, dim, lr, windows, epoch)

    train_file, dev_file = get_train_dev_corpus_file_name(label=label)

    if not os.path.exists(clf_path + '.bin'):
        classifier = fasttext.supervised(
            train_file,
            clf_path,
            dim=dim,
            pretrained_vectors=w2v_model_path,
            thread=threads
        )
    else:
        classifier = fasttext.load_model(clf_path + '.bin')

    print('WHEN LABEL = {} DIM = {}, LR = {}, windows = {}, epoch = {}, model = {}'.format(label, dim, lr, windows, epoch, model))
    result = classifier.test(dev_file)
    print(" PRECISION: {}, RECALL: {}".format(result.precision, result.recall))

    with open(record, 'a') as f:
        f.write('{}-{}-{}-{}-{}-{}-precision-{}-recall-{}\n'.format(label, model, dim, lr, windows, epoch, result.precision, result.recall))


if __name__ == '__main__':
    models = ['cbow', 'skip']
    dimensons = [20, 50, 100, 200]
    learning_rates = [1e-3, 1e-2]
    ws = [5, 7, 9]
    epochs = [5, 10, 15]
    threads = 50

    for label in labels:
        record = '{}_train_recoding.txt'.format(label)
        for m, d, l, w, e in product(models, dimensons, learning_rates, ws, epochs):
            train(label=label, model=m, dim=d, lr=l, windows=w, epoch=e, record=record, thread=threads)
