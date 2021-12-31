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
device = torch.device('cuda')
if __name__ == "__main__":
    batch_size=1
    df=pd.read_csv('test.txt',header=None)
    all_input_ids = encode_fn(df[0].values)
    #labels = torch.tensor(df['label'].values)

    #split data
    dataset = TensorDataset(all_input_ids)


    #create dataloader
    test_dataloader = DataLoader(dataset, batch_size=batch_size, shuffle = False)

    #load BERT
    model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=2, output_attentions=False, output_hidden_states=False)
    model.load_state_dict(torch.load('./data/bert-base-chinese-model.pt'))
    print('model loaded')
    model.cuda()
    model.eval()
    preds=[]
    pred1=[]
    pred2=[]
    for step, batch in enumerate(test_dataloader):
        with torch.no_grad():
            output = model(batch[0].to(device), token_type_ids=None, attention_mask=(batch[0] > 0).to(device))
            logits = output[0]
            pred1.append(logits[0][0].cpu())
            pred2.append(logits[0][1].cpu())
            logits = logits.detach().cpu().numpy()
            preds.append(logits)
    final_preds=np.concatenate(preds, axis=0)
    final_preds=np.argmax(final_preds,axis=1).reshape(-1,1)
    pred1=np.array(pred1).reshape(-1,1)
    pred2=np.array(pred2).reshape(-1,1)
    out = np.concatenate([final_preds,pred1,pred2],axis=1)
    out=pd.DataFrame(out)
    out=out.astype({0:int})
    print(out)
    out.to_csv('output.txt',sep=' ',header=None,index=False)