import os
import json
import pandas as pd
from nltk import word_tokenize, FreqDist, bigrams, trigrams
import numpy as np
import re


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



def received_reactions_stats(df):

    #
    #   This function can get a dataframe (either whole conversation or user specified messages) and retrieve statistics about reactions posted to
    #   all of messages in the dataframe. This is from a point of view of a RECEIVING user.
    #   Input: Pandas DataFrame in a form as created by prepare_data() function.
    #   Output: Python dict with 3 reaction statistics: total number of reactions, most common reaction and the name of the user that reacted most often.
    #

    if np.any(df["reactions"].dropna().to_numpy()):
        reactions = np.hstack(df["reactions"].dropna().to_numpy())
        total_reactions = len(reactions)

        icons = []
        reactors = []
        for r in reactions:
            icons.append(r['reaction'])
            reactors.append(r['actor'])

        icons = pd.Series(icons).astype(str).str.encode('iso-8859-1').str.decode('utf-8') 
        reactors = pd.Series(reactors).astype(str).str.encode('iso-8859-1').str.decode('utf-8') 

        icons_ranking = icons.value_counts()
        reactors_ranking = reactors.value_counts()

        favourite_icon_received = icons_ranking.index[0]
        most_emotional = reactors_ranking.index[0]

    else:
        total_reactions = 0
        favourite_icon_received = None
        most_emotional = ""

    
    result = {
                "total_reactions" : total_reactions,
                "favourite_icon_received" : favourite_icon_received,
                "most_reactions_received" : most_emotional
             }
    
    return result


def granted_reaction_stats_per_user(df):

    #
    #   This function retrieves reaction statistics, but from the point of a GIVING user. 
    #   Input: Pandas DataFrame in a form as created by prepare_data() function.
    #   Output: Python dict where the key is the user name, and value is another dict with two statistics: most common reaction given by the user and to 
    #   which other user messages current participant reacted the most number of times. Example of Output:
    #
    #   Output =  {
    #               'User1': {
    #                          'favourtite_reaction_given': '😆',
    #                          'favourite_user_to_give': 'User2'
    #                        },
    #               'User2': {
    #                          'favourtite_reaction_given': '😆',
    #                          'favourite_user_to_give': 'User3'
    #                        },
    #               'User3': {
    #                          'favourtite_reaction_given': '👍',
    #                          'favourite_user_to_give': 'User1'
    #                        } 
    #              }
    #

    conversation_users = df['sender_name'].unique()
    collection_dict = {}
    result_dict = {}

    senders = df['sender_name'].to_numpy()
    reactions = df['reactions'].to_numpy()

    for usr in conversation_users:
        
        collection_dict[usr] = {
                            "reactions" : [],
                            "receivers" : []
                           }
        
        for i in range(len(reactions)):

            if isinstance(reactions[i], list):
                
                for r in reactions[i]:

                    if r['actor'].encode('iso-8859-1').decode('utf-8') == usr:

                        collection_dict[usr]["reactions"].append(r['reaction'])
                        collection_dict[usr]["receivers"].append(senders[i])
    

        given_reactions = pd.Series(collection_dict[usr]["reactions"]).astype(str).str.encode('iso-8859-1').str.decode('utf-8') 
        users_to_give = pd.Series(collection_dict[usr]["receivers"])#.astype(str).str.encode('iso-8859-1').str.decode('utf-8') 

        favourtite_reaction_given_ranking = given_reactions.value_counts()
        favourite_users_ranking = users_to_give.value_counts()
        total_reactions_given = len(collection_dict[usr]["reactions"])

        result_dict[usr] = {
                            "favourite_reaction_given" : favourtite_reaction_given_ranking.index[0],
                            "favourite_user_to_give" : favourite_users_ranking.index[0],
                            "reactions_given" : total_reactions_given
                           }
                

    return result_dict


def get_conversation_stats(df):
    
    #
    #   A helper function that collects all useful statistics about the conversation.
    #   Input: Pandas DataFrame in a form as created by prepare_data() function.
    #   Output: Python dict with statistics: 
    #            1. Total numer of messgaes
    #            2. Average message length
    #            3. The day when the most messages were sent
    #            4. The number of messages sent on most busy day
    #            5. First message sent in the conversation
    #            6. The sender of the first message
    #            7. Total number of reactions
    #            8. Most common reaction in the conversation
    #            9. The user which granted a reaction most often
    #

    reaction_stats = received_reactions_stats(df)
    messgaes_daily = df.groupby(df['datetime'].dt.date).size().reset_index(name='counts').sort_values(by=['counts'], ascending=False).reset_index()
    sorted_messages = df.loc[df['content'] != 'nan'].sort_values(by=['timestamp_ms']).reset_index()

    msg_lengths = [len(re.findall(r'\w+', i)) for i in sorted_messages['content'].to_numpy()]

    result_stats = {
                    "total_messages" : df.shape[0],
                    "avg_message_length": np.round(np.mean(msg_lengths), 2),
                    "most_busy_day" : str(messgaes_daily.loc[0, 'datetime']),
                    "messgaes_on_most_busy_day" : messgaes_daily.loc[0, 'counts'],
                    "first_message" : sorted_messages.loc[0, 'content'],
                    "first_message_sender" : sorted_messages.loc[0, 'sender_name'],
                    "total_reactions" : reaction_stats["total_reactions"],
                    "most_common_reaction" : reaction_stats["favourite_icon_received"],
                    "most_emotional_user" : reaction_stats["most_reactions_received"]
                   }
    return result_stats
    


def get_stats_per_user(df):

    #
    #   Collect all statistics per user and wrap them into a Pandas Dataframe.
    #   Input: Pandas DataFrame in a form as created by prepare_data() function.
    #   Output: Pandas Dataframe where index is the user and columns are statistics returned by get_conversation_stats().
    #

    conversation_users = df['sender_name'].unique()
    output_dict = {}
    granted_reaction_stats = granted_reaction_stats_per_user(df)

    for user in conversation_users:

        user_messages_df = df.loc[df["sender_name"] == user]
        user_stats = get_conversation_stats(user_messages_df)
        user_stats["favourtie_reaction_given"] = granted_reaction_stats[user]['favourite_reaction_given']
        user_stats['favourite_user_to_give_to'] = granted_reaction_stats[user]['favourite_user_to_give']
        user_stats["total_reactions_given_to_others"] = granted_reaction_stats[user]['reactions_given']
        output_dict[user] = user_stats

    result = pd.DataFrame.from_dict(output_dict, orient='index')
    
    return result[result['total_messages'] > 1] # return the actual participants which sent more that jsut one message



def get_badges(df):
    
    """
    Retrieves the top performers in different categories based on the provided DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the necessary data.

    Returns:
        dict: A dictionary with keys representing different categories and values representing the top performers in each category.

    Description:
        This function takes a DataFrame as input and retrieves the top performers in different categories. The categories and their corresponding criteria are as follows:
        
        - Messenger: The top 3 individuals with the highest total number of messages.
        - Storyteller: The top 3 individuals with the highest average message length.
        - Entertainer: The top 3 individuals with the highest ratio of total reactions to total messages.
        - Sensitivist: The top 3 individuals with the highest total number of reactions given to others.
        
        The function creates a dictionary with the category names as keys and a list of top performers (formatted as "<performer> - <value>") as values. The resulting dictionary is returned.
    """

    Messenger = df["total_messages"].sort_values(ascending=False)[:3].reset_index()
    Storyteller = df["avg_message_length"].sort_values(ascending=False)[:3].reset_index()
    Entertainer = (df["total_reactions"] / df["total_messages"]).sort_values(ascending=False)[:3]
    Sensitivist = df["total_reactions_given_to_others"].sort_values(ascending=False)[:3].reset_index()
    
    result = {"Messenger" : [str(Messenger.loc[i,:]["index"]) + " - " + str(Messenger.loc[i,:]["total_messages"]) for i in range(3)],
              "Storyteller" : [str(Storyteller.loc[i,:]["index"]) + " - " + str(Storyteller.loc[i,:]["avg_message_length"]) for i in range(3)],
              "Entertainer" : [i + " - " + str(np.round(Entertainer.loc[i], 2)) for i in Entertainer.index],
              "Sensitivist" : [str(Sensitivist.loc[i,:]["index"]) + " - " + str(Sensitivist.loc[i,:]["total_reactions_given_to_others"]) for i in range(3)]

    }

    return result
