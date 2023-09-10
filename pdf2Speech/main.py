import sys; sys.path.append('..')
import click
import fitz
from tqdm import tqdm
from threading import Thread
from utils import (getSentencesAndConvertToSpeech, process_page,
                   getFilenameWithoutExtension, genderStringToGCloudGenderFormat,
                   calculateMoneySpent, AUDIO_DIR, TXT_DIR)

# GPT Model Type
GPT_MODEL_TYPE = "gpt-3.5-turbo"

@click.command()
@click.option('--pdf-path', type=click.Path(exists=True), required=True, help='Path to the input PDF file.')
@click.option('--voice-type', default="en-US-Studio-O", help='Type of voice for the speech.')
@click.option('--language', default="en-US", help='Language of the speech.')
@click.option('--gender', default='Female', help='Gender of the voice (Male or Female).')

def pdf2Speech(pdf_path, voice_type, language, gender):
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
    text = ""

    # Use tqdm to create a progress bar
    for page_index in tqdm(range(len(doc)), desc="Processing pages"):
        # Process each page of the PDF
        updated_text, section_title, num_input_tokens, num_output_tokens = process_page(page_index, doc, section_title, GPT_MODEL_TYPE)

        # If there's a previous speech thread, wait for it to finish
        if speech_thread and speech_thread.is_alive():
            speech_thread.join()
        
        # On another thread, convert the processed text to speech
        speech_thread = Thread(target=getSentencesAndConvertToSpeech, args=(updated_text, base_filename, voice_type, gender, language))
        speech_thread.start()

        # Add to the total number of input and output tokens
        input_token_count += num_input_tokens
        output_token_count += num_output_tokens

        # Add the updated text to the text variable
        text += updated_text

    # Ensure the last speech thread finishes before exiting the function
    if speech_thread:
        speech_thread.join()

    # Save the text to a file
    with open(f"{TXT_DIR}out_text_{base_filename}.txt", "w") as f:
        f.write(text)
    
    # Print the number of input and output tokens
    print(f"Number of input tokens: {input_token_count}")
    print(f"Number of output tokens: {output_token_count}")
    print(f"Money spent: ${calculateMoneySpent(input_token_count, output_token_count,GPT_MODEL_TYPE):.2f}")

    click.echo(f"Converted {pdf_path} to audio and saved as {AUDIO_DIR}{base_filename}.mp3!")

if __name__ == "__main__":
    pdf2Speech()
