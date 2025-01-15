# Web Intelligence Course - Exam Repository

This repository contains the relevant code developed as part of the Web Intelligence course. The included files and examples demonstrate key functionalities implemented for the course exam.

## Overview of the Repository

- **Web Crawler**  
  Gathers information from websites and stores the extracted data in the `crawled_content` folder.  
  Sample crawled files are provided in the `crawled_content` folder as examples.

- **Indexer**  
  Handles the preprocessing of the crawled content, including:
  - Tokenization
  - Stopword removal
  - Stemming  
  Produces an inverted index for efficient document retrieval.  
  An example of the output is provided as `inverted_index_batch_0`.

- **Boolean Search**  
  Searches through the inverted index using logical operators such as:
  - `AND`
  - `OR`
  Facilitates document retrieval based on user queries.


