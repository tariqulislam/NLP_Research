from os import listdir
from os.path import dirname, join, isfile, abspath
import PyPDF2
import re
import pprint
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import gensim
from gensim import corpora
from database import getTrainedDataSet, getCategories

## using the cleaning words repository from documents
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def cleanDoc(doc):
    stop_free =" ". join([i for i in doc.lower().split() if i not in stop])
    punc_free =''. join(ch for ch in stop_free if ch not in exclude)
    normalized = " ". join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

def PDFRead(fileName):
    # Read the pdf file 
    pdfFileObj = open(fileName, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    extractText = ''
    for i in range(0, pdfReader.numPages -1):
        pageObj = pdfReader.getPage(i)
        extractText +=  pageObj.extractText()
    pdfFileObj.close()
    return extractText

def getHighFreqWord(docArr):
    freqDis = nltk.FreqDist(docArr)
    #wordCount = len(docArr)
    #print(wordCount)
    return freqDis.most_common(100)
    
def buildDocCorpus(lstFiles):
    
    file_list = [f[1] for f in lstFiles]
    doc_list = [PDFRead(f[0]) for f in  lstFiles]
     # doc_list = re.split(r"\.\s*", extractText)
    doc_templates = [doc.replace("\n", "") for doc in doc_list]
    doc_clean = [cleanDoc(doc).split() for doc in doc_templates]
    

    ##         Get the document frequency and compare to dataset and interset information create category   ##
    docFrequnecy = [getHighFreqWord(doc) for doc in doc_clean]
    print('\r\n\r\n')
    print("---------------------- start finding document word frequency -----------------------")
    pprint.pprint(docFrequnecy)
    print('\r\n\r\n')
    print("---------------------- End finding document word frequency -----------------------")
    lstTrainDataset = [str(tdataSet[0]).strip() for tdataSet in convertTrainedDataArr(getTrainedDataSet())]
    ##pprint.pprint(lstTrainDataset)
    lstCategory = convertCategoryDataArr(getCategories())
    ##pprint.pprint(lstCategory)
        #compaire similar word
    total_frequency_arr = []
    for i in range(len(docFrequnecy)):
        lstdoc = [str(doc[0]).strip() for doc in docFrequnecy[i]]
        similar_element = list(set(lstTrainDataset).intersection(lstdoc))
        document_name = file_list[i]
        lstSimilarElmCat = []
        if len(similar_element) >= 1:
            lstSimilarElmCat = [tdd + (document_name,) for tdd in convertTrainedDataArr(getTrainedDataSet()) if tdd[0] in similar_element]
            total_frequency_arr.append(lstSimilarElmCat)
        else:
            lstSimilarElmCat = [('NAN', 'NAN', document_name)]
            total_frequency_arr.append(lstSimilarElmCat)
    
    doc_classification_freq = []
              
    for docFreq in total_frequency_arr:
        if len(docFreq) >=1:
            totalMedical = 0
            totalLegal = 0
            totalInternet =0
            temoDoc = ''
            for keyword,cassification, document in docFreq:
                temoDoc = document
                if cassification == "MEDICAL_ISSUE":
                    totalMedical += 1          
                if cassification == "LEGAL_ISSUE":
                    totalLegal += 1   
                if cassification == "INTERNET_ISSUE":
                    totalInternet += 1
        doc_classification_freq.append((temoDoc,totalMedical, totalLegal, totalInternet))

    print("\r\n\r\n")
    print("----------- Start Organizating  classification frequency with document ---------------")
    pprint.pprint(doc_classification_freq)
    print("----------- End Document classification information ---------------")
    print("\r\n\r\n")

    classified_documents = []

    for document, medical, legal, internet in doc_classification_freq:
        if medical == 0 and legal == 0 and internet == 0:
            classified_documents.append((document, 'NO-CLASSIFICATION'))
        else:
            if medical > legal  and medical > internet:
                classified_documents.append((document, 'MEDICAL_ISSUE'))
            
            if legal > medical and legal > internet:
                classified_documents.append((document, 'LEGAL_ISSUE'))
            
            if internet > medical and internet > legal:
                classified_documents.append((document, 'INTERNET_ISSUE'))

    print("\r\n\r\n")
    print("----------- Start Document classification information ---------------")
    pprint.pprint(classified_documents)
    print("----------- End Document classification information ---------------")
    print("\r\n\r\n")

    print("--------------------- Start build corpus by LDA for documents -----------------")
    dictionary  = corpora.Dictionary(doc_clean)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]

    # Creating the object for LDA model using gensim library
    Lda = gensim.models.ldamodel.LdaModel
    # Running and Trainign LDA model on the document term matrix.
    ldamodel = Lda(doc_term_matrix, num_topics=3, id2word = dictionary, passes=50)
    pprint.pprint(ldamodel.print_topics(num_topics=3, num_words=30))

    print("------------------- End Build corpus by LDA for documents -----------------------")


def convertTrainedDataArr(lstData):
    tData = []
    for doc in lstData:
        temp_value = ''
        temp_cat = ''
        for key, value in doc.items():
            if key == 'data_field':
                if len(value) != 0:
                    temp_value = str(value).strip()
            if key == 'data_category':
                if len(value) != 0:
                    temp_cat = str(value).strip()
        if temp_value and temp_cat:
            tData.append((temp_value, temp_cat))

    return tData

def convertCategoryDataArr(lstData):
    cData = []
    for cat in lstData:
        for key, value in cat.items():
            if key == 'name' and value:
                cData.append(str(value).strip())
    return cData

def main():
    corpus_raw_files_directory = './corpus_raw_doc'
    lstFiles = [(join(corpus_raw_files_directory,f), f) for f in listdir(corpus_raw_files_directory) if isfile(join(corpus_raw_files_directory, f))]
    buildDocCorpus(lstFiles)

if __name__ == "__main__":
    main()
