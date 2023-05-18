import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont
import textwrap


def plot_monthly_messages(df, output_path):

    #
    #   Create a line chart of number of messages sent per month
    #   Input: Pandas DataFrame with converted timestamps
    #   Output: Line chart in format of matplotlib figure
    #

    layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',#'rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)')#'rgba(0,0,0,0)')

    df = df.groupby(['month']).size().reset_index(name='counts')

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']

    fig = go.Figure(layout=layout)

    fig.add_trace(go.Scatter(x=months, y=df["counts"], name='Messages per month', 
                mode="lines+markers+text",text=df['counts'], textposition="top right",
        textfont=dict(
            family="Verdana",
            size=14,
            color="black"
        ), line = dict(color='LightSeaGreen', width=2)))



    #fig.update_layout(title='Messages sent in conversation',
    #                xaxis_title='Month',
    #                yaxis_title='Number of messages sent',
    #                font=dict(
    #        family="Verdana",
    #        size=12,
    #        color="DarkBlue"
    #    )
     #               )

    
    #fig.show()
    fig.write_image(output_path, width=800, height=400)

def distribution_pie(df):

    #
    #   Create a pie chart message distribution among conversation participants
    #   Input: Pandas DataFrame with converted timestamps
    #   Output: Pie chart in format of matplotlib figure
    #

    labels = df['sender_name'].unique()
    counts = df['sender_name'].value_counts()
    labels = counts.index

    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')


    # Use `hole` to create a donut-like pie chart
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Pie(labels=labels, values=counts, hole=.3))


    fig.update_traces(hoverinfo='label+percent', textinfo='label+value+percent', textfont_size=15, textposition='inside')
    fig.update_layout( margin=dict(t=0, b=0, l=0, r=0),
            
                        font=dict(
                family="Verdana",
                size=12,
                color="DarkBlue"
            ), showlegend=False, width=500
                        )
    
    
    #fig.show()
    fig.write_image("figures/pie.png")




def trim(im):

    #
    #   Helper function to trim the image from white margins
    #   Input: Image
    #   Output: Trimmed image
    #

    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def generate_wordcloud(tokenized_text, path_to_mask='resources/mask.npy', colormap='viridis', background_color='white', max_words=100):

    #
    #   Create a word cloud of most popular words in the conversation.
    #   Input: Python list of tokens prepared by tokenize_messages in prepocessing_utils
    #   Output: Word Cloud image 
    #
    
    text = " ".join(tokenized_text)
   
    mask = np.load(path_to_mask)

    cloud = WordCloud(scale=3,
                      max_words=max_words,
                      colormap=colormap,
                      mask=mask,
                      background_color=background_color,
               
                      collocations=True).generate_from_text(text)
    
    img = Image.fromarray(cloud.to_array())
    img = trim(img)
   # plt.figure(figsize=(10,6))
   # plt.imshow(cloud)
   # plt.axis('off')
  
    img.save("figures/wordcloud.png")

 


def create_transparent_image_with_text(width, height, text):

    #
    #   Create an image with message, which fits the provided bounding box.
    #   Input: width (px), height (px) and text to be placed.
    #   Output: Image 
    #


    # Create a new transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Get a drawing context
    draw = ImageDraw.Draw(img)
    
    # Initialize the font size and set the font
    font_size = 1
    font = ImageFont.truetype('arial.ttf', font_size)
    lines = textwrap.wrap(text, width=120)
    # Loop until the text fits entirely within the image
    while True:
        # Get the size of the text
        
        line_width = [draw.textbbox((0,0), line, font=font)[2] for line in lines]
        line_heights = [draw.textbbox((0,0), line, font=font)[3] for line in lines]
        text_height = sum(line_heights)
        text_width = max(line_width)
  
        y = (height - text_height) / 2
        
        # Check if the text fits entirely within the image
        if text_width >= width or text_height >= height:
            font_size -= 1
            font = ImageFont.truetype('arial.ttf', font_size)
            break
        else:
            # Increase the font size and set the new font
            font_size += 1
            font = ImageFont.truetype('arial.ttf', font_size)
        
    # Draw the text
    y_offset = 0
    for line, line_height in zip(lines, line_heights):
        text_bbox = draw.textbbox((0, 0), line, font=font)
        x_offset = (width - text_bbox[2]) / 2
        draw.text((x_offset , y + y_offset), line, fill=(255, 255, 255, 255), font=font)
        y_offset += line_height
    
    return img
