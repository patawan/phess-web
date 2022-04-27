import pandas as pd
import os
import markovify as mk
import re
import json
import boto3


# Creating and training the models
class POSifiedTextNLTK(mk.Text):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


def replace_names(names_list, lines_df):
    for misspelling in names_list:
        lines_df.loc[lines_df.speaker == misspelling, "speaker"] = "Michael"
    return lines_df


def create_models(event, context):

    # import the excel file to a pandas data frame
    cwd = os.getcwd()
    all_lines = pd.read_excel(cwd + "/the-office-lines.xlsx")

    # SCRUB A DUB DUB
    clean_lines = all_lines.loc[all_lines.deleted == False, :]  # only select rows that weren't deleted scenes
    clean_lines['line_text'] = clean_lines['line_text'].str.replace(r"\[.*\]", "")  # remove all actions plus the brackets
    clean_lines['speaker'] = clean_lines['speaker'].str.replace(r"\[.*\]", "")  # remove actions from speaker plus brackets
    clean_lines['speaker'] = clean_lines['speaker'].str.replace("Dwight.", "Dwight")
    clean_lines['speaker'] = clean_lines['speaker'].str.replace("Dwight:", "Dwight")  # fix spellings of Dwight

    michael_misspellings = ["Micheal", "Michel", "Micael", "Micahel",
                            "Michae", "Michal", "Mihael", "Miichael"]

    clean_lines = replace_names(michael_misspellings, clean_lines)

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

    model_json_dict = {
        "michael_model_json": michael_model_json,
        "jim_model_json": jim_model_json,
        "dwight_model_json": dwight_model_json,
        "pam_model_json": pam_model_json
    }

    s3 = boto3.client("s3")

    for name in model_json_dict.keys():
        s3.put_object(
            Body=json.dumps(model_json_dict["name"]),
            Bucket="office-model-bucket",
            Key=f"{name}.json"
        )

    print("Models created and serialized!")
