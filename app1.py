import gradio as gr
import PyPDF2
import os
import openai
import re
import plotly.graph_objects as go
from openai import AzureOpenAI
import os
import openai

class ResumeAnalyser:
  """A class for analyzing resumes and job descriptions."""
  def __init__(self):
      """Initialize the ResumeAnalyser."""
      openai.api_type = "........."
      openai.api_base = "....................."
      openai.api_version = "...................."
      openai.api_key = '............................'
      self.client = AzureOpenAI()
  def extract_text_from_file(self,file_path):
      """Extract text content from a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The extracted text content.
      """
      # Get the file extension
      file_extension = os.path.splitext(file_path)[1]
      if file_extension == '.pdf':
          with open(file_path, 'rb') as file:
              # Create a PDF file reader object
              reader = PyPDF2.PdfFileReader(file)

              # Create an empty string to hold the extracted text
              extracted_text = ""

              # Loop through each page in the PDF and extract the text
              for page_number in range(reader.getNumPages()):
                  page = reader.getPage(page_number)
                  extracted_text += page.extractText()
          return extracted_text

      elif file_extension == '.txt':
          with open(file_path, 'r') as file:
              # Just read the entire contents of the text file
              return file.read()

      else:
          return "Unsupported file type"

  def responce_from_ai(self,textjd, textcv):
      """Generate response from OpenAI based on job description and resume.

        Args:
            textjd (str): Text content of the job description.
            textcv (str): Text content of the resume.

        Returns:
            str: Generated text response.
      """
      job_description = self.extract_text_from_file(textjd)
      resume = self.extract_text_from_file(textcv)

      conversation = [
          {"role": "system", "content": "You are a Reason Analyser"},
          {"role": "user", "content": f"""
  Given the job description and the resume, access the matching percentage to 100 and if 100 percentage not matched mention the remaining percentage with reason.if doesn't match return 0. **Job Description:**{job_description}**Resume:**{resume}
  **Detailed Analysis:**
                  the result should be in this format:
                  Matched Percentage: [matching percentage].
                  Reason            : [give me a Reason (shortly in passage) and keys from job_description and resume get this matched percentage.].
                  Skills To Improve : [give me a the skills How to improve and get 100 percentage job description matching (shortly in passage).].
                  Keywords          : [give me a matched key words from {job_description} and {resume}].
                  """}
      ]
      response = self.client.chat.completions.create(
          model="ChatGPT",
          messages=conversation,
          temperature=0,
          max_tokens=500,
          n=1,
          stop=None,
      )
      generated_text = response.choices[0].message.content
      print(generated_text)
      return generated_text


  def matching_percentage(self,job_description_path, resume_path):
      """Calculate matching percentage between job description and resume.

        Args:
            job_description_path (str): Path to the job description file.
            resume_path (str): Path to the resume file.

        Returns:
            tuple: A tuple containing matched percentage, reason, skills to improve,
                   keywords, and a Plotly graph object.
      """
      job_description_path = job_description_path.name
      resume_path = resume_path.name

      generated_text = self.responce_from_ai(job_description_path, resume_path)

      result = generated_text

      lines = result.split('\n')

      matched_percentage = 0
      matched_percentage_txt = None
      reason = None
      skills_to_improve = None
      keywords = None

      for line in lines:
          if line.startswith('Matched Percentage:'):
              matched_percentage = re.search(r'\d+', line)
              if matched_percentage:
                  matched_percentage = int(matched_percentage.group())
                  matched_percentage_txt = (f"Matched Percentage: {matched_percentage}%")
          elif line.startswith('Reason'):
              reason = line.split(':')[1].strip()
              print(reason)
          elif line.startswith('Skills To Improve'):
              skills_to_improve = line.split(':')[1].strip()
              print(skills_to_improve)
          elif line.startswith('Keywords'):
              keywords = line.split(':')[1].strip()


      # Extract the matched percentage using regular expression
      # match1 = re.search(r"Matched Percentage: (\d+)%", matched_percentage)
      # matched_Percentage = int(match1.group(1))

      # Creating a pie chart with plotly
      labels = ['Matched', 'Remaining']
      values = [matched_percentage, 100 - matched_percentage]

      fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
      # fig.update_layout(title='Matched Percentage')


      return matched_percentage_txt,reason, skills_to_improve, keywords,fig

  def filename(self,uploadbutton):
      """Get the filename from an upload button.

        Args:
            uploadbutton: The upload button object.

        Returns:
            str: The filename.
      """
      return uploadbutton.name

  def gradio_interface(self):
      """Create and launch the Gradio interface."""
      with gr.Blocks(css="style.css",theme="freddyaboulton/test-blue") as app:
            with gr.Row():
                gr.HTML("""<center class="darkblue" text-align:center;padding:30px;'><center>
                <br><center><h1 style="color:#fff">Resume Analyser</h1></center>""")
            with gr.Row():
              with gr.Column(scale=0.45, min_width=150, ):
                file_jd = gr.File()
                jobDescription = gr.UploadButton(
                    "Browse File",file_types=[".txt", ".pdf", ".doc", ".docx",".json",".csv"],
                    elem_classes="filenameshow")
              with gr.Column(scale=0.45, min_width=150):
                file_resume = gr.File()
                resume = gr.UploadButton(
                    "Browse File",file_types=[".txt", ".pdf", ".doc", ".docx",".json",".csv"],
                    elem_classes="filenameshow")
              with gr.Column(scale=0.10, min_width=150):
                analyse = gr.Button("Analyse")
            with gr.Row():
              with gr.Column(scale=1.0, min_width=150):
                perncentage = gr.Textbox(label="Matching Percentage",lines=8)
              with gr.Column(scale=1.0, min_width=150):
                reason = gr.Textbox(label="Matching Reason",lines=8)
              with gr.Column(scale=1.0, min_width=150):
                skills = gr.Textbox(label="Skills To Improve",lines=8)
              with gr.Column(scale=1.0, min_width=150):
                keywords = gr.Textbox(label="Matched Keywords",lines=8)
            with gr.Row():
              with gr.Column(scale=1.0, min_width=150):
                pychart = gr.Plot(label="Matching Percentage Chart")
            jobDescription.upload(self.filename,jobDescription,file_jd)
            resume.upload(self.filename,resume,file_resume)
            analyse.click(self.matching_percentage, [jobDescription, resume], [perncentage,reason,skills,keywords,pychart])

      app.launch()

resume=ResumeAnalyser()
resume.gradio_interface()
