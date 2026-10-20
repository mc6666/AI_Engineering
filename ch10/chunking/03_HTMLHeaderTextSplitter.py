from langchain_text_splitters import HTMLHeaderTextSplitter

headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
]
html_string = open('index.html', encoding='utf8').read()
html_splitter = HTMLHeaderTextSplitter(headers_to_split_on)
chunks = html_splitter.split_text(html_string)
print(chunks)
