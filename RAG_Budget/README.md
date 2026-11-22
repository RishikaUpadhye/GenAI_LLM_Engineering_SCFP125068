# RAG-Based Budget Analysis — Union Budget 2026–27

A Retrieval-Augmented Generation (RAG) notebook that answers questions using the **Government of India's Union Budget 2026–27 speech**. The notebook combines semantic search over the budget PDF with a Groq-hosted language model and tool calling.

The workflow loads and cleans the PDF, splits it into overlapping text chunks, creates embeddings, stores them in ChromaDB, and retrieves relevant passages to support answers. A calculator tool is also available for numerical comparisons.

## Project files

```text
RAG_Budget/
├── README.md
├── RAG_Budget.ipynb
└── budget_speech.pdf
```

| File | Description |
|---|---|
| `RAG_Budget.ipynb` | Notebook containing PDF ingestion, preprocessing, embedding, vector search, tool definitions, and question answering. |
| `budget_speech.pdf` | Source document: Union Budget 2026–27 speech. |
| `README.md` | Project documentation and setup instructions. |

## Key features

- **PDF ingestion:** Loads the budget speech using LangChain's `PyPDFLoader`.
- **Text cleaning:** Normalizes whitespace and joins words split across PDF line breaks.
- **Text chunking:** Uses `RecursiveCharacterTextSplitter` with a chunk size of 800 and overlap of 150.
- **Semantic embeddings:** Generates embeddings with `sentence-transformers/all-mpnet-base-v2` through Hugging Face.
- **Vector database:** Stores and retrieves document chunks using ChromaDB.
- **RAG question answering:** Retrieves the four most relevant passages before the LLM responds to budget-specific questions.
- **LLM tool calling:** Uses the Groq model configured in the notebook, `openai/gpt-oss-120b`, through LangChain's `ChatGroq` integration.
- **Budget search tool:** `search_budget` searches the indexed speech and returns passages with page references.
- **Calculator tool:** `calculator` performs arithmetic for numerical questions and comparisons.
- **Grounded responses:** The system prompt asks the model to cite source pages and state when an answer is not present in the document.

## Technology stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Kaggle Notebooks | Notebook execution environment used by the current notebook |
| LangChain | Document processing, prompts, retrieval integration, and tool calling |
| PyPDF | Loading the source PDF |
| Hugging Face Sentence Transformers | Text embeddings |
| ChromaDB | Vector storage and similarity search |
| Groq | LLM inference |
| Pandas | Displaying query results in a table |

## Workflow

```text
Union Budget 2026–27 PDF
          |
          v
      PDF loading
          |
          v
 Text cleaning + page metadata
          |
          v
     Text chunking
  (800 size / 150 overlap)
          |
          v
  Hugging Face embeddings
          |
          v
      ChromaDB
          |
          v
     User question
          |
          v
  Groq LLM with tool calling
          |
      +---+---+
      |       |
      v       v
 Budget    Calculator
 search      tool
      |       |
      +---+---+
          |
          v
 Answer with page references
```

## Model and retrieval configuration

| Parameter | Value in the notebook |
|---|---|
| Embedding model | `sentence-transformers/all-mpnet-base-v2` |
| Chat model | `openai/gpt-oss-120b` via `ChatGroq` |
| Chunk size | `800` characters |
| Chunk overlap | `150` characters |
| Results retrieved per budget search | `4` |
| ChromaDB persistence directory | `./db` |
| Maximum tool-call loop iterations per question | `5` |

## Setup and execution

The notebook is currently configured for **Kaggle Notebooks**.

### 1. Open the notebook

Upload or open `RAG_Budget.ipynb` in Kaggle Notebooks.

### 2. Provide the budget PDF

The notebook currently loads the PDF from this Kaggle input path:

```text
/kaggle/input/datasets/rishika/budget/budget_speech.pdf
```

Attach the dataset containing `budget_speech.pdf` to the notebook. When using a different Kaggle dataset or running locally, update the `PyPDFLoader(...)` path in the PDF ingestion cell to the location of the PDF.

### 3. Configure the Groq API key

The notebook retrieves the key using Kaggle's `UserSecretsClient`. In Kaggle, create a secret named:

```text
GROQ_API_KEY
```

Set its value to your Groq API key and enable access to that secret for the notebook.

**Security:** Do not hardcode your API key or commit it to GitHub. The notebook is written to retrieve it from Kaggle Secrets.

### 4. Install dependencies

The first notebook cell installs the libraries used by the project:

```bash
pip install -q langchain-core langchain-text-splitters langchain-huggingface langchain-chroma chromadb "langchain-docling[local]" langsmith langchain-groq langchain-community pypdf pandas
```

### 5. Run the cells in order

Run the notebook from top to bottom:

1. Install the required packages.
2. Import the libraries and load the Kaggle secret.
3. Load, clean, and split the budget PDF.
4. Generate embeddings and create the ChromaDB vector store.
5. Define the budget-search and calculator tools and configure the Groq LLM.
6. Execute the predefined questions and inspect the responses and Pandas results table.

## Example questions in the notebook

- What is the outlay of Biopharma SHAKTI?
- How does the 2026–27 fiscal deficit compare with 2025–26?
- What changes for NCCD on chewing tobacco, and what is the effective duty?
- Explain fiscal deficit in simple words.
- What are the new income tax slab rates in this budget?
- By what percentage does public capex rise from BE 2025–26 to FY2026–27?
- What is the combined outlay of Biopharma SHAKTI, the Container Manufacturing scheme and CCUS?

The test questions are currently stored in a predefined `queries` list in the notebook. Edit that list to test other questions.

## Notes and limitations

- This repository contains the source speech PDF used by the notebook. Budget-specific answers should be checked against that source, especially before relying on financial or tax information.
- The current notebook uses a Kaggle-specific file path and Kaggle Secrets. These need to be adapted for another execution environment.
- The ChromaDB index is generated in `./db` when the notebook runs; the generated database directory does not need to be committed.
- The notebook prints a decision-accuracy summary for its small predefined test set. This is a demonstration of the expected tool-selection behaviour, not a comprehensive evaluation of factual answer accuracy or retrieval quality.
- The calculator tool is intended for arithmetic expressions used by the notebook's questions; do not pass untrusted expressions to it.

## Author

**Rishika Upadhye**  
[GitHub Profile](https://github.com/RishikaUpadhye)

---

Part of the [GenAI LLM Engineering](https://github.com/RishikaUpadhye/GenAI_LLM_Engineering_SCFP125018) repository.
