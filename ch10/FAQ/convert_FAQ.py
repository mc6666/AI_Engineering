f = open('./Amazon_EC2_FAQ.txt', encoding='utf8')
output_file = open('./data/Amazon_EC2_FAQ.csv', 'w', encoding='utf8')
output_file.write('Prompt,answer\n')
lines = f.readlines()
for i in range(len(lines)):
    if lines[i].startswith('問：'): 
        row = '"' + lines[i][2:-1] + '"'
        i = i+2
        row += ',"' + lines[i][:-1] + '"'
        output_file.write(row+'\n')
output_file.close()        
f.close()        
