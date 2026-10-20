from langchain_text_splitters import RecursiveCharacterTextSplitter

text = "LangChain simplifies AI workflows. " + \
    "It enables advanced retrieval-augmented generation systems " + \
    "for NLP tasks."
splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
chunks = splitter.split_text(text)
print(chunks)