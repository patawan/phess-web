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


def create_models(event, context):

    # import the excel file to a pandas data frame
    cwd = os.getcwd()
    clean_lines = pd.read_csv(cwd + "/of-lines.csv")

    # create the sets of lines for a few characters. The resultant is a Series
    michael_lines = clean_lines.loc[clean_lines.speaker == "Michael", "line_text"]
    jim_lines = clean_lines.loc[clean_lines.speaker == "Jim", "line_text"]
    pam_lines = clean_lines.loc[clean_lines.speaker == "Pam", "line_text"]
    dwight_lines = clean_lines.loc[clean_lines.speaker == "Dwight", "line_text"]

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

    pr_lines = pd.read_csv(cwd + "/pr-lines.csv")
    leslie_lines = pr_lines.loc[pr_lines.speaker == "Leslie Knope", "line_text"]
    ron_lines = pr_lines.loc[pr_lines.speaker == "Ron Swanson", "line_text"]
    tom_lines = pr_lines.loc[pr_lines.speaker == "Tom Haverford", "line_text"]
    ann_lines = pr_lines.loc[pr_lines.speaker == "Ann Perkins", "line_text"]
    april_lines = pr_lines.loc[pr_lines.speaker == "April Ludgate", "line_text"]
    andy_lines = pr_lines.loc[pr_lines.speaker == "Andy Dwyer", "line_text"]
    ben_lines = pr_lines.loc[pr_lines.speaker == "Ben Wyatt", "line_text"]
    chris_lines = pr_lines.loc[pr_lines.speaker == "Chris Traeger", "line_text"]
    jerry_lines = pr_lines.loc[pr_lines.speaker == "Jerry Gergich", "line_text"]
    donna_lines = pr_lines.loc[pr_lines.speaker == "Donna Meagle", "line_text"]

    # Converts the Series above to one long string
    leslie_lines_string = leslie_lines.str.cat(sep=" ")
    ron_lines_string = ron_lines.str.cat(sep=" ")
    tom_lines_string = tom_lines.str.cat(sep=" ")
    ann_lines_string = ann_lines.str.cat(sep=" ")
    april_lines_string = april_lines.str.cat(sep=" ")
    andy_lines_string = andy_lines.str.cat(sep=" ")
    ben_lines_string = ben_lines.str.cat(sep=" ")
    chris_lines_string = chris_lines.str.cat(sep=" ")
    jerry_lines_string = jerry_lines.str.cat(sep=" ")
    donna_lines_string = donna_lines.str.cat(sep=" ")

    leslie_modelNLTK = POSifiedTextNLTK(leslie_lines_string, state_size=3)
    ron_modelNLTK = POSifiedTextNLTK(ron_lines_string, state_size=3)
    tom_modelNLTK = POSifiedTextNLTK(tom_lines_string, state_size=3)
    ann_modelNLTK = POSifiedTextNLTK(ann_lines_string, state_size=3)
    april_modelNLTK = POSifiedTextNLTK(april_lines_string, state_size=3)
    andy_modelNLTK = POSifiedTextNLTK(andy_lines_string, state_size=3)
    ben_modelNLTK = POSifiedTextNLTK(ben_lines_string, state_size=3)
    chris_modelNLTK = POSifiedTextNLTK(chris_lines_string, state_size=3)
    jerry_modelNLTK = POSifiedTextNLTK(jerry_lines_string, state_size=3)
    donna_modelNLTK = POSifiedTextNLTK(donna_lines_string, state_size=3)

    # exporting the models to json files
    leslie_model_json = leslie_modelNLTK.to_json()
    ron_model_json = ron_modelNLTK.to_json()
    tom_model_json = tom_modelNLTK.to_json()
    ann_model_json = ann_modelNLTK.to_json()
    april_model_json = april_modelNLTK.to_json()
    andy_model_json = andy_modelNLTK.to_json()
    ben_model_json = ben_modelNLTK.to_json()
    chris_model_json = chris_modelNLTK.to_json()
    jerry_model_json = jerry_modelNLTK.to_json()
    donna_model_json = donna_modelNLTK.to_json()

    model_json_dict = {
        "michael_model_json": michael_model_json,
        "jim_model_json": jim_model_json,
        "dwight_model_json": dwight_model_json,
        "pam_model_json": pam_model_json,
        "leslie_model_json": leslie_model_json,
        "ron_model_json": ron_model_json,
        "tom_model_json": tom_model_json,
        "ann_model_json": ann_model_json,
        "april_model_json": april_model_json,
        "andy_model_json": andy_model_json,
        "ben_model_json": ben_model_json,
        "chris_model_json": chris_model_json,
        "jerry_model_json": jerry_model_json,
        "donna_model_json": donna_model_json,
    }

    s3 = boto3.client("s3")

    for name in model_json_dict.keys():
        s3.put_object(
            Body=json.dumps(model_json_dict[name]),
            Bucket="office-model-bucket",
            Key=f"{name}.json",
        )

    print("Models created and serialized!")
