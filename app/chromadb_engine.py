import chromadb
import pandas as pd
from pypdf import PdfReader
import docx2txt

#load persistent dir
client = chromadb.PersistentClient(path="chromadbs")

# generic funcs

def split_texts(input_str: str, split_length: int = 128) -> list[str]:
    """
    takes a text input and splits it into a list of strings of 128 words (or less for the last entry if it doesn't make it up to 128 words)

    inputs:
        - input_str: str - candidate string to split
        - split_length: int - number of words per split

    outputs:
        - splitlist: list[str] - list of split strings generated from inputs, which each string being split_length number of words
    """
    wordlist = input_str.split(' ')
    splitlist = [' '.join(wordlist[i:i+split_length]) for i in range(0, len(wordlist), split_length)]
    return splitlist

### FUNCS FOR IMPORTING AND STUFF

def switch_db(db_name: str):
    """
    abstracting function to switch collections, but I've called them dbs because silly me.

    unsure how necessary it is.

    inputs:
        - db_name: str - name of db to connect to
    outputs:
        - collection - connection to ChromaDB client collection (should it exist
    """
    collection = client.get_collection(name=db_name)
    return collection

def make_db_from_pdf(pdf_dir: str, db_name: str, split_length: int = 128, ):
    """
    function which creates a db from pdf.

    inputs:
        - pdf_dir: str - directory where pdf can be read from (NOTE: probably needs to be refactored to allow for arbitrary dir strings????? or maybe I'll do that with a drag-drop functionality which returns the string based on OS???????) not sure
        - db_name: str - name of db (really just name of collection). Maybe I should put a check here which checks if db name already exists? Or maybe I chuck it outside this func
        - split_length: int - length of each chunk to be used in injection/embedding

    outputs:
        - collection: returns ChromaDB collection that was just created.
        
    """

    #make docs for embedding
    reader = PdfReader(pdf_dir)
    pagetexts = []
    total_splits = []
    for page in reader.pages:
        text = page.extract_text()
        text = text.replace('\n', ' ') #clean text of new lines
        pagetexts.append(text, split_length)

    for pagetext in pagetexts:
        textchunks = split_texts(pagetexts, split_length)
        total_splits.extend(text_chunks)

    #get num of ids for chromadb creation
    ids = [f"id{num}" for num in range(len(total_splits))]

    #create (or upsert into) chromadb
    collection = client.get_or_create_collection(name=db_name)

    #using upsert to overwrite existing
    collection.upsert(documents = total_splits,
                  ids = ids)

    return collection


def make_db_from_csv(csv_dir: str, embedding_col: str, db_name: str):
    """
    function which creates a db from csv, preserving all cols in csv as metadatas.

    inputs:
        - csv_dir: str - directory where csv can be read from
        - embedding_col: str - name of column with text in it that should be embedded
        - db_name: str - name of ChromaDB collection

    outputs:
        - collection: returns ChromaDB collection that was just created.
    
    TO DO: 
        - make this robust to adding multiple metadatas, allow us to specify which column is returned from embedding etc.
        - automatically split embedding dim into 128 words? Logic which also splits injection col????? man I dunno
    
    """
    #ingest and prepare data
    init_df = pd.read_csv(csv_dir)
    documents = list(init_df[embedding_col])
    #add metadatas for select querying I guess, or allowing to pick what we query
    metadatas = [init_df.loc[x].to_dict() for x in range(len(init_df))]
    ids = [f"id{num}" for num in range(len(init_df))]
    
    #create or upsert into collection
    collection = client.get_or_create_collection(name=db_name)

    #using upsert to overwrite existing
    collection.upsert(documents = documents,
                   metadatas = metadatas,
                  ids = ids)

    return collection
    

def make_db_from_docx(docx_dir: str, db_name: str, split_length: int = 128, ):
    """
    func to create db from docx file.

    inputs:
        - docx_dir: str - directory where docx file needs to be read from
        - db_name: str - name of ChromaDB collection
        - split_length: int - length of each chunk of text to be embedded
        
    outputs:
        - collection: returns ChromaDB collection that was just created.
    """
    text = docx2txt.process(docx_dir)
    split_list = split_texts(text, split_length)
    ids = [f"id{num}" for num in range(len(split_list))]

    collection = client.get_or_create_collection(name=db_name)

    collection.upsert(documents = split_list,
                  ids = ids)

    return collection
    
    

def make_db_from_txt(txt_dir: str, db_name: str, split_length: int = 150, ):
    """
    func to create db from txt file.

    inputs:
        - txt_dir: str - directory where txt file needs to be read from
        - db_name: str - name of ChromaDB collection
        - split_length: int - length of each chunk of text to be embedded

    outputs:
        - collection: returns ChromaDB collection that was just created.
    """
    with open(txt_dir, 'r') as f:
        text = f.read()
    
    split_list = split_texts(text, split_length)
    ids = [f"id{num}" for num in range(len(split_list))]

    collection = client.get_or_create_collection(name=db_name)

    collection.upsert(documents = split_list,
                  ids = ids)

    return collection

### TO DO:
"""
TO DO:
    - abstracting function that allows you to delete db?
    - (note: I will probably not expose the funcitonality of updating a db.)
    - idk
"""