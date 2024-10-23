# Data pipeline

## Load data for RAG

⚠️ This workflow is in flux and subject to change.

To load a PDF as a source of data for Retrieval Augmented Generation:

```sh
# place the source PDF in the data_pipeline directory
cp source.pdf ./local/data_pipeline/

# run a script to extract text from the PDF and save
# to `sourcetext.tmp` in the data_pipeline directory
python ./local/data_pipeline/pdf_to_raw_sourcetext.py source.pdf

# run the database in the background and ensure all migrations have run
just db &
just migrate

# insert extracted data as a SourceText record in the database
# - assumes a previous step wrote to `sourcetext.tmp`
PGPASSWORD=password ./local/data_pipeline/raw_sourcetext_to_database.sh
```

## Embeddings service

[draLLaM](https://github.com/albertomh/draLLaM) is DepositDuck's dedicated LLM service.
As of draLLaM@0.1.0 the service focuses on generating text embeddings.  
Invoke `just drallam` to run it locally - containerised and available on `:11434` - ready
to respond to queries from the main DepositDuck webapp. There are draLLaM-specific settings
in `.env` that can be used to specify host and port.
