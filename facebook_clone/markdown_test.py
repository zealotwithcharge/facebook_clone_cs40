import string
# line = ""


# mark = "*"
# tag = "<i>"
# end_tag = tag[0]+'/'+tag[1:]

# word_list = line.split(mark)


# for i,word in enumerate(word_list):
#     if i!=0 and i!=len(word_list)-1:


#         if  word != "" and word[-1] != '\\':
#             word_list[i] = tag+word+end_tag
#         elif word[-1] == '\\':
#             if word == '\\':
#                 word_list[i] = mark
#             else:
#                 word_list[i] = mark+word[:-1]
#         else:
#             word_list[i] = mark+word
#     if i == 0:
#         if word != "" and word[-1] == '\\':
#             if word == '\\':
#                 word_list[i] = ""
#             else:
#                 word_list[i] = word[:-1]
#     if len(word_list) != 1 and i == len(word_list)-1:
#         if word_list[i-1].find(end_tag) != -1 and word_list[i-1].find(end_tag) == len(word_list[i-1])-len(end_tag):
#             pass
#         else:
#             word_list[i] = mark+word
# line1 = "".join(word_list)

# print(line1)
# # with should not be connected


line = "*oeauAOE*!"

mark = "*"
tag = "<i>"
end_tag = tag[0]+'/'+tag[1:]

word_list = line.split(mark)


for i,word in enumerate(word_list):
    if i!=0 and i!=len(word_list)-1:


        if (word_list[i-1]=="" or word_list[i-1][-1] == " " or word_list[i-1][-1] in string.punctuation) and (word_list[i+1] == "" or word_list[i+1][0] == " " or word_list[i+1][0] in string.punctuation) and word != "" and word[-1] != '\\':
            word_list[i] = tag+word+end_tag
        elif word[-1] == '\\':
            if word == '\\':
                word_list[i] = mark
            else:
                word_list[i] = mark+word[:-1]
        else:
            word_list[i] = mark+word
    if i == 0:
        if word != "" and word[-1] == '\\':
            if word == '\\':
                word_list[i] = ""
            else:
                word_list[i] = word[:-1]
    if len(word_list) != 1 and i == len(word_list)-1:
        if word_list[i-1].find(end_tag) != -1 and word_list[i-1].find(end_tag) == len(word_list[i-1])-len(end_tag):
            pass
        else:
            word_list[i] = mark+word
line1 = "".join(word_list)
print(line1)