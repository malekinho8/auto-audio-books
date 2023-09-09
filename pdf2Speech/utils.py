import pytesseract 
import os
import nltk
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from PIL import Image 
from pdf2image import convert_from_path 
from google.cloud import texttospeech
from google.api_core.exceptions import InvalidArgument
from tqdm import tqdm

# donload nltk data
nltk.download('punkt')

# utility to create dir
def createDir(dirName):
  if not os.path.exists(dirName):
    os.makedirs(dirName)
    print("Directory " , dirName ,  " Created ")
  else:    
    print("Directory " , dirName ,  " already exists")

# utility to extract file name
def getFilenameWithoutExtension(file_path):
    file_basename = os.path.basename(file_path)
    filename_without_extension = file_basename.split('.')[0]
    return filename_without_extension

# utility to get percentage of progress
def getPercentage(current, total):
    return (current / total) * 100

# constants
IMAGES_DIR = "./content/Images/"
AUDIO_DIR = "./content/Audio/"
TXT_DIR = "./content/Text/"
createDir(IMAGES_DIR)
createDir(AUDIO_DIR)
createDir(TXT_DIR)

SECTION_TITLES = [
    "Abstract",
    "Introduction",
    "Background",
    "Literature Review",
    "Methods",
    "Methodology",
    "Results",
    "Discussion",
    "Findings",
    "Analysis",
    "Conclusion",
    "Conclusions",
    "Recommendations",
    "Acknowledgements",
    "Acknowledgments",
    "References",
    "Bibliography",
    "Appendix",
    "Future Work",
    "Limitations",
    "Scope",
    "Objectives",
    "Definitions",
    "Terminology",
    "Assumptions",
    "Summary",
    "Data Collection",
    "Experimentation",
    "Validation",
    "Observations"
]

# Convert a PDF to image snapshots
def pdf2Image(fn):
  file = getFilenameWithoutExtension(fn)
  image_fn_dir= IMAGES_DIR + file
  createDir(image_fn_dir)
  print(fn);
  pages = convert_from_path(fn, 500)
  print(pages)
  filenames = [];
  
  # Counter to store images of each page of PDF to image 
  image_counter = 1
  total = len(pages)

  # Iterate through all the pages stored above 
  for page in tqdm(pages, desc='Converting PDF to Images'): 
    
      # Declaring filename for each page of PDF as JPG 
      # For each page, filename will be: 
      # PDF page 1 -> page_1.jpg 
      # PDF page 2 -> page_2.jpg 
      # PDF page 3 -> page_3.jpg 
      # .... 
      # PDF page n -> page_n.jpg 
      filename = image_fn_dir+ "/page_"+str(image_counter)+".jpg"
      filenames.append(filename);

      # check if the file has already been created
      if os.path.exists(filename):
        image_counter = image_counter + 1
        continue

      # Save the image of the page in system 
      page.save(filename, 'JPEG') 
      å
      # Increment the counter to update filename 
      image_counter = image_counter + 1
      
  return filenames

# Convert images to text using OCR
def convertImagesToText(filenames, ofilename):
  # Creating a text file to write the output 
  outfile = os.path.join(TXT_DIR, "out_text_"+ofilename+".txt")

  if os.path.exists(outfile):
    print(f'{outfile} already exists. Skipping...')
    return outfile
  else:
    # Open the file in append mode so that  
    # All contents of all images are added to the same file 
    f = open(outfile, "a")
    for file in tqdm(filenames, desc='Converting Images to Text'):
        print(file)
        text = str(((pytesseract.image_to_string(Image.open(file)))))
        text = text.replace('-\n', '')     
        text = text + '\n'
        f.write(text)
    f.close()
    return outfile

# Get sentences from text file
def getSentencesFromTextFile(fn):
  with open(fn, 'r') as file:
      text = file.read().replace('\n\n','. ')  # Replace newline characters with spaces
      sentences = sent_tokenize(text)
      # Filter out sentences that have fewer than 3 words
      sentences = [sentence.replace('\n',' ') for sentence in sentences if sentence.strip() in SECTION_TITLES or len(word_tokenize(sentence)) > 1]

  return sentences

# define utility for converting to proper gender format
def genderStringToGCloudGenderFormat(genderString):
  if genderString == 'Male':
    gender = texttospeech.SsmlVoiceGender.MALE
  else:
    gender = texttospeech.SsmlVoiceGender.FEMALE
  return gender

# convert text to speech using google cloud api
def convertTextToSpeech(sentences, ofilename, voice_name="en-US-Studio-O", voice_gender=texttospeech.SsmlVoiceGender.FEMALE, language_code="en-US", audio_encoding=texttospeech.AudioEncoding.MP3):  
  # Instantiates a client
  client = texttospeech.TextToSpeechClient()
  
  # Select audio params
  voice = texttospeech.VoiceSelectionParams(
    language_code=language_code, ssml_gender=voice_gender, name=voice_name
  )

  # Select the type of audio file you want returned
  audio_config = texttospeech.AudioConfig(
    audio_encoding=audio_encoding
  )

  # specify the outfile for continuous audio writing
  outfile = AUDIO_DIR + ofilename + ".mp3"

  # Open the file in append mode so that
  # All contents of all sentence are added to the same file
  f = open(outfile, "wb")
  for idx, sentence in enumerate(tqdm(sentences, desc='Converting Text to Speech')):
    synthesis_input = texttospeech.SynthesisInput(text=sentence)
    try:
      response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
      f.write(response.audio_content)
    except InvalidArgument as e:
      if "Input size limit exceeded for Studio Voice" in e.message:
        # split the sentence using re to find a ", [letter]" pattern and split at that comma
        # this is to avoid the InvalidArgument error
        sentence_parts = re.split(r', [a-zA-Z]', sentence)
        for temp_idx, sentence_part in enumerate(sentence_parts):
          synthesis_input = texttospeech.SynthesisInput(text=sentence)
          response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
          f.write(response.audio_content)
      else:
        raise e
  f.close()
  print(outfile + " prepared :) ")