import os
import string
import math
import nltk
import smtplib
import requests
import datetime
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

from bs4 import BeautifulSoup
from datetime import date
from urllib.request import Request, urlopen
from email.message import EmailMessage
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

def get_preprocessed(text):
    text = text.lower()
    for ponctuation in string.punctuation:
        text = text.replace(ponctuation, '')
    return text

def get_lemmatized_tokens(text):
    text = get_preprocessed(text)
    words = nltk.word_tokenize(text)
    return [nltk.stem.WordNetLemmatizer().lemmatize(word) for word in words]

def get_average_tfid_value(X_i):
    sum = 0
    n = 0
    for j in range(len(X_i)):
        if X_i[j] != 0:
            sum += X_i[j]
            n += 1
    return sum/n

def get_sentence_treshold(weights, treshold):
    sorted_weights = sorted(weights, reverse=True)
    proportion = treshold*len(weights)
    first_ok_idx = math.ceil(proportion)
    optimal_weight = sorted_weights[first_ok_idx]
    return optimal_weight

def get_sentence_infos(text):
    sentence_list = nltk.sent_tokenize(text)
    X = TfidfVectorizer(tokenizer=get_lemmatized_tokens, stop_words=stopwords.words('french')).fit_transform(sentence_list)
    sentences_tfid_weights = [get_average_tfid_value(X[i].toarray()[0]) for i in range(X.shape[0])]
    sentence_treshold = get_sentence_treshold(sentences_tfid_weights, extraction_percentage)
    return sentence_list, X, sentences_tfid_weights, sentence_treshold

def get_article_from_filename(link):
    req = Request(link, headers={'User-Agent': 'XYZ/3.0'})
    webpage = urlopen(req, timeout=10).read()
    soup = BeautifulSoup(webpage, 'html.parser')

    title = soup.find_all("title")[0].get_text()
    filename = '_'.join(title.split(' '))
    return filename, title, soup

def save_article(filename, title, link, soup):
    f = open('articles/' + filename + '.txt', 'w')

    f.writelines(title + '\n')
    f.writelines(link + '\n\n')

    has_seen_a_lire_aussi = False
    for data in soup.find_all("p")[2:]:
        if 'À lire aussi' in data.get_text():
            has_seen_a_lire_aussi = True
        if not has_seen_a_lire_aussi:
            f.writelines(data.get_text() + '\n')

    f.close()

def get_and_save_article(link):
    filename, title, soup = get_article_from_filename(link)
    save_article(filename, title, link, soup)
    return title, filename 

def get_raw_text_from(filename):
    document = open('articles/' + filename + '.txt', 'r')
    text = document.read()
    document.close()
    return text

def get_summary(text):
    sentence_list, X, sentences_tfid_weights, sentence_treshold = get_sentence_infos(text)
    summary = '        '
    last_idx_picked = -2
    for i in range(X.shape[0]):
        if sentences_tfid_weights[i] >= sentence_treshold:
            if last_idx_picked == (i-1):
                summary += ' '
            else:
                summary += '\n       '
            last_idx_picked = i
            summary += sentence_list[i]
    summary = summary[1:]
    return summary

def save_summary(filename, summary):
    f = open('summaries/' + filename + '_summarized.txt', 'w')
    f.writelines(summary)
    f.close()

def get_summary_from_article(filename, title):
    text = get_raw_text_from(filename)
    title = text.split('\n')[0]
    source = text.split('\n')[1]

    text = '\n'.join(text.split('\n')[3:])

    summary = get_summary(text)
    summary = title + '\n' + summary + '\n\n' + 'Source : ' + source
    save_summary(filename, summary)

    return summary

def get_links_from_main_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    clean_link_list = []
    for link in soup.find_all('a'):
        ref = link.get('href')
        if ref:
            if 'https://www.20minutes.fr/monde/' in ref and str(datetime.date.today().year) in ref:
                if not 'direct' in link.get('href'):
                    clean_link_list.append(link.get('href'))

    return clean_link_list[:nbr_articles]

def get_today_date():
    today = date.today()
    day = str(today.day)
    month = months[today.month - 1]
    year = str(today.year)

    return day, month, year

def get_short_today_date():
    now = datetime.datetime.now()
    today = str(now.strftime("%d/%m/%Y %H:%M:%S"))
    return today

def get_subject():
    day, month, year = get_today_date()
    subject = 'Your (short) daily news - ' + day + ' ' + month + ' ' + year
    return subject

def get_content(links):
    content = ''

    for link in links:
        title, filename = get_and_save_article(link)
        summary = get_summary_from_article(filename, title)
        content += summary + '\n\n------------------------------------------------------------------------\n\n'

    content = content[:-6]

    return content

def send_email(recipient_email_adress, subject, content):
    email_address = os.environ.get("GMAIL_ADRESS")
    email_password = os.environ.get("GMAIL_PASSWORD")

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = recipient_email_adress
    msg.set_content(content)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)
        logger.info(f'Email succesfully sent to {recipient_email_adress}!')

def get_recipient_email_adresses():
    with open('short_recipients.txt') as f:
        lines = f.readlines()
    recipient_email_adresses = [line[:-2] for line in lines]
    return recipient_email_adresses

def send_all_emails(subject, content):
    recipient_email_adresses = get_recipient_email_adresses()

    for recipient_email_adress in recipient_email_adresses:
        send_email(recipient_email_adress, subject, content)

def process():
    url = 'https://www.20minutes.fr/actu-generale'
    links = get_links_from_main_url(url)
    subject = get_subject()
    content = get_content(links)

    date = get_short_today_date()
    print('Running project on', date + '...')

    send_all_emails(subject, content)

    print('------------------------------------------------------------------------')

if __name__ == "__main__" :
    load_dotenv()

    months = ['Janvier', 'Février',
              'Mars', 'Avril',
              'Mai', 'Juin',
              'Juillet', 'Août',
              'Septembre', 'Octobre',
              'Novembre', 'Décembre'
             ]

    extraction_percentage = 0.6
    nbr_articles = 5

    process()