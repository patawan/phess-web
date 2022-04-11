import pandas as pd
import os
import markovify as mk
import re
import json


# import the excel file to a pandas data frame
cwd = os.getcwd()
all_lines = pd.read_excel(cwd + "/the-office-lines.xlsx")


# Plan to build a model for the top 4 speakers (Michael, Dwight, Jim, & Pam)


# SCRUB A DUB DUB
clean_lines = all_lines.loc[all_lines.deleted == False, :]  # only select rows that weren't deleted scenes
clean_lines['line_text'] = clean_lines['line_text'].str.replace(r"\[.*\]", "")  # remove all actions plus the brackets
clean_lines['speaker'] = clean_lines['speaker'].str.replace(r"\[.*\]", "")  # remove actions from speaker plus brackets
clean_lines['speaker'] = clean_lines['speaker'].str.replace("Dwight.", "Dwight")
clean_lines['speaker'] = clean_lines['speaker'].str.replace("Dwight:", "Dwight")  # fix spellings of Dwight


# The below user-defined function takes input as a list of misspellings of Michael's name and fixes
# all of those misspellings. It could easily be modified to take input of which character to fix names for.
# But for my purposes Michael had a ton of misspellings and the other characters didn't.


michael_misspellings = ["Micheal", "Michel", "Micael", "Micahel",
                        "Michae", "Michal", "Mihael", "Miichael"]


def replace_names(names_list):
    for misspelling in names_list:
        clean_lines.loc[clean_lines.speaker == misspelling, "speaker"] = "Michael"


replace_names(michael_misspellings)


# create the sets of lines for a few characters. The resultant is a Series
michael_lines = clean_lines.loc[clean_lines.speaker == "Michael", 'line_text']
jim_lines = clean_lines.loc[clean_lines.speaker == "Jim", 'line_text']
pam_lines = clean_lines.loc[clean_lines.speaker == "Pam", 'line_text']
dwight_lines = clean_lines.loc[clean_lines.speaker == "Dwight", 'line_text']


# Converts the Series above to one long string
michael_lines_string = michael_lines.str.cat(sep=" ")
jim_lines_string = jim_lines.str.cat(sep=" ")
pam_lines_string = pam_lines.str.cat(sep=" ")
dwight_lines_string = dwight_lines.str.cat(sep=" ")


# Creating and training the models
class POSifiedTextNLTK(mk.Text):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        # words = ["::".join(tag) for tag in nltk.pos_tag(words)]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


# https://joshuanewlan.com/spacy-and-markovify
michael_modelNLTK = POSifiedTextNLTK(michael_lines_string, state_size=3)
jim_modelNLTK = POSifiedTextNLTK(jim_lines_string, state_size=3)
pam_modelNLTK = POSifiedTextNLTK(pam_lines_string, state_size=3)
dwight_modelNLTK = POSifiedTextNLTK(dwight_lines_string, state_size=3)


# exporting the models to json files
michael_model_json = michael_modelNLTK.to_json()
jim_model_json = jim_modelNLTK.to_json()
dwight_model_json = dwight_modelNLTK.to_json()
pam_model_json = pam_modelNLTK.to_json()


# Below cells export to cwd. I then copied them to desktop for easy importing into the flask app.
# these should probably get sent to s3
with open('michael_model_json.txt', 'w') as outfile:
    json.dump(michael_model_json, outfile)
with open('jim_model_json.txt', 'w') as outfile:
    json.dump(jim_model_json, outfile)
with open('pam_model_json.txt', 'w') as outfile:
    json.dump(pam_model_json, outfile)
with open('dwight_model_json.txt', 'w') as outfile:
    json.dump(dwight_model_json, outfile)
