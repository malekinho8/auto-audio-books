import sys; sys.path.append('..')
import click
import os
from utils import (pdf2Image, convertImagesToText, getSentencesFromTextFile,
                   convertTextToSpeech, getFilenameWithoutExtension, genderStringToGCloudGenderFormat,
                   AUDIO_DIR,TXT_DIR,IMAGES_DIR)

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
    
    # PDF to Images
    image_files = pdf2Image(pdf_path)
    
    # Images to Text
    convertImagesToText(image_files, base_filename)
    
    # Get Sentences
    sentences = getSentencesFromTextFile(os.path.join(TXT_DIR, "out_text_"+base_filename+".txt"))
    
    # Text to Speech
    convertTextToSpeech(sentences, base_filename, voice_type, gender, language)

    click.echo(f"Converted {pdf_path} to audio and saved as {AUDIO_DIR}{base_filename}.mp3.")

if __name__ == "__main__":
    pdf2Speech()
