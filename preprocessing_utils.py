import os
import json
import pandas as pd


def load_conversation(path):

    #
    #   Find all json files in the directory and create the Pandas DataFrame containing all messages in the conversation.
    #   Input: path, exmpl: "facebook-data\messages\inbox\conversation_folder"
    #   Output: Pandas DataFrame with columns: ['sender_name', 'timestamp_ms', 'content', 'reactions']
    #

    json_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
    data = pd.DataFrame()

    for f in json_files:
        file = open(os.path.join(path, f), encoding='utf-8')
        json_file = json.load(file)
        temp_df = pd.DataFrame.from_dict(json_file['messages'])
        data = pd.concat([data, temp_df])
        file.close()

    
    data = data[['sender_name', 'timestamp_ms', 'content', 'reactions']]     

    return data


def decode_data(data):

    #
    #   A helper funciton to decode all Polish special characters.
    #   Input: Pandas DataFrame created by load_conversation()
    #   Output: Pandas DataFrame with decoded special characters
    #
    
    for col in data.columns:
        try:
            data[col] = data[col].astype(str).str.encode('iso-8859-1').str.decode('utf-8') 
        except:
            pass
        
    return data


def convert_timestamps(data):
    
    #
    #   A helper funciton to convert message timestamps in miliseconds into two columns: datetime format and month.
    #   Input: Pandas DataFrame
    #   Output: Pandas DataFrame with two additional columns
    #

    data['datetime'] = pd.to_datetime(data['timestamp_ms'], unit='ms')
    data['month'] = pd.to_datetime(data['timestamp_ms'], unit='ms').dt.month

    return data

def prepare_data(data_path):

    #
    #   Wrapper function to load and preprocess json data.
    #   Input: A path to the conversation data
    #   Output: Preprocessed Pandas DataFrame with columns ['sender_name', 'timestamp_ms', 'content', 'reactions', 'date', 'datetime', 'month']
    #

    df = load_conversation(data_path)
    df = decode_data(df)
    df = convert_timestamps(df)

    return df