# -*- coding:utf-8 -*-
import os
import pandas as pd
import re
import numpy as np
import random
import torch
from torch.utils.data import TensorDataset, DataLoader, random_split
from transformers import BertTokenizer,BertForSequenceClassification,AdamW
from transformers import RobertaTokenizer,RobertaForSequenceClassification
from transformers import get_linear_schedule_with_warmup
from sklearn.metrics import f1_score, accuracy_score
from transformers import RoFormerForSequenceClassification, RoFormerTokenizer

device = torch.device('cuda')
#tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
#tokenizer = BertTokenizer.from_pretrained('clue/roberta_chinese_base')
tokenizer = RoFormerTokenizer.from_pretrained("junnyu/roformer_chinese_base")

def data_split_weibosenti(file):
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

def data_split_simplifyweibo(file):
    df = pd.read_csv(file).dropna(axis=0)
    # 书籍、平板、手机、水果、洗发水、热水器、蒙牛、衣服、计算机、酒店
    df = df.sample(frac=1.0)
    #criteria = (df['label'] == 1) | (df['label'] == 2) | (df['label'] == 3)
    df0 = df[(df['label'] == 0)]    #pos
    df1 = df[(df['label'] == 1)]  # neg1
    df2 = df[(df['label'] == 2)]    #neg2
    df3 = df[(df['label'] == 3)]    #neg3

    cut_idx0 = int(round(0.1 * df0.shape[0]))
    df_test0, df_train0 = df0.iloc[:cut_idx0], df0.iloc[cut_idx0:]
    cut_idx1 = int(round(0.1 * df1.shape[0]))
    df_test1, df_train1 = df1.iloc[:cut_idx1], df1.iloc[cut_idx1:]
    cut_idx2 = int(round(0.1 * df2.shape[0]))
    df_test2, df_train2 = df2.iloc[:cut_idx2], df2.iloc[cut_idx2:]
    cut_idx3 = int(round(0.1 * df3.shape[0]))
    df_test3, df_train3 = df3.iloc[:cut_idx3], df3.iloc[cut_idx3:]
    print('df0:',df_test0.shape,df_train0.shape,"df1:",df_test1.shape,df_train1.shape,"df2:",df_test2.shape,df_train2.shape,"df3:",df_test3.shape,df_train3.shape)
    df_test=pd.concat([df_test0,df_test1,df_test2,df_test3],axis=0)
    df_train=pd.concat([df_train0,df_train1,df_train2,df_train3],axis=0)
    print('df.shape:',df.shape, ' test.shape:',df_test.shape, ' train.shape:',df_train.shape)
    df_test.to_csv('test_simplifyweibo.csv')
    df_train.to_csv('train_simplifyweibo.csv')
    print('Split')

def encode_fn(text_list):
    all_input_ids=[]
    for text in text_list:
        input_ids = tokenizer.encode(text,add_special_tokens=True,max_length=160,pad_to_max_length = True, return_tensors='pt')
        all_input_ids.append(input_ids)
    all_input_ids = torch.cat(all_input_ids, dim=0)
    print('input_ids_shape:',all_input_ids.shape)
    return all_input_ids

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
        line = re.sub("[\[\]\s+\.\!\/_,$%^*(\"\'；:：“”．]+|[—\-！，。？?、~@#￥%……&*（）]+", "", line)#加入\[\]
        return line
    return None


if __name__ == "__main__":
    #data_split_weibosenti('weibo_senti_100k.csv')
    #data_split_simplifyweibo('simplifyweibo_4_moods.csv')

    df=pd.read_csv('train_simplifyweibo.csv')
    train_review=df['review'].values

    for i in range(train_review.shape[0]):
        train_review[i]=clearTxt(train_review[i])
    print(train_review)


    all_input_ids=encode_fn(train_review)
    labels = df['label'].values
    for i in range(labels.shape[0]):
        if labels[i]!=0:
            labels[i]=1
    labels= torch.tensor(labels)

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
    #model = BertForSequenceClassification.from_pretrained('clue/roberta_chinese_base', num_labels=2, output_attentions=False,output_hidden_states=False)
    model = RoFormerForSequenceClassification.from_pretrained("junnyu/roformer_chinese_base", num_labels=2, output_attentions=False,
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
        for i,batch2 in enumerate(val_dataloader):
            with torch.no_grad():
                output = model(batch2[0].to(device), token_type_ids=None, attention_mask=(batch2[0]>0).to(device), labels=batch2[1].to(device))
                loss=output[0]
                logits=output[1]
                total_val_loss+=loss.item()
                logits = logits.detach().cpu().numpy()
                label_ids = batch2[1].to('cpu').numpy()
                total_eval_accuracy += flat_accuracy(logits, label_ids)
        avg_train_loss = total_loss/len(train_dataloader)
        avg_val_loss = total_val_loss/ len(val_dataloader)
        avg_val_accuracy = total_eval_accuracy/ len(val_dataloader)

        print('Train loss  :', avg_train_loss)
        print('Valid loss  :', avg_val_loss)
        print('Accuracy    :', avg_val_accuracy)
        print('\n')
    torch.save(model.state_dict(), './data/' + 'roformer-chinese-base-simplifyweibo.pt')
    print('saved')




