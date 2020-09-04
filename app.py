from google.cloud import documentai_v1beta2 as documentai
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="myki.json"




class pdf_to_csv():
    
    def __init__(self, pdf):
        self.doc_in = pdf
        self.project_id='teak-span-275205'
        self.client = documentai.DocumentUnderstandingServiceClient()
        self.document = self.client.process_document(request=self.generate_request())
        self.tables = self.get_tables()
        self.max_cols = self.get_max_cols()
        self.table_indices = []
        
    
    def generate_request(self):
        
        # set google storage bucket source
        gcs_source = documentai.types.GcsSource(uri=self.doc_in)

        # app type: pdf
        # image/png is currently unsupported by Google Document AI API
        input_config = documentai.types.InputConfig(
            gcs_source=gcs_source, mime_type='application/pdf')


        # enable table extraction
        table_extraction_params = documentai.types.TableExtractionParams(
                enabled=True)


        # create a request

        parent = 'projects/{}/locations/us'.format(self.project_id)
        
        request = documentai.types.ProcessDocumentRequest(
            parent=parent,
            input_config=input_config,
            table_extraction_params=table_extraction_params
        )
        
        return request
    
    
    
    # retrieve table elements from document
    def get_tables(self):
        
        # enumerate tables 
        return ([table for page in self.document.pages for table in page.tables])
    

    
    # get max number of cilumns in table
    # this is used to define csv layout
    def get_max_cols(self):

        ## use number of header cells in each table to count the number of columns

        def get_cols(tab):

            cells = [cell.layout for row in tab.header_rows for cell in row.cells]
            return cells
        
        # find number of columns in each table
        table_lengths = [len(get_cols(x)) for x in self.tables]

        # use max value of number of columns
        return max(table_lengths)
    
    
    
    # given a starting and ending index, extraxt text from document.text object
    def txt_from_indx(self, start, end):
        
        # initialize empty string to store data
        response = ''
        
        # slice text between given indices
        response += self.document.text[start:end]
            
        # remove all whitespace and newlines using strip()
        response = response.strip()

        # preserve commas in csv by enclosing string in between double quotes ("")
        if "," in response:
            response = '"' + response + '"'
        
        return response
    

    
    def get_text(self, el, el_type="table"):
        """Convert text offset indexes into text snippets.
        
        el_type: keeps a track if the particular text segment is a table
        this is later used to process the non-table text segments as lines
        
        """
        response = ''
        el_start_indx = []
        
        # If a text segment spans several lines, it will
        # be stored in different text segments.       
        
        for segment in el.layout.text_anchor.text_segments:
            

            start_index = segment.start_index
            end_index = segment.end_index
            
            el_start_indx.append(start_index)
            
            # if element is table, store the indices
            if el_type == "table":
                 
                self.table_indices.extend(range(start_index,end_index))
                response = self.txt_from_indx(start_index,end_index)
                
            elif el_type == "line":
                
                # only use non-table indices
                if start_index not in self.table_indices:
                    response = self.txt_from_indx(start_index,end_index)
                    response = response + "\n"
                    
        # keep the smallest index to track the beginning of an element
        header_min = min(el_start_indx) if len(el_start_indx) != 0 else None
        
        return (header_min, response)
    
          
    
    
    def process_table(self, table):
        
        _max = self.max_cols
        csv_part = ""


        header_data = [self.get_text(cell) for row in table.header_rows for cell in row.cells]
        header = [x[1] for x in header_data]


        # keep smalles index to track the table position
        tbl_header_indx = min([x[0] for x in header_data])
        

        """
		if the particular table being processed has lesser number of columns than the largest table
		then normlaize the table by appending empty columns
        """

        if len(header) < _max:
            header.append(", " * (_max - len(header)))

        # append header to table data
        csv_part += ", ".join(header) + "\n"


        for row in table.body_rows:

            # extract each cell as a list
            row_txt = [self.get_text(cell)[1] for cell in row.cells]

            # append rows to csv string
            csv_part += ", ".join(row_txt) + "\n"

        return (tbl_header_indx, csv_part)
    
    
    def to_csv(self, out):
        
        # process all tables
        table_parts = [self.process_table(x) for x in self.tables]
        

        """
        convert table data to dictionary
        key: starting index of element
        value: table csv as a string
        """

        tbl_dict = {x[0]: x[1] for x in table_parts}
        
        # process lines i.e, non-table elements
        all_lines = [self.get_text(line, el_type="line") for page in self.document.pages for line in page.lines]

        # remove empty values
        all_lines = [x for x in all_lines if x[1] != ""]
        


		# normalize line data so that it follows the overall csv structure        
        lines = [(indx, line + ", " * (self.max_cols) )  for (indx, line) in all_lines]
        
        # convert line data to dictionary
        lines_dict = {x[0]: x[1] for x in all_lines}
        

        # merge the two dictionaries
        d = {**tbl_dict, **lines_dict}

        """
		sort the keys
		this is done to print the data in the same sequence as it appears in the original input file
        """
        keys = list(d.keys())
        keys.sort()
        
        # combine everything
        csv = "\n".join([d[indx] for indx in keys])
        
        # write out
        with open("output/" + out, "w") as f:
            f.write(csv)





if __name__ == "__main__":
    gs_url = 'gs://hgs-docai/input/'
    input_docs = ["1.pdf", "2.pdf", "3.pdf"]
    
    for file_name in input_docs:
        
        file_url = gs_url + file_name
        
        doc_obj = pdf_to_csv(file_url)
        
        out_file_name = file_name[:-3] + "csv"
        doc_obj.to_csv(out_file_name)
        print("csv exported for input file:", file_name)
