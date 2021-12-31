# -*- coding:utf-8 -*-
import os
import pandas as pd
import numpy as np
import random
import torch
from torch.utils.data import TensorDataset, DataLoader, random_split
from transformers import BertTokenizer,BertForSequenceClassification,AdamW
from transformers import get_linear_schedule_with_warmup
from sklearn.metrics import f1_score, accuracy_score
from data_util import encode_fn
import re
device = torch.device('cuda')

def flat_accuracy(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return accuracy_score(labels_flat, pred_flat)

# 清洗文本
def clearTxt(line:str):
    if(line != ''):
        line = line.strip()
        # 去除文本中的英文和数字
        line = re.sub("[a-zA-Z0-9]", "", line)
        # 去除文本中的中文符号和英文符号
        line = re.sub("[\[\]\s+\.\!\/_,$%^*(+\"\'；：“”．]+|[+——！，。？?、~@#￥%……&*（）]+", "", line)#add \[\]
        return line
    return None

if __name__ == "__main__":
    batch_size=32
    df=pd.read_csv('test_.csv')

    test_review = df['review'].values

    for i in range(test_review.shape[0]):
        test_review[i] = clearTxt(test_review[i])
    print(test_review)

    all_input_ids = encode_fn(test_review)
    labels = torch.tensor(df['label'].values)

    #split data
    dataset = TensorDataset(all_input_ids,labels)


    #create dataloader
    test_dataloader = DataLoader(dataset, batch_size=batch_size, shuffle = False)

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
            print(logits)
            print(label_ids)

            total_eval_accuracy += flat_accuracy(logits, label_ids)
    avg_val_accuracy = total_eval_accuracy / len(test_dataloader)
    print('Accuracy    :', avg_val_accuracy)

