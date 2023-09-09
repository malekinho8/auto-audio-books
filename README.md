# Auto Audiobooks
Convert pdf to audiobooks 📚


**Inspiration** : 
I am a nerd 🤓. I like reading research papers, articles and books. I also travel alot often from my work city to my hometown. During which I tend to feel unwell on account of motion sickness, if I read while travelling. Have been looking for a tool but either some of them had paid implementation or restrictions. Also audiobooks are pretty cool to multitask on and keep them running in the background 🖖🏻

So inspiration was to use existing tech available and with ~20 lines of code, build a simple, pdf -> audiobook generator. 🤞🏻

## Implementation

Source code - [Auto Audio Book](https://github.com/bhavita/Auto-Audio-Books/blob/master/Auto_AudioBooks.ipynb)

Steps 

![steps](https://raw.githubusercontent.com/bhavita/Auto-Audio-Books/master/demo/Auto-Audiobook.png)

1. Research Paper - [Scientific Research Paper](https://github.com/bhavita/Auto-Audio-Books/blob/master/demo/Scientific%20Method%20Research.pdf)
 Generated audiobook -  [Generated Audio](https://github.com/bhavita/Auto-Audio-Books/blob/master/demo/Scientific%20Method%20Research.mp3?raw=true) 
3. Research Paper - [Research Paper](https://github.com/bhavita/Auto-Audio-Books/blob/master/demo/research-paper.pdf) 
Generated audiobook - [Generated Audio](https://github.com/bhavita/Auto-Audio-Books/blob/master/demo/research-paper.mp3?raw=true)

## Google Cloud Text-To-Speech Implementation for Higher Quality Audio Transcription

For the given code to run smoothly, users will have a few prerequisites and setup steps they need to follow before running the Google Cloud example script (`gcloud_api_AudioBooks.py`).

---

### Prerequisites and Setup for Text-to-Speech Synthesis:

#### 1. **Environment:**

- **Python**: Ensure you have Python installed. The code seems to be Python 3.x compatible, so a recent version of Python 3 would be best.

- **Virtual Environment (Optional but Recommended)**: It's recommended to run this in a virtual environment to avoid conflicts with other projects or system-wide packages.

  ```bash
  python3 -m venv myenv
  source myenv/bin/activate  # On Windows, use `myenv\Scripts\activate`
  ```

#### 2. **Google Cloud SDK and Project Setup**:

- **Google Cloud SDK**: Ensure you have the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and initialized.

- **Google Cloud Project**: Create a project on the [Google Cloud Console](https://console.cloud.google.com/).

- **Enable Text-to-Speech API**: Navigate to the [Text-to-Speech API page](https://console.cloud.google.com/marketplace/product/google/texttospeech.googleapis.com) and ensure the API is enabled for your project.

#### 3. **Authentication**:

- **Service Account**: Create a service account with roles that grant permissions to use the Text-to-Speech API. Download the JSON key for this service account.

- **Environment Variable**: Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the service account key:

  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
  ```

  This ensures the client library knows where to find your credentials.

#### 4. **Dependencies**:

- **Google Cloud Text-to-Speech Library**: Install the required library using pip:

  ```bash
  pip install --upgrade google-cloud-texttospeech
  ```

---

### Running the Code:

1. Activate your virtual environment if you set one up.
2. Run the provided script:

   ```bash
   python gcloud_api_AudioBooks.py
   ```

3. If successful, you'll find generated MP3 files with names like `output_0.mp3`, `output_1.mp3`, etc. in the current directory.

---

### Troubleshooting:

- If you encounter any `InvalidArgument` errors, the input might be too long or the voice might not be available. Consider shortening the text or choosing a different voice.

- Ensure your service account has the necessary permissions for the Text-to-Speech API.

- Check quota limits on the [Google Cloud Console](https://console.cloud.google.com/) if you're making a large number of requests.

---

## License
 
The MIT License (MIT)
Copyright (c) 2020 Bhavita Lalwani 

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
