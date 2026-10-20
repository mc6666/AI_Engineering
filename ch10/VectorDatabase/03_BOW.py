# 引入套件
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

# 測試資料
doc = [
    'This movie is very scary and long',
    'This movie is not scary and is slow',
    'This movie is spooky and good'
]

# BOW
cv = CountVectorizer()
X = cv.fit(doc) 
print('Dictionary of all the unique words in the doc:\n',X.vocabulary_)

# 列舉所有單字
print(f'\nFeature names:\n{cv.get_feature_names_out()}\n', )

# 測試資料經BOW轉換後的向量
X = cv.transform(doc)
print('\nDocuments Transformed by BOW:')
print(X.toarray())

# 轉換為表格
df =pd.DataFrame(X.toarray(), columns = cv.get_feature_names_out())
print('\nBOW表格:\n', df)
