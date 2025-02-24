from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup as bs
from difflib import SequenceMatcher
from googlesearch import search
import pandas as pd
import requests
import warnings
import PyPDF2
import nltk
import re
import os


warnings.filterwarnings("ignore", module='bs4')

# The following two lines download the stopwords and punkt from the nltk library which are used for text preprocessing.
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

# This function searches Microsoft Bing search engine for a given query and returns a list of URLs up to a certain number.
def searchBing(query, num):
    
    # create an empty list to hold the URLs
    urls1 = []

    # construct the URL for the query
    url1 = 'https://www.bing.com/search?q=' + query

    # send a GET request to the URL with a custom user agent header
    page = requests.get(url1, headers={'User-agent': 'Mighty Near'})

    # parse the HTML content of the page using BeautifulSoup
    soup = bs(page.text, 'html.parser')

    # iterate over all the links in the HTML content
    for link in soup.find_all('a'):
        # get the URL of the link as a string
        url1 = str(link.get('href'))

        # filter out URLs that don't start with 'http' and exclude some specific URLs
        if url1.startswith('http'):
            if not url1.startswith('https://go.m') and not url1.startswith('https://go.m'):
                urls1.append(url1)

    # return the list of URLs up to the given number
    return urls1[:num]

# This function searches Google search engine for a given query and returns a list of URLs up to a certain number.
def searchGoogle(query, num):

    # create an empty list to hold the URLs
    urls2 = []

    # construct the URL for the query
    url2 = 'https://www.google.com/search?q=' + query

    # send a GET request to the URL with a custom user agent header
    page = requests.get(url2, headers={'User-agent': 'John Doe'})

    # parse the HTML content of the page using BeautifulSoup
    soup = bs(page.text, 'html.parser')

    # iterate over all the links in the HTML content
    for link in soup.find_all('a'):
        # get the URL of the link as a string
        url2 = str(link.get('href'))

        # filter out URLs that don't start with 'http' and exclude some specific URLs
        if url2.startswith('http'):
            if not url2.startswith('https://go.m') and not url2.startswith('https://go.m') and not url2.startswith(
                    'https://maps.google'):
                urls2.append(url2)

    # return the list of URLs up to the given number
    return urls2[:num]


# This function takes a URL as input and extracts the text content from the page.
# The text content is extracted using BeautifulSoup library and then returned.
def extractText(url):
    page = requests.get(url)
    soup = bs(page.text, 'html.parser')
    return soup.get_text()

# This variable initializes a set of stopwords which are commonly occurring words that do not provide useful information.
stop_words = set(nltk.corpus.stopwords.words('english'))


# This function takes a string as input and removes stopwords from it using nltk library.
# The string is first tokenized into words and then stop words are removed using list comprehension.
def purifyText(string):
    words = nltk.word_tokenize(string)
    return (" ".join([word for word in words if word not in stop_words]))


'''
A function to verify the text against the web sources and return the matching sites.

Parameters:
string: The text string to be verified against web sources
results_per_sentence: Number of results per sentence to retrieve from web sources
'''
def webVerify(string, results_per_sentence):

    # Tokenize the string into sentences using nltk.sent_tokenize
    sentences = nltk.sent_tokenize(string)
    # List to store the matching sites
    matching_sites = []
    # Search the web using the searchBing function for the entire string and each sentence
    for url in searchBing(query=string, num=results_per_sentence):
        matching_sites.append(url)
    for sentence in sentences:
        for url in searchBing(query=sentence, num=results_per_sentence):
            matching_sites.append(url)

    # Search the web using the searchGoogle function for the entire string and each sentence
    for url in searchGoogle(query=string, num=results_per_sentence):
        matching_sites.append(url)
    for sentence in sentences:
        for url in searchGoogle(query=sentence, num=results_per_sentence):
            matching_sites.append(url)

    # Return a list of unique matching sites using list(set())
    return (list(set(matching_sites)))


# Similarity function
# The function calculates and compares instances to get a ratio for them.

def similarity(str1, str2):
    # Returns a ratio of similarity between two strings.
    # Uses the SequenceMatcher method from the difflib module.
    return (SequenceMatcher(None, str1, str2).ratio()) * 100


# Generate report function
# Passed input text or file text as parameters.

def report(text):
    # Generates a report of matching websites and their similarity scores to the input text.
    matching_sites = webVerify(purifyText(text), 2)
    matches = {}

    # Iterate through each matching site and calculate the similarity score with the input text.
    for i in range(len(matching_sites)):
        matches[matching_sites[i]] = similarity(text, extractText(matching_sites[i]))

    # Sort the matches dictionary by descending similarity score.
    matches = {k: v for k, v in sorted(matches.items(), key=lambda item: item[1], reverse=True)}

    # Calculate the total similarity score.
    sum = 0
    for k, v in matches.items():
        sum += v
    matches["TOTAL SIMILARITY"] = sum

    # Return the matches dictionary with similarity scores and the total similarity score.
    return matches


# Return Table function
# Used for returning data-frame to the final report page.
# Define a function to return a HTML table from a dictionary
def returnTable(dictionary):
    df = pd.DataFrame({'Similarity (%)': dictionary})
    # df = df.fillna(' ').T
    # df = df.transpose()
    return df.to_html(classes="table ")

# Set up upload folder and allowed extensions
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

# Create a Flask app instance and configure upload folder and secret key
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['SECRET_KEY'] = 'super secret key'

# Define a function to check if a file is allowed based on its extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['text'] != '' and request.files['file'].filename == '':
            word = request.form['text']
            masukan = "word"
            with open('word.txt', 'w', encoding='utf-8') as f:
                f.write(word)
            return redirect(url_for('plagiarism', name=masukan) + "#hasil")
        elif request.files['file'].filename != '' and request.form['text'] == '':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file1 = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file1.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file1 and allowed_file(file1.filename):
                filename = secure_filename(file1.filename)
                file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('plagiarism', name=filename) + "#hasil")
        else:
            flash('Please fill the form')
            return redirect(request.url)
    return render_template("index.html")


@app.route('/plagiarism/<name>', methods=['GET', 'POST'])
def plagiarism(name):
    domain = "co.id"
    link_output = []
    hasil_plagiarism = []
    hasil_link = []
    hasil_persen = 0
    inputan_mentah = ""
    inputan = []
    filename = ""
    text = ""
    hasil_plagiarism_final = []
    hasil_link_final = []
    link_blocked = ["id.linkedin.com", "linkedin.com", "youtube.com", "instagram.com", "facebook.com", "tokopedia.com",
                    "twitter.com", "reddit.com", "bukalapak.com", "shopee.com", "blibli.com"]
    if request.method == 'POST':
        if request.form['text'] != '' and request.files['file'].filename == '':
            word = request.form['text']
            filename += "word"
            with open('word.txt', 'w', encoding='utf-8') as f:
                f.write(word)
        elif request.files['file'].filename != '' and request.form['text'] == '':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                pdfFileObj = open('uploads/{}'.format(filename), 'rb')
                pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
                num_pages = pdfReader.numPages
                count = 0
                while count < num_pages:
                    pageObj = pdfReader.getPage(count)
                    count += 1
                    text += pageObj.extractText()
        else:
            flash('Please fill the form')
            return redirect(request.url)

        if filename == "word":
            if request.method == 'POST':
                inputan_mentah += request.form['text']
            else:
                f = open("word.txt", "r")
                inputan_mentah += f.read()
            inputan += inputan_mentah.replace("\n", " ").split(". ")
            # This code takes input from a web page and performs plagiarism detection using Google search API.
            # Loop through each sentence in inputan
            for i in range(len(inputan)):
                # Form a search query from the sentence
                query = '"' + inputan[i].strip().replace(".", "").replace('"', "'") + '"'
                # Search for the query in Google and store the links in a list
                for j in range(len(list(search(query, num_results=10, sleep_interval=2)))):
                    if i != j:
                        continue
                    hasil_plagiarism.append(inputan[i])
                    hasil_link.append(list(search(query, num_results=10, sleep_interval=2))[j])
            # Check for links that are blocked and remove them from the list        
            for i in range(len(hasil_plagiarism)):
                for j in range(len(hasil_link)):
                    if i != j:
                        continue
                    while True:
                        for k in range(len(link_blocked)):
                            if link_blocked[k] in hasil_link[j]:
                                break
                        else:
                            hasil_plagiarism_final.append(hasil_plagiarism[i])
                            hasil_link_final.append(hasil_link[j])
                            break
                        break

            # Calculate plagiarism percentage
            count = len(inputan)
            count_hasil = len(hasil_link_final)
            hasil_persen += (count_hasil / count) * 100
            # Store final links in a list
            for i in range(len(hasil_link_final)):
                link_output.append(hasil_link_final[i])
        else:
            inputan += text.replace("\n", " ").split(". ")
            for i in range(len(inputan)):
                query = '"' + inputan[i].strip().replace(".", "").replace('"', "'") + '"'
                for j in range(len(list(search(query, num_results=10, sleep_interval=2)))):
                    if i != j:
                        continue
                    hasil_plagiarism.append(inputan[i])
                    hasil_link.append(list(search(query, num_results=10, sleep_interval=2))[j])
            for i in range(len(hasil_plagiarism)):
                for j in range(len(hasil_link)):
                    if i != j:
                        continue
                    while True:
                        for k in range(len(link_blocked)):
                            if link_blocked[k] in hasil_link[j]:
                                break
                        else:
                            hasil_plagiarism_final.append(hasil_plagiarism[i])
                            hasil_link_final.append(hasil_link[j])
                            break
                        break
            count = len(inputan)
            count_hasil = len(hasil_link_final)
            hasil_persen += (count_hasil / count) * 100
            for i in range(len(hasil_link_final)):
                link_output.append(hasil_link_final[i])
    else:
        if name == "word":
            if request.method == 'POST':
                inputan_mentah += request.form['text']
            else:
                f = open("word.txt", "r")
                inputan_mentah += f.read()
            inputan += inputan_mentah.replace("\n", " ").split(". ")
            for i in range(len(inputan)):
                query = '"' + inputan[i].strip().replace(".", "").replace('"', "'") + '"'
                for j in range(len(list(search(query, num_results=10, sleep_interval=2)))):
                    if i != j:
                        continue
                    hasil_plagiarism.append(inputan[i])
                    hasil_link.append(list(search(query, num_results=10, sleep_interval=2))[j])
            for i in range(len(hasil_plagiarism)):
                for j in range(len(hasil_link)):
                    if i != j:
                        continue
                    while True:
                        for k in range(len(link_blocked)):
                            if link_blocked[k] in hasil_link[j]:
                                break
                        else:
                            hasil_plagiarism_final.append(hasil_plagiarism[i])
                            hasil_link_final.append(hasil_link[j])
                            break
                        break
            count = len(inputan)
            count_hasil = len(hasil_link_final)
            hasil_persen += (count_hasil / count) * 100
            for i in range(len(hasil_link_final)):
                link_output.append(hasil_link_final[i])
        else:
            pdfFileObj = open('uploads/{}'.format(name), 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            num_pages = pdfReader.numPages
            count = 0
            text = ""
            while count < num_pages:
                pageObj = pdfReader.getPage(count)
                count += 1
                text += pageObj.extractText()
            inputan += text.replace("\n", " ").split(". ")
            for i in range(len(inputan)):
                query = '"' + inputan[i].strip().replace(".", "").replace('"', "'") + '"'
                for j in range(len(list(search(query, num_results=10, sleep_interval=2)))):
                    if i != j:
                        continue
                    hasil_plagiarism.append(inputan[i])
                    hasil_link.append(list(search(query, num_results=10, sleep_interval=2))[j])
            for i in range(len(hasil_plagiarism)):
                for j in range(len(hasil_link)):
                    if i != j:
                        continue
                    while True:
                        for k in range(len(link_blocked)):
                            if link_blocked[k] in hasil_link[j]:
                                break
                        else:
                            hasil_plagiarism_final.append(hasil_plagiarism[i])
                            hasil_link_final.append(hasil_link[j])
                            break
                        break
            count = len(inputan)
            count_hasil = len(hasil_link_final)
            hasil_persen += (count_hasil / count) * 100
            for i in range(len(hasil_link_final)):
                link_output.append(hasil_link_final[i])
    return render_template("index.html", hasil_persen=hasil_persen, data=inputan,
                           hasil_plagiarism=hasil_plagiarism_final,
                           link_output=link_output, hasil_link=hasil_link_final)


# To generate report
@app.route('/report', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form['text']

        if len(result) == 0:
            resultf = request.files['myfile']

            result = {'myfile': resultf.read()}
        test = returnTable(report(str(result)))

        return render_template('report.html', PWM_value=test)


# Compare b/w two files code below
# Check root_text_from_html = 1  & root_file_from_html = 2
# Check plag_text_from_html = 1@ & plag_file_from_html = 2@
@app.route('/f2f_kmp', methods=['GET', 'POST'])
def index1():
    global rootText, rootFile, plagText, plagFile
    if request.method == 'POST':
        # 1(available) & 2(unavailable)
        if request.form['root_text_from_html'] != '' and request.files['root_file_from_html'].filename == '':
            # 1@(available) & 2@(unavailable)
            if request.form['plag_text_from_html'] != '' and request.files['plag_file_from_html'].filename == '':
                rootText = request.form['root_text_from_html']
                plagText = request.form['plag_text_from_html']
                return redirect(url_for('onRunF2F'))
            # 1@(unavailable) & 2@(available)    
            elif request.form['plag_text_from_html'] == '' and request.files['plag_file_from_html'].filename != '':
                rootText = request.form['root_text_from_html']
                if 'plag_file_from_html' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                plagFile = request.files['plag_file_from_html']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if plagFile.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if plagFile and allowed_file(plagFile.filename):
                    filename = secure_filename(plagFile.filename)
                    plagFile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return redirect(url_for('onRunF2F'))
            # BOTH 1@ & 2@(unavailable)        
            else:
                flash('Please fill the form')
                return redirect(request.url)
        # 1(unavailable) & 2(available)                
        elif request.form['root_text_from_html'] == '' and request.files['root_file_from_html'].filename != '':
            # 1@(available) & 2@(unavailable)
            if request.form['plag_text_from_html'] != '' and request.files['plag_file_from_html'].filename == '':
                plagText = request.form['plag_text_from_html']
                if 'root_file_from_html' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                rootFile = request.files['root_file_from_html']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if rootFile.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if rootFile and allowed_file(rootFile.filename):
                    filename = secure_filename(rootFile.filename)
                    rootFile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('onRunF2F'))
            # 1@(unavailable) & 2@(available) ---> Only both 2 & 2@ are availabe    
            elif request.form['plag_text_from_html'] == '' and request.files['plag_file_from_html'].filename != '':
                # For 2 -> (root_file_from_html)
                if 'root_file_from_html' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                rootFile = request.files['root_file_from_html']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if rootFile.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if rootFile and allowed_file(rootFile.filename):
                    filename = secure_filename(rootFile.filename)
                    rootFile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # For 2 -> (root_file_from_html)
                if 'plag_file_from_html' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                plagFile = request.files['plag_file_from_html']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if plagFile.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if plagFile and allowed_file(plagFile.filename):
                    filename = secure_filename(plagFile.filename)
                    plagFile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                return redirect(url_for('onRunF2F'))

            # BOTH 1@ & 2@(unavailable)        
            else:
                flash('Please fill the form')
                return redirect(request.url)

                # When nothing is available (1, 2, 1@, ,2@)
        else:
            flash('Please fill the form')
            return redirect(request.url)

    return render_template("f2f.html")

# This function is used to compute the Longest Prefix Suffix (LPS) array for a given pattern.
def computeLPSArray(pat, M, lps):
    len = 0 # Initialize length of the previous longest prefix suffix
    lps[0] # lps[0] is always 0
    i = 1
    # Loop to fill LPS array
    while i < M:
        if pat[i] == pat[len]: # If the characters match, increment length of longest prefix suffix
            len += 1
            lps[i] = len
            i += 1
        else: # If characters do not match
            if len != 0: # Check if the previous character had a longest prefix suffix
                len = lps[len - 1] # Set length to the longest prefix suffix of the previous character
            else: # If the previous character did not have a longest prefix suffix
                lps[i] = 0 # Set longest prefix suffix of the current character to 0
                i += 1


def KMPSearch(pat, text, p):
    M = len(pat) # length of the pattern
    N = len(text) # length of the text
    lps = [0] * M # create a list to store the longest proper suffix
    j = 0 # index for pattern

    # compute the longest proper suffix
    computeLPSArray(pat, M, lps)

    i = 0 # index for text
    while i < N:
        if pat[j].lower() == text[i].lower(): # if the characters match
            i += 1 # increment index of text
            j += 1 # increment index of pattern

        if j == M: # if pattern is found
            p += 1 # increment count of patterns found
            j = lps[j - 1] # reset index of pattern
            break # exit the loop

        elif i < N and pat[j].lower() != text[i].lower(): # if characters don't match
            if j != 0: # if not at the beginning of pattern
                j = lps[j - 1]  # reset index of pattern to previous character
            else:
                i += 1 # increment index of text
    return p # return the count of patterns found


@app.route('/f2f_kmp/onRunF2F', methods=['GET', 'POST'])
def plag():
    if request.method == 'POST':
        rootText = request.form['root_text_from_html']
        plagText = request.form['plag_text_from_html']
        plagFile = request.files['plag_file_from_html']
        rootFile = request.files['root_file_from_html']

        # result = request.form['text']

        # if len(result) == 0:
        #    resultf = request.files['myfile']   

        text = rootText
        pattern = plagText

        if len(text) == 0:
            # resultf = request.files['myfile']
            text = {'root_file_from_html': rootFile.read()}

        if len(pattern) == 0:
            # resultf = request.files['myfile']
            pattern = {'plag_file_from_html': plagFile.read()}

        sentences = re.split(r'[\.\?!\r\n]', pattern)

        counter_matched = 0
        counter_total = 0
        p = 0
        for pattern in sentences:
            pattern = pattern.strip()
            if len(pattern) > 0:
                counter_total += 1
                counter_matched += KMPSearch(pattern, text, p)
        rez = counter_matched * 100 / counter_total

        return render_template("f2f.html", F2F_value=rez)


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5555)
    app.run()
    report('This is a pure test')
