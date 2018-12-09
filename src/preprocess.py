
# coding: utf-8

# # Pre-processing Comment Text

# In[1]:


import csv
import re as re
import string
from nltk.corpus import stopwords
import nltk.stem


# In[ ]:


# ALREADY CLEANED:
# Sentences marked by begin/end <EOS>
# Non-alphabet characters <SPECIAL>
# URLs <URL>
# All lowercase


# In[2]:


stop_words = set(stopwords.words('english'))
stop_words.remove("not")
stop_words.remove("no")


# In[3]:


# def preprocess(comment):   
#     # Remove punctuation, numbers, non-alphabet characters (again), extra whitespace
#     words = re.sub("([^\w]|[\d_])+", " ", comment).split()

#     # Remove stop words and tags
#     # Stem with Porter's Algorithm
#     ps = nltk.stem.PorterStemmer()
#     filtered_sentence = [ps.stem(w) for w in words if (w not in stop_words)
#                          and (w != 'EOS' and w != 'URL' and w!= 'SPECIAL')] 
    
#     return " ".join(filtered_sentence)


# In[4]:


def preprocessModified(comment):
    
    # Fix contractions
    comment = comment.replace("ca n't", "cannot")
    comment = comment.replace("wo n't", "not") # will is a stop word
    comment = comment.replace("n't", "not")
    comment = comment.replace("'ve", "") # have is a stop word
    
    # Remove word if it contains numbers
    comment = re.sub(r'\w*\d\w*', '', comment).strip()
    
    # Remove punctuation
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    comment = regex.sub('', comment)
    
    # Remove extra whitespace
    words = comment.split()
    
    ps = nltk.stem.PorterStemmer()
    filtered_sentence = [ps.stem(w) for w in words if (w not in stop_words)
                        and (w != 'EOS' and w != 'URL' and w!= 'SPECIAL')
                        and (w != 'gt')] 
    
    return " ".join(filtered_sentence)


# In[ ]:


# Cleans politics.tsv -> processed.tsv

with open("processed2.tsv", "w") as tsv_wr:
    with open("politics.tsv") as tsv_rd:
        wr = csv.writer(tsv_wr, delimiter="\t")
        rd = csv.reader(tsv_rd, delimiter="\t", quotechar='"')
        for row in rd:
            commentId = row[3]
            comment = row[9]
            processed = preprocessModified(comment)
            wr.writerow([commentId, processed])

