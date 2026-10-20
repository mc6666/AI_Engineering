from langchain_community.document_loaders import CSVLoader
import tempfile, os
import streamlit as st
from Base import creation_FAQ_chain,creation_of_vectorDB_in_local

# 定義載入CSV檔案的函數
def csv_loader(tmp_file_path):
    loader=CSVLoader(file_path=tmp_file_path, encoding='utf8')
    return loader

def main():
    # 定義網頁標題
    st.set_page_config(page_title="FAQ Chatbot",page_icon="😈",layout="wide")
    st.title("🦜FAQ ChatBot with your CSV files🦜")

    # 定義側邊欄
    with st.sidebar:
        st.title("數據導入(Data ingestion)")
        st.markdown('---')
        st.subheader('上傳 CSV 檔案')
        doc=st.file_uploader("上傳 CSV 檔案後點擊 『處理』 按鈕",'csv')

        if st.button("處理"):
            with st.spinner("Processing"):
                if doc is not None:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(doc.getvalue())
                        tmp_file_path = tmp_file.name
            
                        st.success(f'File {doc.name} is successfully saved!')
                    
                    load=csv_loader(tmp_file_path)
                    creation_of_vectorDB_in_local(load)
                    st.success("Process Done")
                else:
                    st.error("❗️請上傳 CSV 檔案❗️")
        
    # 定義主畫面
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown (message["content"])

    query=st.chat_input("Ask the Question")
    if query:
        # RAG查詢
        result=creation_FAQ_chain(query)
        st.chat_message ("user"). markdown(query)
        st.session_state. messages.append({"role": "user","content": query})

        # 顯示查詢結果
        with st.chat_message("assistant"):
            st.markdown (result)
            st.session_state.messages. append(
                {"role": "assistant",
                "content": result})
       
if __name__=='__main__':
    main()                