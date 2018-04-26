"""
Code was written following an online guide from http://www.karsdorp.io/python-course/
Unless noted, all code was written by me

Functions to preprocesses text files.

TO DO: Create functions to extract data from multiple txt files
 """

from os import listdir
 
def read_file(filename):
    "Read the contents of FILENAME and return as a string."
    infile = open(filename) # windows users should use codecs.open after importing codecs
    contents = infile.read()
    infile.close()
    return contents 
 
 #Code taken from guide
def remove_punc(text):
    "Removes punctation from a text."
    punctuation = '!#$%^&*()+={}[]:;"\'|<>,.?/~`'
    clean_text = ""
    for character in text:
        if character not in punctuation:
            clean_text += character.lower()
    return clean_text

def clean_text(text):
    return remove_punc(text)

#Fucntion written by me 
def end_of_sentence_marker(character):
    """Returns True if the character is a period, question mark, or exclaimation point."""
    sentence_marker = ".?!"
    if character in sentence_marker:
        return True
    else:
        return False

#Most of function taken from class.
"""I added code that covers an edge case where the text is a single sentence with no punctuation.
While covering this edge case might seem not very useful, it proves useful when trying to tokenize text that is missing punctuation. 
"""
def split_sentences(text):
    """Split a text string into a list of sentences."""
    sentences = []
    start = 0
    for end, character in enumerate(text):
        if end_of_sentence_marker(character):
            sentence = text[start: end + 1]
            sentences.append(sentence)
            start = end + 1
    if len(sentences) == 0:
        sentences.append(text)
    return sentences

#Functin written by me    
def tokenize(text):
    """Transform TEXT into a list of sentences. Lowercase 
    each sentence and remove all punctuation. Finally split each
    sentence into a list of words."""
    tokens = []
    sentences = split_sentences(text)
    if sentences == []:
        sentence = remove_punc(sentences)
        words = sentence.split()
        tokens.append(words)
        return tokens  
    for sentence in sentences:
        sentence = remove_punc(sentence)
        words = sentence.split()
        tokens.append(words)
    return tokens
    
def list_textfiles(directory):
    "Return a list of filenames ending in '.txt' in DIRECTORY."
    textfiles = []
    for filename in listdir(directory):
        if filename.endswith(".txt"):
            textfiles.append(directory + "/" + filename)
    return textfiles

def make_twittercorpus(directory):
    corpus = ""
    num_files = len(list_textfiles(directory))
    count = 0
    for filepath in list_textfiles(directory):
        text = read_file(filepath)
        corpus += text
        count += 1
        print(str(count) +" files of "+str(num_files)+" added to corpus")

    return split_tweet(corpus)

def split_tweet(corpus):
    prev = 0 
    count = 0
    tweets = []
    for index, char in enumerate(corpus):
        if count is 0:
            if char is "\t":
                username = corpus[prev:index]
                prev = index+1
                count = 1
                
            elif char is "\n":
                count = 0
                prev = index+1
                
        elif count is 1:
            if char is "\t":
                time = corpus[prev:index]
                prev = index+1
                count = 2
            elif char is "\n":
                count = 0
                prev = index+1
                
        elif count is 2:
            if char is "\n":
                message = corpus[prev:index]
                prev = index+1
                count = 0
                tweets.append([username, time, message])
            elif char is "\t":
                count = 0
                prev = index+1
        
    return tweets

def get_username(text):
    punctuation = '!#$%^&*()+={}[]:;"\'|<>,.?/~`'
    clean_text = ''
    for character in text:
        if character not in punctuation:
            clean_text += character.lower()
        else:
            return clean_text
    return clean_text

