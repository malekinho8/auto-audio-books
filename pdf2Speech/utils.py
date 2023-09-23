import pytesseract 
import os
import nltk
import re
import openai
import fitz
import tiktoken
from nltk.tokenize import sent_tokenize, word_tokenize
from PIL import Image 
from pdf2image import convert_from_path 
from google.cloud import texttospeech
from google.api_core.exceptions import InvalidArgument
from tqdm import tqdm

# set the openai api key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# donload nltk data
nltk.download('punkt')

# utility to create dir
def createDir(dirName):
  """Create a directory if it does not exist"""
  if not os.path.exists(dirName):
    os.makedirs(dirName)
    print("Directory " , dirName ,  " Created ")
  else:    
    print("Directory " , dirName ,  " already exists")

# utility to extract file name
def getFilenameWithoutExtension(file_path):
  """Extract filename without extension from a file path"""
  file_basename = os.path.basename(file_path)
  filename_without_extension = file_basename.split('.')[0]
  return filename_without_extension

# utility to get percentage of progress
def getPercentage(current, total):
  """Get percentage of progress"""
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
  """Convert a PDF to image snapshots of each page and return the filenames of the images"""
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
  """Convert images to text using OCR and return the filename of the text file"""
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

# Get sentences from raw text
def getSentencesFromRawText(text):
  """Get sentences from raw text"""
  sentences = sent_tokenize(text)
  # Filter out sentences that have fewer than 3 words
  sentences = [sentence.replace('\n',' ') for sentence in sentences if sentence.strip() in SECTION_TITLES or len(word_tokenize(sentence)) > 1]
  return sentences

# Get sentences from text file
def getSentencesFromTextFile(fn):
  """Get sentences from text file"""
  with open(fn, 'r') as file:
      text = file.read().replace('\n\n','. ')  # Replace newline characters with spaces
      sentences = getSentencesFromRawText(text)
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
  """Convert text to speech using google cloud api"""
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
  f = open(outfile, "ab")
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

def query_gpt(prompt, instructions, gpt_model_type, max_tokens=1000, temperature=1):
  COMPLETIONS_API_PARAMS = {
      "temperature": temperature,
      "max_tokens": max_tokens,
      "model": gpt_model_type,
  }
  
  response = openai.ChatCompletion.create(
      messages = [{"role": "user", "content": prompt}, {"role": "system", "content": instructions}],
      **COMPLETIONS_API_PARAMS
  )
  return response['choices'][0]['message']['content']

def process_page(page_index, pdf_file, previous_section, gpt_model_type, prompt_style):
    page = pdf_file[page_index]
    page_text = page.get_text()
    prompt_start = f"TEXT: \n\n{page_text}"
    if prompt_style == 'qa':
      prompt_instructions = "Please use hypophora and anthypophora style of prose to convey your understanding of the passage. Your output should follow a call and reponse style of prose. For example: Why do we use this technique? Because it grabs the reader's attention."
    elif prompt_style == 'conversational':
      prompt_instructions = "Please use conversational style of prose to convey your understanding of the passage."

    num_input_tokens = len(tiktoken.encoding_for_model(gpt_model_type).encode(prompt_start + prompt_instructions))
    if num_input_tokens > 3000:
      prompt_start = prompt_start[:3000]
      num_input_tokens = 3000
    reference_rating = query_gpt(prompt_start, "Give a confidence rating on a scale of 0 to 100 if you think this is a References section of a paper. Only respond with a number.", gpt_model_type, max_tokens = 5)
    if int(reference_rating) <= 90 or page_index <= 0.7 * len(pdf_file):
      gpt_out = query_gpt(prompt_start, prompt_instructions, gpt_model_type)
      section_title = query_gpt(prompt_start, "What would be a good section title for this passage?", gpt_model_type)
      updated_text = f'Page {page_index}, Continuing from Section {previous_section}, and beginning section {section_title}: \n\n{gpt_out}\n\n'
      num_output_tokens = len(tiktoken.encoding_for_model(gpt_model_type).encode(gpt_out)) + len(tiktoken.encoding_for_model(gpt_model_type).encode(section_title))
      num_input_tokens = 2 * num_input_tokens
    else : 
      section_title = "References"
      updated_text = "Please see the paper to inspect the references."
      num_output_tokens = 5
    return updated_text, section_title, num_input_tokens, num_output_tokens
  
def get_last_page_processed(base_filename):
  """Get the last page of the PDF that was processed."""
  if os.path.exists(f'{TXT_DIR}out_text_{base_filename}.txt'):
    with open(f'{TXT_DIR}out_text_{base_filename}.txt', 'r') as f:
      text = f.read()
      if text:
        # use regex to find pattern of r"Page X, ", and extract X as an integer
        last_page_processed = int(re.findall(r"Page (\d+), ", text)[-1])
      else:
        last_page_processed = 0
  else:
    last_page_processed = 0
  return last_page_processed

def reformulate_pdf(pdf_path, gpt_model_type='gpt-3.5-turbo', max_tokens=1000, temperature=1):
  pdf_file = fitz.open(pdf_path)
  text = ""
  previous_section = "Pre-Abstract"
  input_token_count = 0
  output_token_count = 0

  for page_index in range(len(pdf_file)):
    updated_text, new_section, num_input, num_output = process_page(page_index, pdf_file, previous_section, gpt_model_type)
    text += updated_text
    input_token_count += num_input
    output_token_count += num_output
    previous_section = new_section

  encoding = tiktoken.encoding_for_model(gpt_model_type)
  tokens = encoding.encode(text)
  return text, len(tokens), input_token_count, output_token_count

def getSentencesAndConvertToSpeech(text_from_page, base_filename, voice_type, gender, language):
  # This assumes you have a function to split text into sentences. 
  sentences = getSentencesFromRawText(text_from_page)
  # Text to Speech
  convertTextToSpeech(sentences, base_filename, voice_type, gender, language)

# calculate the amount of money spent by defining a function
def calculateMoneySpent(input_token_count, output_token_count, gpt_model_type):
  """Calculate the amount of money spent. Updated as of September 2023. Pricing data from https://openai.com/pricing/"""
  # define the cost per token
  if gpt_model_type == 'gpt-3.5-turbo':
    cost_per_input_token = 0.0015/1000
    cost_per_output_token = 0.002/1000
  else:
    raise NotImplementedError("Only gpt-3.5-turbo is supported at this time")

  # calculate the cost
  cost = input_token_count * cost_per_input_token + output_token_count * cost_per_output_token
  return cost