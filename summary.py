#gpt-3 max 4096 token
import os
import PyPDF2
import re
import openai
import time
import requests
from bs4 import BeautifulSoup

openai.api_key = 'your-api-key'
PERC_SUMMARY = 35 #the percentage you want to summarize your file/URL

LANGUAGE='italiano'


def read_pdf(pdf_file_path):
    pdf_summary_text = ""
    # Open the PDF file
    # Read the PDF file using PyPDF2
    pdf_file = open(pdf_file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # Loop through all the pages in the PDF file
    i = 0
    pagine = len(pdf_reader.pages)
    for page_num in range(pagine):
        # Extract the text from the page
        page_text = pdf_reader.pages[page_num].extract_text().lower()
        print(f"pagina {i}/{pagine}")
        
        while True:
            try:
                response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a helpful research assistant."},
                                    {"role": "user", "content": "riassumi di circa il {}% , in lingua: {} questo testo: {}. In piu metti dei titoli e metti in maiuscolo e grassetto le parole chiave".format(PERC_SUMMARY,LANGUAGE,page_text)},
                                        ],
                                            )
                page_summary = response["choices"][0]["message"]["content"]
                break
            except openai.error.RateLimitError:
                print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
                time.sleep(60)  # Aspetta per 60 secondi
        pdf_summary_text+=page_summary + "\n\n\n"
        pdf_summary_file = pdf_file_path.replace(os.path.splitext(pdf_file_path)[1], "_summary.txt")
        with open(pdf_summary_file, "w+") as file:
            file.write(pdf_summary_text)
        i+=1

    pdf_file.close()

def read_word(file):
    doc = Document(file)
    text = ''
    for para in doc.paragraphs:
        text += para.text
    return text    


def get_text_from_url(url):
    # Scarica l'HTML dalla URL

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Scarica l'HTML dalla URL con l'intestazione definita
    response = requests.get(url, headers=headers)

    # Controlla che la richiesta sia andata a buon fine
    print(response)
    if response.status_code != 200:
        return None

    # Crea un oggetto BeautifulSoup con l'HTML scaricato
    soup = BeautifulSoup(response.text, 'html.parser')

    # Estrai tutto il testo dall'HTML
    text = soup.get_text()

    print(text)
    return text

def chunk_text(text, chunk_size=4000):
    # Divide il testo in pezzi di circa chunk_size caratteri
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def summary_url(text):
    url_summary_text = ""
    chunks = chunk_text(text)
    for c in chunks:
        # Extract the text from the page      
        while True:
            try:
                response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a helpful research assistant."},
                                    {"role": "user", "content": "riassumi di circa il {}% , in lingua: {} questo testo: {}. In piu metti dei titoli e metti in maiuscolo e grassetto le parole chiave".format(PERC_SUMMARY,LANGUAGE,c)},
                                        ],
                                            )
                url_summary = response["choices"][0]["message"]["content"]
                break
            except openai.error.RateLimitError:
                print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
                time.sleep(60)  # Aspetta per 60 secondi
        url_summary_text+=url_summary + "\n\n\n"
        url_summary_file = "summary.txt"

        with open(url_summary_file, "w+") as file:
            file.write(url_summary_text)
if __name__=='__main__':
    pdf_file_path = "COPIA FINALE.pdf"
    selezione = input("Seleziona: \n1)PDF\n2)WORD\n3)URL\n\n")

    if selezione == '1':
        pdf_file_path = input("inserisci il path(percorso file) del PDF-----> ")
        read_pdf(pdf_file_path)
    elif selezione == '3':
        URL = input("inserisci l' URL da riassumere----> ").strip()
        text = get_text_from_url(URL)
        summary_url(text)
