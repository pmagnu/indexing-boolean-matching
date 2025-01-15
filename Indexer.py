import json
import re
import os
import hashlib

from docx import Document
from nltk.stem import PorterStemmer
from collections import defaultdict

global TERM_SEQUENCE_JSON

class InvertedIndexBuilder:
    def __init__(self):
        self.term_sequence = {}
        self.inverted_index = defaultdict(list)
    
    # Load document helper function
    def load_document(self, file_path):
        script_dir = os.path.dirname(__file__)
        absolute_file_path = os.path.join(script_dir, file_path)

        if not os.path.isfile(absolute_file_path):
            raise FileNotFoundError(f"The file {absolute_file_path} does not exist.")

        _, file_extension = os.path.splitext(absolute_file_path)

        if file_extension.lower() == '.txt':
            return self.read_text_file(absolute_file_path)
        elif file_extension.lower() == '.docx':
            return self.read_word_file(absolute_file_path)
        else:
            raise ValueError("Unsupported file type. Please provide a .txt or .docx file.")

    # Read text file
    def read_text_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    # Read word document
    def read_word_file(self, file_path):
        doc = Document(file_path)
        return ' '.join(paragraph.text for paragraph in doc.paragraphs)

    # Tokenize document content
    def tokenization(self, doc):
        stream = re.sub(r'[,\.\-\!\?:;()\[\]{}<>\\/|@#$%^&*_+=~`\'"´]', '', doc).split()
        return [token.lower().strip() for token in stream]

    # Remove stop words from tokens
    def remove_stop_words(self, tokens):
        stop_words = self.load_document("stopwords_en.txt").split("\n")
        return [word for word in tokens if word not in stop_words]

    # Apply stemming to tokens
    def stemming(self, tokens):
        ps = PorterStemmer()
        return [ps.stem(token) for token in tokens]

    # Create term sequence and inverted index
    def create_term_sequence_json(self, tokens, doc_id):
        for position, term in enumerate(tokens):
            if term not in self.term_sequence:
                self.term_sequence[term] = {"doc_freq": 0, "postings": []}
            
            # Update term sequence to add document only once, but track positions
            posting_found = False
            for posting in self.term_sequence[term]["postings"]:
                if posting["doc_id"] == doc_id:
                    posting["positions"].append(position)
                    posting_found = True
                    break
            
            # If it's the first time this doc_id is added for the term
            if not posting_found:
                self.term_sequence[term]["postings"].append({"doc_id": doc_id, "positions": [position]})
                self.term_sequence[term]["doc_freq"] += 1
            
        # Update the inverted index (storing positions)
        self.inverted_index[term].append((doc_id, position))  # Store doc ID and position



    # Normalize document and update term sequence and inverted index
    def linguistic_normalization(self, doc_id, doc):
        print(f"Normalizing document {doc_id}...")
        tokens = self.tokenization(doc)
        tokens = self.remove_stop_words(tokens)
        tokens = self.stemming(tokens)
        print(f"No. of Tokens: {len(tokens)}")
        self.create_term_sequence_json(tokens, doc_id)

    # Save data to JSON file
    def save_to_json(self, data, filename):
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    # Build the entire inverted index
    def build_inverted_index(self, docs):
        for doc_id, doc in docs:
            self.linguistic_normalization(doc_id, doc)
        # Save the term sequence and inverted index to JSON files
        self.save_to_json(self.term_sequence, 'term_sequence.json')
        self.save_to_json(self.inverted_index, 'inverted_index.json')

    # Print term frequencies
    def calculate_doc_frequency(self):
        print("Term".ljust(15), "Doc. Freq.", "Posting List")
        for term in sorted(self.term_sequence.keys()):
            print(term.ljust(15), self.term_sequence[term]["doc_freq"], self.term_sequence[term]["postings"])

    def get_crawled_content_file_path(self, filename):
        script_dir = os.path.dirname(__file__)  
        crawled_content_dir = os.path.join(script_dir, '../Web_Crawler/crawled_content')
        return os.path.join(crawled_content_dir, filename)

    def read_crawled_content_file(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def process_crawled_content(self, file_path):
        # Step 1: Read the crawled content
        crawled_data = self.read_crawled_content_file(file_path)
        content = crawled_data["content"]
        url = crawled_data["url"]
        
        # Step 2: Tokenize, Remove Stop Words, and Stem the content
        tokens = self.tokenization(content)
        tokens = self.remove_stop_words(tokens)
        tokens = self.stemming(tokens)
        
        # Step 3: Update the inverted index (term sequence)
        doc_id = hashlib.md5(url.encode('utf-8')).hexdigest()  # Use hash of the URL as doc ID
        self.create_term_sequence_json(tokens, doc_id)

    def store_inverted_index(self, file_name='inverted_index.json'):
        # Store the updated term sequence to a JSON file
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(self.term_sequence, json_file, indent=4)
        print(f"Inverted index stored in {file_name}")

    def process_files_in_batches(self, batch_size=100):
        script_dir = os.path.dirname(__file__)
        crawled_content_dir = os.path.join(script_dir, '../Web_Crawler/crawled_content')
        
        # Get all JSON files in the directory
        files = [f for f in os.listdir(crawled_content_dir) if f.endswith('.json')]
        
        total_files = len(files)
        print(f"Total files to process: {total_files}")
        
        # Process files in batches
        for i in range(0, total_files, batch_size):
            batch_files = files[i:i + batch_size]
            
            # Process each file in the batch
            for filename in batch_files:
                file_path = self.get_crawled_content_file_path(filename)
                self.process_crawled_content(file_path)
            
            # Store the intermediate result
            self.store_inverted_index(f'inverted_index_batch_{i // batch_size}.json')
            print(f"Processed batch {i // batch_size + 1} of {total_files // batch_size + 1}")
   

# Example usage
if __name__ == "__main__":
    docs = {
        "doc1": "THIS is'n SomThing. I want to know if it works. Hahah, nope JUST KIDDING. I'm not sure if it works. O. 2014 computer, computer",
        "doc2": "hello from the other side computer"
    }

    # Initialize builder
    index_builder = InvertedIndexBuilder()

    index_builder.process_files_in_batches(batch_size=100)
    # Build the inverted index
    # index_builder.build_inverted_index(docs.items())

    # # Calculate document frequency
    # index_builder.calculate_doc_frequency()

    print("Inverted index and term sequence stored in JSON files.")
