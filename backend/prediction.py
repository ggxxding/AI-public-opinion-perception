# -*- coding:utf-8 -*-
import os
import pandas as pd
import numpy as np
import random
import torch
from torch.utils.data import TensorDataset, DataLoader, random_split
from transformers import BertTokenizer,BertForSequenceClassification,AdamW
from transformers import RoFormerForSequenceClassification, RoFormerTokenizer
from transformers import get_linear_schedule_with_warmup
from sklearn.metrics import f1_score, accuracy_score
from data_util import encode_fn
import textProcess
device = torch.device('cuda')
#tokenizer = BertTokenizer.from_pretrained('clue/roberta_chinese_base')
tokenizer = RoFormerTokenizer.from_pretrained('junnyu/roformer_chinese_base')

def flat_accuracy(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return accuracy_score(labels_flat, pred_flat)

def predict(path='article.csv'):
    batch_size=32
    df=pd.read_csv(path)

    text = df['text'].values

    for i in range(text.shape[0]):
        text[i]=textProcess.clearTxt(text[i])
    print(text)

    all_input_ids = encode_fn(text)
    print(all_input_ids)
    dataset = TensorDataset(all_input_ids)
    test_dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    '''
    model = BertForSequenceClassification.from_pretrained('clue/roberta_chinese_base', num_labels=2, output_attentions=False,
                                                          output_hidden_states=False)
    model.load_state_dict(torch.load('../experiments/data/roberta-base-chinese-model.pt'))
    '''
    model = RoFormerForSequenceClassification.from_pretrained('junnyu/roformer_chinese_base', num_labels=2, output_attentions=False,
                                                          output_hidden_states=False)
    model.load_state_dict(torch.load('../experiments/data/roformer-chinese-base-simplifyweibo.pt'))

    print('model loaded')
    model.cuda()
    model.eval()

    preds = []
    pred1 = []
    pred2 = []
    for step, batch in enumerate(test_dataloader):
        with torch.no_grad():
            output = model(batch[0].to(device), token_type_ids=None, attention_mask=(batch[0] > 0).to(device))
            print(output)
            logits = output[0]
            print('logits:',logits)
            logits = logits.detach().cpu().numpy()
            preds.append(logits)
    final_preds = np.concatenate(preds, axis=0)
    final_preds = np.argmax(final_preds, axis=1).reshape(-1, 1)
    print(final_preds)
    out = pd.DataFrame(final_preds)
    out = out.astype({0: int})
    print(out)

    sum=0
    for i in final_preds:
        sum+=int(i[0])
    senti=sum/len(final_preds)

    return [{'name':'pos','value':sum},{'name':'neg','value':len(final_preds)-sum}]



if __name__ == "__main__":
    batch_size=32
    df=pd.read_csv('test_.csv')
    all_input_ids = encode_fn(df['text'].values)

    labels = torch.tensor(df['label'].values)

    #split data
    dataset = TensorDataset(all_input_ids,labels)


    #create dataloader
    test_dataloader = DataLoader(dataset, batch_size=batch_size, shuffle = True)

    #load BERT
    model = BertForSequenceClassification.from_pretrained('clue/roberta_chinese_base', num_labels=2, output_attentions=False, output_hidden_states=False)
    model.load_state_dict(torch.load('./data/roberta-base-chinese-model.pt'))
    print('model loaded')
    model.cuda()
    model.eval()
    total_eval_accuracy = 0

    for step, batch in enumerate(test_dataloader):
        with torch.no_grad():
            output = model(batch[0].to(device), token_type_ids=None, attention_mask=(batch[0] > 0).to(device),
                       labels=batch[1].to(device))
            loss, logits = output[0], output[1]
            logits = logits.detach().cpu().numpy()
            label_ids = batch[1].to('cpu').numpy()
            total_eval_accuracy += flat_accuracy(logits, label_ids)
    avg_val_accuracy = total_eval_accuracy / len(test_dataloader)
    print('Accuracy    :', avg_val_accuracy)

