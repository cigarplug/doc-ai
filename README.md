DESCRIPTION

This program reads pdf invoices that are saved on my GCP Storage and converts them to CSV files using Google Document AI.



USAGE

In the root directory, execute

$ python app.py


A copy of the sample pdf files is also available in the 'input' directory.
After executing this program, the processed CSV files will be stored in the 'output' directory.

The 'demo' directory contains a side-by-side comparison of the input pdf files and generated CSV files.



NOTES

-	The application uses my personal GCP credentials, which are included in this zip file.
	
	Since that isn't a particularly safe way of shipping API keys, I have set the key to automatically expire on
	Monday Sept 7, 2020 12:00 AM AEST


-	The Document AI API fails to identify some table-like structures as an actual 'table'. In such cases, I have treated 	 these sections as plain text lines.
	

-	Given the time constraint, I have not attempted to imitate the document structure along the horizontal axis.
	As such, sections of lines/paragraphs that appear side-by-side in the pdf are written one-below-the-other in exported CSV. 
	
	It should be however possible to imitate the original structure using bounding polygon parameters.
