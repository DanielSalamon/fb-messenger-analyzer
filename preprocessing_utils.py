import os
import json
import pandas as pd
from nltk import word_tokenize, FreqDist, bigrams, trigrams


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


def load_stopwords(path):
    
    #
    #   Helper function to load and polish stopwords from text file.
    #   Input: A path to the stopwords.txt file
    #   Output: Python list of stopwords
    #

    with open(path, "r", encoding='utf-8') as file:
        stopwords = file.read()
        stopwords = stopwords.split("\n")
    
    return stopwords


def tokenize_messages(df, path_to_stopwords):

    #
    #   Function to preprocess all messages in the conversation. It cleanes the data from nan's and stopwords and split into meaningful tokens..
    #   Input: Pandas DataFrame prepared by prepare_data function, path to stopwords text file.
    #   Output: Python list of all tokens from conversation messages
    #

    messages = df['content'].to_numpy()
    tokenized_text = []

    stopwords = load_stopwords(path_to_stopwords)

    for msg in messages:
        if msg != 'nan':
            
            tokens = word_tokenize(msg.lower(), language='polish')
            tokens = [token for token in tokens if (token not in stopwords) and (token.isalpha())] 
            tokenized_text.extend(tokens)

    return tokenized_text


def prepare_word_freq_distribution(tokenized_text, n=1):

    #
    #   Function to calculate word frequencies in the conversation. It can count single words as well as bigrams and trigrams.
    #   Input: Python list of tokens prepared by tokenize_messages function, number of n-grams (1, 2, or 3 possible).
    #   Output: nltk FreqDist based on the conversation
    #

    assert 0 < n <= 3, "n must be 1, 2 or 3"

    if n == 1:
        freqDist = FreqDist(tokenized_text)
    elif n == 2:
        bgs = bigrams(tokenized_text)
        freqDist = FreqDist(bgs)
    else:
        tgs = trigrams(tokenized_text)
        freqDist = FreqDist(tgs)

    return freqDist