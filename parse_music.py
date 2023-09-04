import fitz
from PIL import Image
import pytesseract #Should be added to path
import re

from collections import defaultdict
import os
from dotenv import load_dotenv
import glob
from fpdf import FPDF #

import pandas as pd
from email.message import EmailMessage
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def split_list_into_chunks(members_list, k):
    n = len(members_list)
    if n <= k:
        return [[item] for item in members_list]  # Wrap each item in a separate list when its length is less than or equal to k

    chunk_size = n // k  # Determine the size of each chunk
    remainder = n % k  # Determine the remaining elements

    chunks = []
    start = 0

    for i in range(k-1, -1, -1):  # Iterate in reverse order
        chunk_length = chunk_size + 1 if i < remainder else chunk_size
        end = start + chunk_length
        chunks.append([item for item in members_list[start:end]])
        start = end

    return chunks

def update_instrument_dict(instrument_dict, instrument):
    if instrument in instrument_dict:
        # increase the count by 1
        instrument_dict[instrument] += 1
    else:
        # insert new entry with count equals 1
        instrument_dict[instrument] = 1
    return instrument_dict


def group_items(list1):
    grouped_strings = {}

    for string in list1:
        match = re.match(r'^(.*?)\s*\(\d\)', string)
        if match:
            group = match.group(1)
            if group in grouped_strings:
                grouped_strings[group].append(string)
            else:
                grouped_strings[group] = [string]

    return grouped_strings

def output_pdf():
    # Get the list of all files and directories
    path = f'{os.getcwd()}/data/new_output'
    print(path)

    dir_list = sorted(os.listdir(path))
    
    print(f'Files and directories in {path}:')
    
    # prints all files
    print(dir_list)
    grouped_instrument_files = group_items(dir_list)
    print(grouped_instrument_files)
    for key, value in grouped_instrument_files.items():
        instrument_type = key
        print(instrument_type)

        pdf = FPDF()
        # imagelist is the list with all image filenames you can create using os module by iterating all the files in a folder or by specifying their name
        for image in value:
            pdf.add_page()
            pdf.image(f'{os.getcwd()}/data/new_output/{image}',x=0,y=0,w=210,h=297) # for A4 size because some people said that every other page is blank
        pdf.output(f'{os.getcwd()}/data/pdf_output/{instrument_type}.pdf', 'F')

def parse_pdf(piece_name):
    # reset the instrument_dict
    instrument_dict = dict()

    input_file = piece_name
    song_title = res = input_file.rsplit('/', 1)[1][:-4]
    print(f'song_title = {song_title}')
    full_text = ''
    zoom = 1.5

    instruments = ['piccolo',
                'oboe',
                'flute',
                'bass clarinet',
                'alto clarinet',
                'clarinet',
                'cornet',
                'bassoon',
                'alto saxophone',
                'tenor saxophone',
                'baritone saxophone',
                'trumpet',
                'english horn',
                'horn',
                'trombone',
                'euphonium',
                #'snare drum',
                #'bass drum',
                'cymbals',
                'timpani',
                'mallet percussion',
                'percussion',
                'string bass',
                'trumpet',
                'trombone',
                'tuba',
                'english horn',
                'horn']

    print(input_file)
    with fitz.open(input_file) as pages:
        mat = fitz.Matrix(zoom, zoom)

        instrument_type = ''
        page_count = 0
        unknown_instrument_page_count = 0

        instrument_found = False
        for page in pages:
            pix = page.get_pixmap(matrix=mat)
            output = f'{os.getcwd()}/data/output/{page.number}.jpg'
            print(f'saving {page.number}.jpg')
            pix.save(output)
            
            page_text = str(pytesseract.image_to_string(Image.open(output)))
            page_text = page_text.strip().lower()
            if (song_title in page_text):
                print('start page')
                #print(page_text)
                instrument_type = ''
                page_count = 0

                # look for instrument match
                instrument_found = False
                for instrument in instruments:
                    if instrument in page_text:
                        print(f'found {instrument}')
                        # find match
                        instrument_type = instrument
                        instrument_found = True
                        page_count = 0
                        instrument_dict = update_instrument_dict(instrument_dict, instrument_type)
                        break
                    
                    #if instrument_found:
                    #    break
            else:
                page_count +=1
                
            # if no instrument found
            if instrument_found:
                instrument_type_count = instrument_dict[instrument_type]

                file_name=f'{os.getcwd()}/data/new_output/{instrument_type}_{instrument_type_count}({page_count}).jpg'
                print(f'parse_pdf save {file_name}')
                pix.save(file_name)
            else:
                unknown_instrument_page_count += 1
                file_name=f'{os.getcwd()}/data/new_output/unknown_{unknown_instrument_page_count}.jpg'
                print(f'parse_pdf save {file_name}')
                pix.save(file_name)
    return instrument_dict

def get_email_body(name):
    body = f'''
Hi {name},

Please see your attached music below. If there is a mistake, please notify me immediately.

Thank you,
Mr. Smith
    '''
    return body

#emails pdf to assigned person based on instrument and part
def email_pdf(instrument_dict, SHEET_ID, band_type, piece_name):
    song_title = piece_name.rsplit('/', 1)[1][:-4].replace('_',' ').title()
    email_sender = 'danielzh08@gmail.com'
    email_password = os.getenv('EMAIL_PASSWORD')
    email_subject = f'Your Music for {song_title} is Attached'
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
    
        #get sheetsheet info (instruments and emails for each chair)
        #https://docs.google.com/spreadsheets/d/1KCxl8vO--KpYwOJpU3ZnSqQUWUasGhoRD6mv9OXkjS8/edit#gid=0
        SHEET_NAME = band_type + '_band_sheet'
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
        df = pd.read_csv(url)
        
        ROSTER_SHEET_NAME = band_type + '_roster'
        roster_url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={ROSTER_SHEET_NAME}'
        roster_df = pd.read_csv(roster_url)
        print(instrument_dict)
        for index, row in df.iterrows():
            instrument = row['instrument']
            if not(pd.isnull(row['members'])):
                members_list = row['members'].split(',')
                print(members_list)
                print(instrument_dict)
                print(instrument_dict[instrument])
                members_list = split_list_into_chunks(members_list,instrument_dict[instrument])
                for part_index in range(len(members_list)):
                    for name in members_list[part_index]:
                        name = name.strip()
                        print(name)
                        email = roster_df.loc[roster_df['name'] == name, 'email'].iloc[0]
                        print(email)
                        pdfname = f'{instrument}{"_"}{part_index+1}{".pdf"}'
                        email_receiver = email

                        email_body = get_email_body(name)
                        em = MIMEMultipart()
                        em['From'] = email_sender
                        em['To'] = email_receiver
                        em['Subject'] = email_subject
                        em.attach(MIMEText(email_body, 'plain'))

                        # open the file in bynary
                        binary_pdf = open(f'{os.getcwd()}/data/pdf_output/' + pdfname, 'rb')

                        payload = MIMEBase('application', 'octate-stream', Name=pdfname)
                        payload.set_payload((binary_pdf).read())

                        # enconding the binary into base64
                        encoders.encode_base64(payload)

                        # add header with pdf name
                        payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
                        em.attach(payload)


                        smtp.sendmail(email_sender, email_receiver, em.as_string())
        smtp.quit()

def process(spreadsheet_id, band_type, piece_name):
    print(f"process() piece_name:{piece_name}")
    load_dotenv()

    instrument_dict = parse_pdf(piece_name)

    output_pdf()
    
    email_pdf(instrument_dict, spreadsheet_id, band_type, piece_name)