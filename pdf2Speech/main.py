import sys; sys.path.append('..')
import click
import os
import fitz
import re
from tqdm import tqdm
from threading import Thread
from utils import (getSentencesAndConvertToSpeech, process_page, get_last_page_processed,
                   getFilenameWithoutExtension, genderStringToGCloudGenderFormat,
                   calculateMoneySpent, AUDIO_DIR, TXT_DIR)

# GPT Model Type
GPT_MODEL_TYPE = "gpt-3.5-turbo"

@click.command()
@click.option('--pdf-path', type=click.Path(exists=True), required=True, help='Path to the input PDF file.')
@click.option('--voice-type', default="en-US-Studio-O", help='Type of voice for the speech.')
@click.option('--language', default="en-US", help='Language of the speech.')
@click.option('--gender', default='Female', help='Gender of the voice (Male or Female).')
@click.option('--page-start', default=0, help='Page to start processing from.')
@click.option('--page-end', default=-1, help='Page to end processing at.')
@click.option('--prompt-style', default='qa', help='Prompt Style, either "qa" or "conversational" for now.')

def pdf2Speech(pdf_path, voice_type, language, gender, page_start, page_end, prompt_style):
    """Convert a PDF to Speech."""
    # convert gender to proper format
    gender = genderStringToGCloudGenderFormat(gender)

    # get base filename
    base_filename = getFilenameWithoutExtension(pdf_path)
    
    # load the PDF
    doc = fitz.open(pdf_path)

    # loop initialization
    speech_thread = None
    section_title = "Preface"
    input_token_count = 0
    output_token_count = 0
    
    # initialize text variable
    # if the text file already exists, read from it
    if os.path.exists(f'{TXT_DIR}out_text_{base_filename}.txt'):
        with open(f'{TXT_DIR}out_text_{base_filename}.txt', 'r') as f:
            text = f.read()
    else:
        text = ""
    
    # specify page range to process
    if page_end != -1:
        page_range = range(page_start-1, page_end)
    else:
        page_range = range(page_start-1, len(doc))

    # Use tqdm to create a progress bar
    for page_index in tqdm(page_range, desc="Processing pages"):
        # only process the page if it hasn't been processed already
        if page_index > get_last_page_processed(base_filename):
            # Process each page of the PDF
            updated_text, section_title, num_input_tokens, num_output_tokens = process_page(page_index, doc, section_title, GPT_MODEL_TYPE)

            # If there's a previous speech thread, wait for it to finish
            if speech_thread and speech_thread.is_alive():
                speech_thread.join()
            
            # On another thread, convert the processed text to speech
            audio_file_name = base_filename if page_end == -1 else f'{base_filename}-[pg.{page_start}-{page_end}]'
            speech_thread = Thread(target=getSentencesAndConvertToSpeech, args=(updated_text, audio_file_name, voice_type, gender, language))
            speech_thread.start()

            # Add to the total number of input and output tokens
            input_token_count += num_input_tokens
            output_token_count += num_output_tokens

            # Add the updated text to the text variable
            text += updated_text

            # continously append text to a text file
            txt_filename = f'{TXT_DIR}out_text_{base_filename}.txt' if page_end == -1 else f'{TXT_DIR}out_text_{base_filename}-[pg.{page_start}-{page_end}].txt'
            with open(txt_filename, "a") as f:
                f.write(text)

    # Ensure the last speech thread finishes before exiting the function
    if speech_thread:
        speech_thread.join()
    
    # Print the number of input and output tokens
    print(f"Number of input tokens: {input_token_count}")
    print(f"Number of output tokens: {output_token_count}")
    print(f"Money spent: ${calculateMoneySpent(input_token_count, output_token_count,GPT_MODEL_TYPE):.2f}")

    click.echo(f"Converted {pdf_path} to audio and saved as {AUDIO_DIR}{base_filename}.mp3!")

if __name__ == "__main__":
    pdf2Speech()
