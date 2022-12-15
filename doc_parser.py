import urllib.request
import fitz
import os
import pytesseract
import cv2
import io
from PIL import Image, ImageEnhance
import layoutparser as lp
import numpy as np
from deskew import determine_skew
from epub_conversion.utils import open_book, convert_epub_to_lines
from bs4 import BeautifulSoup
import time

os.system('export TESSDATA_PREFIX=/fsx/marianna/books/tessdata')
os.system('export PATH=$PATH:TESSDATA_PREFIX')


def process_epubs(filename, output_dir):

    book = open_book(filename)
    lines = convert_epub_to_lines(book)
    lines = [BeautifulSoup(line, 'html.parser').text for line in lines]
    text = ' '.join(lines)
    txt_name = filename.split('.pdf')[0]+'.txt'
    txt_name = txt_name.split('/')[-1]
    txt_name = f'{output_dir}/{txt_name}'
    with open(txt_name, 'w', encoding='utf-8') as f:
        f.write(text) 

def deskew(grayscale):
    angle = determine_skew(grayscale)
    rotated = rotate(grayscale, angle, resize=True) * 255
    return rotated.astype(np.uint8)

def download_file(url, output_dir):
    filename = url.split('/')[-1]
    ext = filename.split('.')[-1]
    if ext==filename: 
      filename += '.djvu'
    filename = filename.replace('.noimages', '').replace('.images', '').replace(':', '_')
    filename = output_dir+'/'+filename
    urllib.request.urlretrieve(url, filename)
    return filename

def read_pdf(doc_path:str, output_dir:str, langs:list, model) -> str:
    langs = '+'.join(langs)
    txt_name = doc_path.split('.pdf')[0]+'.txt'
    txt_name = txt_name.split('/')[-1]
    txt_name = f'{output_dir}/{txt_name}'
    pdf_layout = lp.load_pdf(doc_path)
    text = ' '.join([' '.join(lp.get_texts()) for lp in pdf_layout])
    text_list = []
    if len(text.replace(' ', ''))==0:
      doc = fitz.open(doc_path)
      for i in range(doc.page_count):
        page = doc.load_page(i)
        pix = page.get_pixmap()
        pix = cv2.imdecode(np.frombuffer(pix.tobytes('png'), np.uint8), -1)
        pix = cv2.resize(pix,None,fx=2,fy=2)
        layout = model.detect(pix[..., ::-1])
        text_blocks = lp.Layout([b for b in layout if b.type=='Text'])
        for block in text_blocks:
            segment_image = (block
                                # .pad(left=5, right=5, top=5, bottom=5)
                                .crop_image(pix))
            text = pytesseract.image_to_string(segment_image, lang=langs, config='--psm 6')
            text_list.append(text)
        text = '\n'.join(text_list)
    os.remove(doc_path)
    with open(txt_name, 'w', encoding='utf-8') as f:
      f.write(text) 

def doc_parser_tool(
    filename:str, 
    output_dir:str,
    pdf_dir: str,
    langs:list,
    model
    ):

    if 'https://' in filename:
        filename = download_file(filename, pdf_dir)

    if '.pdf' in filename:
        pdf_filename = filename
        read_pdf(pdf_filename, output_dir, model=model, langs=langs)
    elif '.epub' in filename:
        try:
            process_epubs(filename, output_dir)
        except:
            pdf_filename = filename+'.pdf'
            os.system(f'ebook-convert {filename} {pdf_filename} >/dev/null')
            read_pdf(pdf_filename, output_dir, model=model, langs=langs)
    elif '.djvu' in filename:
        pdf_filename = filename+'.pdf'
        os.system(f'ddjvu -v --format=pdf {filename} {pdf_filename} >/dev/null')
        read_pdf(pdf_filename, output_dir, model=model, langs=langs)
    

