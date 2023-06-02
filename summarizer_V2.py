import os
import openai
import pdfplumber
from time import time,sleep
import textwrap
import re
import glob
import PyPDF2

def open_file(filepath):
    with open(filepath,'r', encoding='utf-8') as infile:
        return infile.read()
        
def save_file(filepath,content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)
        
        

def convert_pdf2txt(src_dir,dest_dir):
    files = os.listdir(src_dir)
    files = [i for i in files if '.pdf' in i]
    
    for file in files:
        try:
            with pdfplumber.open(src_dir+file) as pdf:
                output = ''
                for page in pdf.pages:
                    output += page.extract_text()
                    output += '\n\nNEW PAGE\n\n' #cambia con la tua page demarcation
                save_file(dest_dir+file.replace('.pdf','.txt'), output.strip())
        except Exception as e:
            print(e,file)

openai.api_key = 'your-api-key'

#questa func usa curie-001 per summarizare (meno costosa)
def gpt_3(prompt):
    response = openai.Completion.create(
        model="text-curie-001",
        prompt=prompt,
        temperature=0,
        max_tokens=700,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    text = response['choices'][0]['text'].strip()
    return text
    
#questo usa davinci che e' piu' accurato
def gpt_31(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=700,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    text = response['choices'][0]['text'].strip()
    return text
    
def gpt_32(chunk):
    while true:
        try:
            response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful research assistant."},
                                {"role": "user", "content": f"Scrivi un riassunto conciso e in italiano del seguente: {chunk}"},
                                    ],
                                        )
            text = response['choices'][0]['message']["content"]
        except Exception as e:
            print(e)
            time.sleep(35)
    return text
    
def read_pdf(pdf_file_path):
    pdf_text = ""
    # Open the PDF file
    # Read the PDF file using PyPDF2
    pdf_file = open(pdf_file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # Loop through all the pages in the PDF file
    pagine = len(pdf_reader.pages)
    for page_num in range(pagine):
        try:
            testo_tmp = ""
            # Extract the text from the page
            page_text = pdf_reader.pages[page_num].extract_text().lower()
            pdf_text += page_text
        except Exception as e:
            print(e)
            
    return pdf_text

if __name__ == '__main__':
    #chiama la pdf converter function
    try:
        #convert_pdf2txt('PDFs/','textPDF/')
        
        alltext = read_pdf('C:/Users/jakyd/Desktop/OneDrive/Desktop/gpt-summarizer-main/PDFs/Che stile... di vita - Ricciardi Jole.pdf')
        
        #la nostra path_folder
        #pathfolder = 'C:/sers/jakyd/Desktop/OneDrive/Desktop/gpt-summarizer-main/textPDF'
        
        #prendi una lista dei file di testo creati dai pdf
        #files = glob.glob(f"{pathfolder}/*.txt")
        #print(files)
        
        #alltext = ""
        
        # for file in files:
            # with open(file, 'r', encoding='utf-8') as infile: #apri er file
                # alltext += infile.read()
        
        chunks = textwrap.wrap(alltext,3000)
        result = list()
        count = 0
        
        
        with open('pdfsummary.txt', 'w', encoding='utf-8') as f:
            f.write("SUMMARY STARTS HERE\n\n\n\n\n")
        #scrivi er riassunto
        for chunk in chunks:
            try:
                count = count + 1
                prompt = open_file('promptitaliano.txt').replace('<<SUMMARY>>', chunk)
                prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
                
                #se si chiama qualche altro modello sostituire chunk con prompt
                summary = gpt_32(chunk)
                print('\n\n\n', count, 'out of', len(chunks), 'Compressions', ' : ', summary)
                summary = '\n'+ str(count) + '/' + str(len(chunks)) + '  parte' + '\n' + summary
                result.append(summary)
                save_file("pdfsummary.txt", '\n\n'.join(result))
            except Exception as e:
                print(e)
        
        with open("pdfsummary.txt", 'r', encoding='utf-8') as infile:
            summary = infile.read()
            chunks=textwrap.wrap(summary,3000)
    except Exception as e:
        print(e)
        
    ##inizializza una lista vuota
    # result = []
    # result2 = []
    
    
    ##scrivi delle note dai chunks
    # for i, chunk in enumerate(chunks):
        # with open("prompt2.txt", 'r', encoding='utf-8') as infile:
            # prompt= infile.read()
            
        # prompt = prompt.replace("<<NOTES>>",chunk)
        
        # notes = gpt_3(prompt)
        
        
        ##write a summary from the notes
        # keytw = open_file('prompt6.txt').replace('<<NOTES>>',chunk)
        # keytw2 = gpt_31(keytw)
        
        # print(f"\n\n\n{i+1} out of {len(chunks)} Compression: {notes}")
        
        # result.append(notes)
        # result2.append(keytw2)
        
    ##salva i risultati su un file
    # with open("notes.txt", "w", encoding='utf-8') as outfile:
        # outfile.write("\n\n".join(result))
        
    # with open("notessum.txt", "w", encoding='utf-8') as outfile:
        # outfile.write("\n\n".join(result2))
        
    # sumnotes = open_file("notessum.txt")
    
    
    ##scrimi una step byt step guide dalle note
    # keytw = open_file("prompt3.txt").replace('<<NOTES>>',sumnotes)
    # keytw2 = gpt_31(keytw)
    # print(keytw2)
    # save_file("steps.txt",keytw2)
    
    
    
    ##write essencial info
    # essencial1 = open_file('prompt4.txt').replace("<<NOTES>>",sumnotes)
    # essencial2 = gpt_31(essencial1)
    # print(essencial2)
    # save_file("essencial.txt",essencial2)
    

    
    ##write a blog post
    # blogpost = open_file('essencial.txt')
    # blogpostw = open_file('prompt5.txt').replace("<<NOTES>>",blogpost)
    # blogpostw2 = gpt_31(blogpostw)
    # print(blogpostw2)
    # save_file("blogpost.txt",blogpostw2)
    

    ##write a visual prompt
    # midj = open_file("essencial.txt")
    # mjv4 = open_file('mjv4prompts.txt').replace('<<SCENE>>',midj)
    # desc = gpt_31(mjv4)
    # print('\n\n', desc)
    # save_file("midprompts.txt", desc)
    
    
    
    
    
    
    
        

    
    
    
        
         
    
    
    
    
        
