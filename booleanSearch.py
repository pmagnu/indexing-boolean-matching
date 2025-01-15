import json
import glob
import os

def search_term_in_file(filepath, term):
    """Search for a term in a single JSON file and return document IDs where the term appears."""
    with open(filepath, 'r') as f:
        batch_data = json.load(f)
        if term in batch_data:
            doc_ids = {posting['doc_id'] for posting in batch_data[term]['postings']}
            return doc_ids
    return set()

def boolean_search(directory, query):
    """Perform a boolean search (AND/OR) across multiple files in a directory."""
    if " AND " in query:
        terms = query.split(" AND ")
        operation = "AND"
    elif " OR " in query:
        terms = query.split(" OR ")
        operation = "OR"
    else:
        terms = [query]
        operation = "AND"
    
    result_docs = None
    
    # Iterate through each term in the query
    for term in terms:
        term_docs = set()
        term_found = False
        
        # Search each file for the current term
        for filepath in glob.glob(os.path.join(directory, 'Indexing/inverted_index_batch_*.json')):
            term_docs_in_file = search_term_in_file(filepath, term)
            if term_docs_in_file:
                term_docs.update(term_docs_in_file)
                term_found = True
                break  # Stop searching other files once the term is found
        
        # If the term was not found in any file, handle based on operation
        if not term_found:
            if operation == "AND":
                print(f"Term '{term}' not found in any file.")
                return set()
            else:
                continue
        
        # If this is the first term, initialize result_docs with term_docs
        if result_docs is None:
            result_docs = term_docs
        else:
            # Perform intersection or union with the previous result_docs
            if operation == "AND":
                result_docs &= term_docs
            elif operation == "OR":
                result_docs |= term_docs

        # Early exit if there are no common documents for AND operation
        if operation == "AND" and not result_docs:
            print("No common documents found.")
            return set()

    return result_docs

# Example usage
directory = '.'  # Adjust this if needed to point to the directory with JSON files
query = "ursula AND prime" 
results = boolean_search(directory, query)

# Print the final result in a readable format
if results:
    print(f"Documents matching the query '{query}' ({len(results)} documents):\n" + "\n".join(results))
else:
    print(f"No documents match the query '{query}'.")