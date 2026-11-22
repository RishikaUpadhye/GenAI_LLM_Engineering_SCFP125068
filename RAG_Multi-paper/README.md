# Multi-Paper Research Assistant (RAG)
 
A notebook-based Retrieval-Augmented Generation (RAG) project that loads
three research-paper PDFs, stores their text chunks in Chroma DB, and
answers questions using a Groq-hosted language model.

## Project Structure

``` text
RAG_Multi-paper/
├── multi-research-paper-assignment.ipynb
└── papers/
    ├── Paper_1.pdf
    ├── Paper_2.pdf
    └── Paper_3.pdf
```

## Technologies Used

-   **Python** --- main programming language.
-   **Docling / DoclingLoader** --- loads and extracts content from PDF
    papers.
-   **LangChain** --- connects document loading, text splitting,
    retrieval, prompts, and the language model.
-   **RecursiveCharacterTextSplitter** --- splits extracted text into
    chunks.
-   **Hugging Face Embeddings** ---
    `sentence-transformers/all-mpnet-base-v2` converts text into
    embeddings.
-   **Chroma DB** --- stores the embedded chunks and supports similarity
    search.
-   **Groq / ChatGroq** --- runs the `openai/gpt-oss-120b` model for
    answer generation.
-   **Kaggle Secrets** --- securely provides the `GROQ_API_KEY`.

## Workflow

1.  Install the required Python packages.
2.  Load the three PDF files using `DoclingLoader`.
3.  Attach the paper filename and page index as metadata.
4.  Split the extracted documents into chunks of 800 characters with 100
    characters of overlap.
5.  Remove complex metadata values before inserting documents into
    Chroma DB.
6.  Generate embeddings with `all-mpnet-base-v2` and create a persistent
    Chroma store in `paper_db`.
7.  Retrieve relevant chunks in one of two modes:
    -   **Single-paper mode:** searches within the paper filename
        supplied by the user.
    -   **Cross-paper mode:** searches each paper and combines the
        retrieved chunks.
8.  Send the question and retrieved context to the Groq model using a
    `ChatPromptTemplate`.
9.  Print the generated answer and the paper/page metadata of retrieved
    chunks.
10. Run the interactive question loop until the user enters `exit`, then
    execute the six test prompts in the evaluation cell.

## Setup and Running

### 1. Prepare the PDFs

Place `Paper_1.pdf`, `Paper_2.pdf`, and `Paper_3.pdf` in the `papers/`
folder.

### 2. Open the notebook

Open `multi-research-paper-assignment.ipynb` in Kaggle Notebook.

The current notebook uses this Kaggle dataset path in its PDF-loading
cell:

``` python
folder = "/kaggle/input/datasets/rishika/papers"
```

Make sure the PDFs are available at that path in the Kaggle environment.

### 3. Configure the Groq API key

Add a Kaggle Secret named:

``` text
GROQ_API_KEY
```

The notebook reads this secret using `UserSecretsClient`.

### 4. Run the notebook

Run the notebook cells in order. When the interactive loop asks for
input:

-   Enter a question.
-   Enter `single` to search one paper, then provide its filename (for
    example, `Paper_1.pdf`).
-   Enter `cross` to search across the papers.
-   Enter `exit` to stop the interactive loop.

After the loop ends, the final cell runs the six evaluation prompts.

## Retrieval Modes

  -----------------------------------------------------------------------
  Mode                                How it works
  ----------------------------------- -----------------------------------
  Single-paper                        Uses Chroma metadata filtering to
                                      search the specified paper.

  Cross-paper                         Performs a separate similarity
                                      search for each paper and combines
                                      the retrieved chunks.
  -----------------------------------------------------------------------

## Evaluation Questions

The notebook includes these six test prompts:

1.  What method does Paper_1 use?
2.  What is Paper_2's main contribution?
3.  Compare methods in all papers.
4.  Compare their evaluation approaches.
5.  What is the population of Mars?
6.  What was Apple's stock price in 1900?

The first four are intended as research-paper questions. The last two
are out-of-scope questions intended to check whether the assistant
declines when the retrieved context does not contain the answer.

## Current Notebook Behavior and Notes

This README documents the notebook as it currently exists; it does not
modify the notebook.

-   The page metadata is assigned using the position of each item
    returned by `DoclingLoader` (`i + 1`). This is an index-based page
    value and should not be assumed to be the exact original PDF page
    unless each loaded item corresponds to one page.
-   The Chroma store is created with `persist_directory="paper_db"`. The
    current notebook creates the store from the chunks when Cell 4 runs;
    it does not contain an explicit existing-index reload or
    incremental-add check.
-   In the interactive loop, single-paper mode asks for a filename, such
    as `Paper_1.pdf`.
-   The evaluation cell calls `answer(q, mode)` without passing a paper
    filename for its two single-paper tests. Therefore, those two tests
    may not perform the intended single-paper retrieval as written.
-   The answer prompt instructs the model to use only retrieved context
    and not follow instructions found in document text. Model compliance
    and factual correctness still need to be checked against the
    retrieved excerpts.
-   The printed Sources list shows the metadata of retrieved chunks. It
    does not by itself prove that every generated claim is supported by
    those chunks.
-   PDF layout, two-column text, tables, and equations can affect
    extraction and retrieval quality.

## Expected Output

When a question is submitted, the notebook prints:

-   The model-generated answer.
-   A `Sources` list containing the retrieved paper filename and page
    metadata.

The evaluation cell runs the six predefined questions and prints the
answer and retrieved sources for each.

## Conclusion

This project demonstrates a multi-document RAG workflow: PDF ingestion,
chunking, embedding generation, vector storage, single-paper and
cross-paper retrieval, LLM-based answer generation, source metadata
display, and a small evaluation set.
