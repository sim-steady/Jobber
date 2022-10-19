from flask import Flask, render_template, request, session, redirect
import numpy as np
import pandas as pd
import random
import os
import re

app = Flask(__name__)

def article_info():
    job_info={} #it's a nested dictionary with there being a unqique dictionary which stores info for each article

    for label in ["Engineering", "Accounting_Finance", "Healthcare_Nursing", "Sales"]:
        dir_path = f"./data/{label}"
        for filename in sorted(os.listdir(dir_path)):
            #extracting id out of the filename
            id=re.match("Job_(\d+).txt",filename).group(1)

            #setting label for the article in our job_info dictionary
            job_info[id]={}
            job_info[id]["label"]=label

            #opening file
            file_path = os.path.join(dir_path,filename)
            with open(file_path,"r",encoding= 'unicode_escape') as fhand:

                file_string=fhand.read()
                file_data=file_string.splitlines()
                for i,info in enumerate(file_data):
                    lst=re.match("(\w+?): (.+)", info).groups()
                    job_info[id][lst[0]]=lst[1]

                #generating previews
                description=job_info[id]["Description"]
                preview=re.match("(.+?\s+){0,20}",description).group(0)
                job_info[id]["preview"]=preview

    #replacing the special symbol
    for id in job_info.keys():
        job_info[id]["Title"]=re.sub("â\x80\x93","-",job_info[id]["Title"])

    return job_info

all_articles=article_info()

@app.route('/')
def index():
    return render_template('home.html')

@app.route("/full")
def full():
    return render_template('full.html')

@app.route("/explore/<category>")
def explore(category):
    #last 2
    recent_ids=list(all_articles.keys())[-1:-3:-1]
    return render_template('explore.html', all_articles=read_all(),job_info=all_articles, category=category,recent_ids=recent_ids)

@app.route("/explore/article/<id>")
def article(id):
    return render_template('article.html',id=id, job_info=all_articles)

@app.route('/employer', methods=['GET', 'POST'])
def employer():
    if request.method == 'POST':
        # Read the content
        title = request.form['title']
        description = request.form['description']

        # sending the predicted category
        predicted_cat = classifier(title,description)

        all_articles[str(len(all_articles)+1)]={}
        all_articles[str(len(all_articles))]["Title"]=title
        all_articles[str(len(all_articles))]["Description"]=description
        preview=re.match("(.+?\s+){0,20}",description).group(0)
        all_articles[str(len(all_articles))]["preview"]=preview

        return render_template('predicted.html', predicted_cat=predicted_cat, title=title)
    else:
        return render_template('employer.html')

@app.route('/Employer/<category>')
def posting(category):
    all_articles[str(len(all_articles))]["label"]=category
    return redirect("/explore/all")


#Backend
def read_all():
    job_info={}
    for label in ["Engineering", "Accounting_Finance", "Healthcare_Nursing", "Sales"]:
        #creating dict for each category
        job_info[label]={}

        dir_path = f"./data/{label}"
        for filename in sorted(os.listdir(dir_path)):
            #extracting id out of the filename
            id=re.match("Job_(\d+).txt",filename).group(1)

            #setting label for the article in our job_info dictionary
            job_info[label][id]={}

            #opening file
            file_path = os.path.join(dir_path,filename)
            with open(file_path,"r",encoding= 'unicode_escape') as fhand:
                file_string=fhand.read()
                file_data=file_string.splitlines()
                for i,info in enumerate(file_data):
                    lst=re.match("(\w+?): (.+)", info).groups()
                    job_info[label][id][lst[0]]=lst[1]

                job_info[label][id]["id"]=id
                job_info[label][id]["category"]=label
                #generating previews
                description=job_info[label][id]["Description"]
                preview=re.match("(.+?\s+){0,20}",description).group(0)
                job_info[label][id]["preview"]=preview

    #replacing the special symbol
    for label,label_dict in job_info.items():
        for id in label_dict.keys():
            job_info[label][id]["Title"]=re.sub("â\x80\x93","-",job_info[label][id]["Title"])


    #A list with random article data from each category
    all_lst=[random.choice(list(job_info[category].values())) for category in job_info.keys()]
    Engineering=[random.choice(list(job_info["Engineering"].values())) for category in job_info.keys()]
    Healthcare_Nursing=[random.choice(list(job_info["Healthcare_Nursing"].values())) for category in job_info.keys()]
    Sales=[random.choice(list(job_info["Sales"].values())) for category in job_info.keys()]
    Accounting_Finance=[random.choice(list(job_info["Accounting_Finance"].values())) for category in job_info.keys()]

    return_lst={}
    return_lst["all"]=all_lst
    return_lst["Engineering"]=Engineering
    return_lst["Healthcare-Nursing"]=Healthcare_Nursing
    return_lst["Sales"]=Sales
    return_lst["Accounting-Finance"]=Accounting_Finance

    return return_lst


def classifier(title,description):
    #reading vocab
    vocab=[]
    with open("data/vocab.txt") as fhand:
        lines= fhand.read().splitlines()
        for line in lines:
            vocab.append(line.split(":")[0])

    #loading stopwords
    with open("data/stopwords_en.txt") as fhand:
        stopwords=fhand.read().splitlines()


    full=title+" "+description
    #tokenisation
    tokens=re.findall("[a-zA-Z]+(?:[-'][a-zA-Z]+)?",full)

    #preprocessing
    tokens=[token.lower() for token in tokens]
    tokens=[token for token in tokens if len(token)>=2]
    #removing stopwords
    tokens=[token for token in tokens if token not in stopwords]

    #generating vector representation of tokens
    from sklearn.feature_extraction.text import CountVectorizer
    count_vectorizer = CountVectorizer(analyzer = "word",vocabulary = vocab, binary = False)
    count_features=count_vectorizer.fit_transform([' '.join(tokens)])

    import pickle
    pkl_filename = "count_model.pkl"
    with open(pkl_filename, 'rb') as file:
        model=pickle.load(file)

    return model.predict(count_features)[0]
