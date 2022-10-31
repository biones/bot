#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.feature_extraction.text import TfidfVectorizer
#import spacy
#import ginza
from functools import *
import numpy as np 
import re
import pandas as pd
import tweepy


def getApiInstance(account="fukushibot"):
    if account!="fukushibot":
        consumer_key = ""
    else:
        consumer_key = ""
        
    # OAuth認証
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # APIのインスタンスを生成
    api = tweepy.API(auth, wait_on_rate_limit = True)
    return api

def search(api,search_query,n=10000):
    #texts=tweepy.Cursor(api.search,search_word).items(n)
    texts=tweepy.Cursor(api.search, q =search_query,  include_entities = True, tweet_mode = 'extended', lang = 'ja').items(n)
        
    ret=[{"id":r.id,"name":r.user.name,"screen_name":r.user.screen_name,"location":r.user.location,"description":r.user.description,"search_query":search_query,"tweet":r.full_text,"retweet_count":r.retweet_count}
          for r in texts]    
    df_tw=pd.DataFrame(ret)
    #tmp=list(map(lambda x:x["tweet"],ret))
    class ret_tmp:
        pass
    ret_tmp.df_tw=df_tw
    ret_tmp.tweet=df_tw.tweet
    return ret_tmp
    #return {"df_tw":df_tw,"tweet":df_tw.tweet}


#stop_words = list(ginza.stop_words)
#stop_words.extend(['max', 'エスマックス', 'smaxjp'])
def soften(word):
    replace_table = {
      '為る': 'する', '成る': 'なる', '遣る': 'やる', '有る': 'ある', '無い': 'ない',
      '御洒落': 'おしゃれ', '撫子': 'なでしこ', '未だ未だ': 'まだまだ', '迚も': 'とても',
      '唯': 'ただ', '筈': 'はず', '若し': 'もし'
  }
    return replace_table.get(word, word)

def get_usertimeline(screen_name,api):
    tweet=list(tweepy.Cursor(api.user_timeline,count=2000,screen_name=screen_name,include_rts=True,exclude_replies = False).items())
    texts=[]
    for r in tweet:
        texts.append(r.text)
    return texts
    

def insertusertable(r):
    u=r.user
    dd=[u.id,u.screen_name,u.name,search_query,u.description,r.full_text,u.location]    
    cur.execute("insert into users(id,screen_name,name,search_query,description,tweet,location) values(?,?,?,?,?,?,?)",dd)
    
def inserttweet(tw):
    tw=[r.id,r.full_text,r.user.screen_name,r.user.name,r.user.description,search_query,r.created_at,r.user.location,r.retweet_count]
    cur.execute("insert into tweets(id,tweet,screen_name,name,description,search_query,created_at,location,retweet_count) values(?,?,?,?,?,?,?,?,?)",tw)    



def make_docmat(texts,POS_NOUN = ['PROPN', 'NOUN'],cvtype="count",addstopwords=[]):    
    nlp = spacy.load('ja_ginza')
    NGRAM=1
    MAX_DF=0.95
    MIN_DF=0.001
    NUM_VOCAB=200

    # print(texts)
    #https://yu-nix.com/blog/2021/3/3/spacy-pos-list/
    #https://qiita.com/kei_0324/items/400f639b2f185b39a0cf
        
    #POS_NOUN = ['PROPN', 'NOUN',"VERB","ADJ"] # 固有名詞と名詞
     # 固有名詞と名詞
    tokens = []
    for text in texts:
        #text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
        text=re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+$,%#]+)", "" ,text) 
        try:
            doc=nlp(text)   
        except:
            tokens.append("")
            continue
        tmp=""
        for d in doc:
            if d.pos_ in POS_NOUN or len(POS_NOUN) ==0:
                tmp+=" "+d.lemma_

        tokens.append(tmp)
        #print(tmp)
    
    if cvtype=="count":
        cv = CountVectorizer(stop_words=[],ngram_range=(1,NGRAM), max_df=MAX_DF, min_df=MIN_DF, max_features=NUM_VOCAB)
    else:
        cv = TfidfVectorizer(stop_words=[],ngram_range=(1,NGRAM), max_df=MAX_DF, min_df=MIN_DF, max_features=NUM_VOCAB)
        
    docmat = cv.fit_transform(tokens).toarray()
    print("Shape of X : %s" % (docmat.shape,))
    vocab  = cv.vocabulary_ 
    print("Num of vocab : %s" % (len(vocab)))
    print("Sample of vocab : %s" % (list(vocab.keys())[:-1]))
    class ret:
        pass
    
    w=np.array(cv.get_feature_names())
    freq=np.sum(docmat,axis=0)
    idx=np.argsort(freq)[::-1]
    freq=freq[idx]
    w=w[idx]
    
    ret.docmat=pd.DataFrame(docmat[:,idx])
    ret.docmat.columns=w
    ret.freq=freq
    ret.texts=texts
    ret.word_freq=pd.DataFrame({"word":w,"freq":freq})
    return ret

#from sklearn.decomposition import LatentDirichletAllocation

def LDA(df_lda,n_components=20,Nword=20,filename="tmp_topic"):

    lda = LatentDirichletAllocation(n_components=n_components)
    lda.fit(df_lda.docmat)
    topic=np.argmax(lda.transform(df_lda.docmat),axis=1)

    for i in range(len(lda.components_)):
        tmp=lda.components_[i]
        idx=tmp.argsort()[::-1][:Nword]
        print(i,np.array(df_lda.docmat.columns[idx]))

    #sorted(vocab_freq.items(), key=lambda x:x[0],reverse=True)
    import pandas as pd
    pd.set_option('display.max_rows',500)
    tdf=pd.concat([df_lda.docmat,pd.DataFrame({"topic":topic})],axis=1)
    tdf=tdf.sort_values("topic")
    tdf.to_csv("/Users/satoshi/Desktop/"+filename)


def getdata(search_query,n=1000):    
    for r in tweepy.Cursor(api.search, q =search_query,  include_entities = True, tweet_mode = 'extended', lang = 'ja').items(n):
        [r.id,r.full_text,r.user.screen_name,r.user.name,r.user.description,search_query,r.created_at,r.user.location,r.retweet_count]
    return 


#test
