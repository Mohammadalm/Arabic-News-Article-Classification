#!/usr/bin/python3

import os, pickle, re
from string import punctuation
punctuation += '،؛؟”0123456789“'
# import nltk

categories_dict = {'religion':6, 'world':5, 'sport':2, 'society':4, 'algeria':1, 'entertainment':3}


#Local
root = '/media/said/DevStuff/PFE/ArabicTextCategorization/'
#Server
# root = '/home/said/categ/ArabicTextCategorization/'

tools = root+'Tools/'
farasa = tools+'farasa'
farasaSegmenter = farasa + '/segmenter'


stopWords = open(os.path.join(tools, "arabic-stop-words/list.txt")).read().splitlines()
stopWords.append('ﺮﺒﺨﻟا')

class Helper():
    def __init__(self, article = False):
        self.article = article

    ##~~Pickle helpers~~#
    def getPickleContent(self, pklFile):
        with open (pklFile, 'rb') as fp:
            itemlist = pickle.load(fp)
        return itemlist

    def setPickleContent(self, fileName, itemList):
        with open(fileName+'.pkl', 'wb') as fp:
            pickle.dump(itemList, fp)
    #~~~~~~~~~~~~~~~~~~#

    def getArticleContent(self, article):
        if os.path.exists(article):
            return open(article, 'r').read()

    def dropNline(self, article):
        if os.path.exists(article):
            content = self.getArticleContent(article)
            return re.sub(r'\n', ' ', content)

    def getLemmaArticle(self, content):
        jarFarasaSegmenter = os.path.join(farasaSegmenter, 'FarasaSegmenterJar.jar')

        tmp = os.path.join(farasaSegmenter, 'tmp')
        if os.path.exists(tmp):
            os.system('rm '+tmp)
        open(tmp, 'w').write(content)

        tmpLemma = os.path.join(farasaSegmenter, 'tmpLemma')
        if os.path.exists(tmpLemma):
            os.system('rm '+tmpLemma)

        os.system('java -jar ' + jarFarasaSegmenter + ' -l true -i ' + tmp + ' -o ' + tmpLemma)

        # os.system('echo "' + content + '" > ' + tmp + ' | java -jar ' + jarFarasaSegmenter + ' -l true -i ' + tmp + ' -o ' + tmpLemma)
        return self.getArticleContent(tmpLemma)


    def getCleanArticle(self, content):
        content = ''.join(c for c in content if c not in punctuation)
        # words = nltk.word_tokenize(content)   
        words = content.split()     
        cleandWords = [w for w in words if w not in stopWords]
        return ' '.join(cleandWords)


    def getBagWordsArticle(self, content):
        cleanArticle = self.getCleanArticle(content)
        lemmaContent = self.getLemmaArticle(cleanArticle)
        cleanArticle = self.getCleanArticle(lemmaContent)
        return cleanArticle.split()


    #~~~ Set and get Model
    def getModel(self, name):
        model = self.getPickleContent(os.path.join(root, 'models/dumps/'+name+'/model_'+name+'.pkl'))
        cv = self.getPickleContent(os.path.join(root, 'models/dumps/'+name+'/cv_'+name+'.pkl'))
        tfidf = self.getPickleContent(os.path.join(root, 'models/dumps/'+name+'/tfidf_'+name+'.pkl'))
        return model, cv, tfidf

    def setModel(self, name, model, cv, tfidf):
        path = os.path.join(root, 'models/dumps/'+name)
        if not os.path.exists(path):
            os.mkdir(path)
        self.setPickleContent(os.path.join(root, path+'/model_'+name), model)
        self.setPickleContent(os.path.join(root, path+'/cv_'+name), cv)
        self.setPickleContent(os.path.join(root, path+'/tfidf_'+name), tfidf)
    #~~~~~~~~~~~~~~~~~~

    def pipeline(self, content):
        return ' '.join(self.getBagWordsArticle(content))


    def predict(self, content):
        article = self.pipeline(content)
        model, cv, tfidf = self.getModel('sgd_94')
        vectorized = tfidf.transform(cv.transform([article]))
        predicted = model.predict(vectorized)
        keys = list(categories_dict.keys())
        values = list(categories_dict.values())
        result = keys[values.index(predicted[0])].upper()
        return result


    def main(self):
        content = self.getArticleContent(self.article)
        lemma = self.getLemmaArticle(content)
        print(lemma)


if __name__ == '__main__':
    help = Helper()
    
    content = 'أمرت السلطات القطرية الأسواق والمراكز التجارية في البلاد برفع وإزالة السلع الواردة من السعودية والبحرين والإمارات ومصر في الذكرى الأولى لإعلان هذه الدول الحصار عليها.'



    result = help.getLemmaArticle(content)

    print(result)