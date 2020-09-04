DESCRIPTION

This program reads pdf invoices that are saved on my GCP Storage and converts them to CSV files using Google Document AI.



USAGE

In the root directory, execute

`$ python app.py`


A copy of the sample pdf files is also available in the 'input' directory.
After executing this program, the processed CSV files will be stored in the 'output' directory.

The 'demo' directory contains a side-by-side comparison of the input pdf files and generated CSV files.



NOTES

-	To use this program, you must create a GCP service account (with access to Document AI API) and store the credentials file as myki.json in the application root directory


-	The Document AI API fails to identify some table-like structures as an actual 'table'. In such cases, I have treated these sections as plain text lines.
	

-	At this moment,  I have not attempted to replicate the document structure along the horizontal axis. As such, sections of lines/paragraphs that appear side-by-side in the pdf are written one-below-the-other in exported CSV. It should be however possible to imitate the original structure using bounding polygon parameters.
