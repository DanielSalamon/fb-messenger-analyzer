from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_transparent_image_with_text(width, height, text, linewidth):
    """
    Creates an image with the specified dimensions and places the provided text at the center.

    Args:
        width (int): The width of the image in pixels.
        height (int): The height of the image in pixels.
        text (str): The text to be placed in the image.
        linewidth (int): The maximum width of each line of text.

    Returns:
        PIL.Image.Image: A transparent image with the text placed at the center.

    Description:
        This function creates a new transparent image with the specified dimensions and then places the provided
        text at the center of the image. The text is wrapped into multiple lines based on the specified line width.
        The function adjusts the font size to ensure that the entire text fits within the image. The resulting
        image with the centered text is returned.
    """

    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Get a drawing context
    draw = ImageDraw.Draw(img)
    
    # Initialize the font size and set the font
    font_size = 1
    font = ImageFont.truetype('arial.ttf', font_size)
    lines = textwrap.wrap(text, width=linewidth)
    # Loop until the text fits entirely within the image
    while True:
        # Get the size of the text
        
        line_width = [draw.textbbox((0,0), line, font=font)[2] for line in lines]
        line_heights = [draw.textbbox((0,0), line, font=font)[3] for line in lines]
        text_height = sum(line_heights)
        text_width = max(line_width)
      
        
        # Calculate the position of the text
        x = 0 #(width - text_width) / 2
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


def remove_polish_characters(input_text):

    """
    Removes Polish characters from the input text and returns the refined string.

    Args:
        input_text (str): The input text containing Polish characters.

    Returns:
        str: The refined string with Polish characters replaced by their corresponding non-Polish characters.

    Description:
        This function takes an input text as a string and removes Polish characters from it. It replaces each Polish character
        with its corresponding non-Polish character. The Polish characters and their corresponding replacements are as follows:
        
        - ł -> l
        - ą -> a
        - ę -> e
        - ż -> z
        - ź -> z
        - ó -> o
        - ś -> s
        - ć -> c
        - ń -> n
        
        The function iterates over each character in the input text and checks if it is a Polish character. If it is, the 
        corresponding non-Polish character is used in the refined string. If not, the original character is kept. The refined
        string is then returned as the output.
    """

    special_chars = dict(ł = 'l', ą = 'a', ę = 'e', ż = 'z', ź = 'z', ó = 'o', ś = 's', ć = 'c', ń = 'n')
    refined_string = ""
    for c in input_text:
       
        refined_string += special_chars[c] if c in special_chars.keys() else c
    return refined_string
    


def create_main_page(stats, most_common, badges, conversation_title):

    """
    Creates the main page of a PDF document with statistics, visualizations, and badges.

    Args:
        stats (dict): A dictionary containing various statistics.
        most_common (list): A list of tuples containing the most common words and their frequencies.
        badges (dict): A dictionary containing badges in different categories.
        conversation_title (str): The title of the conversation.

    Returns:
        FPDF: An instance of the FPDF class representing the generated PDF document.

    Description:
        This function creates the main page of a PDF document with statistics, visualizations, and badges. It takes several
        inputs including statistics, most common words, badges, and the conversation title. The function uses the FPDF library
        to create the PDF document.

        The main page layout consists of various elements such as images, text cells, and fonts. The function sets the page
        orientation, unit, and format. It adds a new page to the PDF document and positions the elements on the page.

        The function uses the provided statistics, most common words, and badges to populate the page with relevant
        information. It sets the font, text color, and coordinates to position the text cells containing the statistics,
        most common words, and badges. Polish characters are removed from the badges using the `remove_polish_characters`
        function.

        The first message of the conversation is also displayed on the main page. It is converted into an image using the
        `create_transparent_image_with_text` function and saved as a PNG file. The image is then inserted into the PDF document.

        Finally, the conversation title is displayed at the top of the page using a specific font, text color, and alignment.

        The function returns an instance of the FPDF class representing the generated PDF document.
    """
    
    pdf = FPDF(orientation = 'L', unit = 'mm', format = 'A4')
    pdf.set_auto_page_break(False)
    pdf.add_page()

    pdf.image('templates/template_main.png', x = 0, y = 0, w = 297, h = 210)
    pdf.image('figures/pie.png', x = 205, y = 3, w = 70, h = 70)
    pdf.image('figures/wordcloud.png', x = 70, y = 82, w = 95, h = 60)

    pdf.set_font('helvetica', 'B', 18)
    pdf.set_text_color(33, 131, 128)
    
    pdf.set_xy(x = 9, y = 45)
    pdf.cell(w = 25, h = 10, txt = str(stats["total_messages"]), border=0, align="C", fill=False)
    
    pdf.set_xy(x = 52, y = 45)
    pdf.cell(w = 15, h = 10, txt = str(stats["total_reactions"]), border=0, align="C", fill=False)
    
    pdf.set_xy(x = 91.5, y = 45)
    pdf.cell(w = 20, h = 10, txt = str(stats["avg_message_length"]), border=0, align="C", fill=False)
    
    pdf.set_xy(x = 131.5, y = 45)
    pdf.cell(w = 32, h = 10, txt = str(stats["most_busy_day"]), border=0, align="C", fill=False)


    # Most common words section

    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(33, 131, 128)

    
    pdf.set_xy(x = 16, y = 100)
    pdf.cell(w = 40, h = 5, txt = most_common[0][0] + " - " + str(most_common[0][1]), border=0, align="L", fill=False)
    
    pdf.set_xy(x = 16, y = 111)
    pdf.cell(w = 40, h = 5, txt = most_common[1][0] + " - " + str(most_common[1][1]), border=0, align="L", fill=False)
    
    pdf.set_xy(x = 16, y = 122.5)
    pdf.cell(w = 40, h = 5, txt = most_common[2][0] + " - " + str(most_common[2][1]), border=0, align="L", fill=False)
    
    pdf.set_xy(x = 16, y = 133.5)
    pdf.cell(w = 40, h = 5, txt = most_common[3][0] + " - " + str(most_common[3][1]), border=0, align="L", fill=False)
    
    pdf.set_xy(x = 16, y = 145)
    pdf.cell(w = 40, h = 5, txt = most_common[4][0] + " - " + str(most_common[4][1]), border=0, align="L", fill=False)


    # Badges
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(33, 131, 128)

    # The Messenger
    badges["Messenger"] = [remove_polish_characters(i) for i in badges["Messenger"]]
    pdf.set_xy(x = 182, y = 118.7)
    pdf.cell(w = 30, h = 3, txt = badges["Messenger"][0], border=0, align="L", fill=False)

    pdf.set_xy(x = 182, y = 124.5)
    pdf.cell(w = 30, h = 3, txt = badges["Messenger"][1], border=0, align="L", fill=False)

    pdf.set_xy(x = 182, y = 130.2)
    pdf.cell(w = 30, h = 3, txt = badges["Messenger"][2], border=0, align="L", fill=False)

    # The Storyteller
    badges["Storyteller"] = [remove_polish_characters(i) for i in badges["Storyteller"]]
    pdf.set_xy(x = 244.5, y = 118.7)
    pdf.cell(w = 30, h = 3, txt = badges["Storyteller"][0], border=0, align="L", fill=False)

    pdf.set_xy(x = 244.5, y = 124.5)
    pdf.cell(w = 30, h = 3, txt = badges["Storyteller"][1], border=0, align="L", fill=False)

    pdf.set_xy(x = 244.5, y = 130.2)
    pdf.cell(w = 30, h = 3, txt = badges["Storyteller"][2], border=0, align="L", fill=False)

    # The Entertainer
    badges["Entertainer"] = [remove_polish_characters(i) for i in badges["Entertainer"]]
    pdf.set_xy(x = 182, y = 177.6)
    pdf.cell(w = 30, h = 3, txt = badges["Entertainer"][0], border=0, align="L", fill=False)

    pdf.set_xy(x = 182, y = 183.4)
    pdf.cell(w = 30, h = 3, txt = badges["Entertainer"][1], border=0, align="L", fill=False)

    pdf.set_xy(x = 182, y = 189)
    pdf.cell(w = 30, h = 3, txt = badges["Entertainer"][2], border=0, align="L", fill=False)

    # The Sensitivist
    badges["Sensitivist"] = [remove_polish_characters(i) for i in badges["Sensitivist"]]
    pdf.set_xy(x = 244.5, y = 177.6)
    pdf.cell(w = 30, h = 3, txt = badges["Sensitivist"][0], border=0, align="L", fill=False)

    pdf.set_xy(x = 244.5, y = 183.4)
    pdf.cell(w = 30, h = 3, txt = badges["Sensitivist"][1], border=0, align="L", fill=False)

    pdf.set_xy(x = 244.5, y = 189)
    pdf.cell(w = 30, h = 3, txt = badges["Sensitivist"][2], border=0, align="L", fill=False)


    # FIRST MESSAGE
    first_message_image = create_transparent_image_with_text(1000, 120, stats["first_message"], 120)
    first_message_image.save("figures/first_message.png", "PNG")
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(255, 255, 255)

    
    pdf.set_xy(x = 16, y = 172)
    pdf.image('figures/first_message.png', x = 16, y = 172, w = 142, h = 17)

    pdf.set_font('helvetica', 'B', 8)
    pdf.set_text_color(0, 0, 0)

    sender = remove_polish_characters(stats["first_message_sender"])
    pdf.set_xy(x = 128, y = 192)
    pdf.cell(w = 30, h = 3, txt = sender, border=0, align="C", fill=False)

    # Title
    pdf.set_font('helvetica', 'B', 26)
    pdf.set_text_color(255, 255, 255)

    pdf.set_xy(x = 16, y = 10)
    pdf.cell(w = 142, h = 17, txt = conversation_title, border=0, align="C", fill=False)

    return pdf