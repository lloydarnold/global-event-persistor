from matplotlib.pyplot import title
import numpy as np
import torch
import torch.nn as nn
from transformers import AutoModel, BertTokenizerFast
from pycaret.classification import * 
from newspaper import Article

class BERT_Arch(nn.Module):

    def __init__(self, bert):
      
      super(BERT_Arch, self).__init__()

      self.bert = bert 
      
      # dropout layer
      self.dropout = nn.Dropout(0.1)
      
      # relu activation function
      self.relu =  nn.ReLU()

      # dense layer 1
      self.fc1 = nn.Linear(768,512)
      
      # dense layer 2 (Output layer)
      self.fc2 = nn.Linear(512,2)

      #softmax activation function
      self.softmax = nn.LogSoftmax(dim=1)

    #define the forward pass
    def forward(self, sent_id, mask):

      #pass the inputs to the model  
      cls_hs = self.bert(sent_id, attention_mask=mask)['pooler_output']
      x = self.fc1(cls_hs)

      x = self.relu(x)

      x = self.dropout(x)

      # output layer
      x = self.fc2(x)
      
      # apply softmax activation
      x = self.softmax(x)

      return x

def news_classification(entries):
  
  title_list = []
  for entry in entries:
    try:
      source_url = entry["source"]

      toi_article = Article(source_url, language="en")

      #To download the article
      toi_article.download()
      
      #To parse the article
      toi_article.parse()
      
      #To perform natural language processing ie..nlp
      toi_article.nlp()

      title_list.append(toi_article.title)
    except:
      title_list.append("")

  bert = AutoModel.from_pretrained('bert-base-uncased')
  tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')

  MAX_LENGHT = 15

  input_list= tokenizer.batch_encode_plus(
      title_list,
      max_length = MAX_LENGHT,
      pad_to_max_length=True,
      truncation=True
  )

  ## convert lists to tensors

  input_seq = torch.tensor(input_list['input_ids'])
  input_mask = torch.tensor(input_list['attention_mask'])

  model = BERT_Arch(bert)

  path = 'fake_news_classification/saved_weights.pt'
  model.load_state_dict(torch.load(path))

  with torch.no_grad():
      preds = model(input_seq, input_mask)
      preds = preds.detach().cpu().numpy()

  preds = np.argmax(preds, axis = 1)

  for i in range(0,len(title_list)):
    if title_list[i] == "":
      preds[i]=-1

  return preds