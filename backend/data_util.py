# -*- coding:utf-8 -*-
import os
import pandas as pd
import numpy as np
import random
import torch
from torch.utils.data import TensorDataset, DataLoader, random_split
from transformers import BertTokenizer,BertForSequenceClassification,AdamW
from transformers import RobertaTokenizer,RobertaForSequenceClassification
from transformers import get_linear_schedule_with_warmup
from sklearn.metrics import f1_score, accuracy_score

device = torch.device('cuda')
#tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
tokenizer = BertTokenizer.from_pretrained('clue/roberta_chinese_base')

def data_split(file):
    df = pd.read_csv(file).dropna(axis=0)
    # 书籍、平板、手机、水果、洗发水、热水器、蒙牛、衣服、计算机、酒店
    #criteria = (df['cat'] == '平板') | (df['cat'] == '手机') | (df['cat'] == '水果') | (df['cat'] == '计算机') | (
    #            df['cat'] == '酒店')
    #df = df[criteria]
    df = df.sample(frac=1.0)
    cut_idx = int(round(0.1 * df.shape[0]))
    df_test, df_train = df.iloc[:cut_idx], df.iloc[cut_idx:]
    print('df.shape:',df.shape, ' ;test.shape:',df_test.shape, ' train.shape:',df_train.shape)
    df_test.to_csv('test_.csv')
    df_train.to_csv('train_.csv')
    print('Split')

def encode_fn(text_list):
    all_input_ids=[]
    for text in text_list:
        input_ids = tokenizer.encode(text,add_special_tokens=True,max_length=160,pad_to_max_length = True, return_tensors='pt')
        all_input_ids.append(input_ids)
    all_input_ids = torch.cat(all_input_ids, dim=0)
    return all_input_ids

def flat_accuracy(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return accuracy_score(labels_flat, pred_flat)



if __name__ == "__main__":
    #('weibo_senti_100k.csv')

    df=pd.read_csv('train_.csv')

    all_input_ids=encode_fn(df['review'].values)
    labels= torch.tensor(df['label'].values)
    epochs=20
    batch_size=32
    lr=2e-5

    #split data
    dataset = TensorDataset(all_input_ids,labels)
    train_size=int(0.90*len(dataset))
    val_size=len(dataset)-train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    #create dataloader
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle = True)
    val_dataloader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    #load BERT
    #model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=2, output_attentions=False, output_hidden_states=False)
    model = BertForSequenceClassification.from_pretrained('clue/roberta_chinese_base', num_labels=2, output_attentions=False,
                                                          output_hidden_states=False)

    model.cuda()

    #create optimizer and learning rate shedule
    optimizer = AdamW(model.parameters(), lr=lr)
    total_steps = len(train_dataloader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    for epoch in range(epochs):
        model.train()
        total_loss,total_val_loss=0,0
        total_eval_accuracy=0
        for step,batch in enumerate(train_dataloader):
            model.zero_grad()
            output= model(batch[0].to(device), token_type_ids=None, attention_mask=(batch[0]>0).to(device),labels=batch[1].to(device))
            print(output)
            loss,logits=output[0],output[1]
            total_loss+= loss.item()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
            optimizer.step()
            scheduler.step()

        model.eval()
        for i,batch in enumerate(val_dataloader):
            with torch.no_grad():
                output = model(batch[0].to(device), token_type_ids=None, attention_mask=(batch[0]>0).to(device), labels=batch[1].to(device))
                loss=output[0]
                logits=output[1]
                total_val_loss+=loss.item()
                logits = logits.detach().cpu().numpy()
                label_ids = batch[1].to('cpu').numpy()
                total_eval_accuracy += flat_accuracy(logits, label_ids)
        avg_train_loss = total_loss/len(train_dataloader)
        avg_val_loss = total_val_loss/ len(val_dataloader)
        avg_val_accuracy = total_eval_accuracy/ len(val_dataloader)

        print('Train loss  :', avg_train_loss)
        print('Valid loss  :', avg_val_loss)
        print('Accuracy    :', avg_val_accuracy)
        print('\n')
    torch.save(model.state_dict(), './data/' + 'roberta-base-chinese-model.pt')
    print('saved')




