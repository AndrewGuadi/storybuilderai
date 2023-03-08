import openai
import random
import math
from time import time, sleep
from flask import Flask, render_template, request, jsonify, Response


app = Flask(__name__)

#openai variables (store as environment variable before deployment)
openai.organization = [ORGANIZATION]
openai.api_key = [API KEY]

#global varibables
messages = [
                {"role": "system", "content": "You are the most renowned author of our generation and everything you write is perfect."},
            ]


#basic functions
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def make_davinci_call(prompt, model='text-davinci-003', temp=0.8, top_p=1.0, n=1, best_of=1, tokens=2000, freq_pen=1.1, pres_pen=0.0):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    while True:
        try:
            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                n=n,
                best_of=best_of,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen)
            text = response['choices'][0]['text'].strip()
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

def make_gpt_call(prompt):
    
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    while True:
        try:
            global messages 
            #format for adding user message to conversation/messages
            user_format = {"role":"user", "content":prompt}
            messages.append(user_format)  #append to messages

            ##make the api call
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            message_response = completion.choices[0].message
            ##get text for interface display
            text = message_response.content
            #format assistant data for local conversation submission
            assitant_format = {"role":"assistant", "content":text}
            #add message_response to messages
            messages.append(assitant_format)
                       
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def create_story():
    prompt = "Now write the first 600 words of that story."
    story = make_gpt_call(prompt)
    return story

def finish_story():
    prompt = 'Now finish that story'
    story = make_gpt_call(prompt)
    return story

def divide_text_into_two_pages(input_string):
    # Step 1: Split the string into individual sentences
    sentences = input_string.split(".")
    
    # Step 2: Calculate the total number of sentences
    total_sentences = len(sentences)

    # Step 3: Divide the total number of sentences by 2 to get the target number
    target_sentences = total_sentences // 2

    # Step 4: Iterate through the list of sentences and create two new strings
    first_half = ""
    second_half = ""
    sentence_count = 0
    for sentence in sentences:
        if sentence_count < target_sentences:
            first_half += sentence + "."
        else:
            second_half += sentence + "."
        sentence_count += 1

    return first_half.strip(), second_half.strip()



#paths
@app.route("/")
def index():
    return render_template('home.html')

@app.route("/quick_build")
def quick_build():
    #pull random prompt
    prompt_text_array = ['SAMPLE_STORY_PROMPT']
    random_number = random.random()
    array_length = len(prompt_text_array)
    random_prompt_number = math.floor(random_number*array_length)
    random_prompt = prompt_text_array[random_prompt_number]
    ##extract text from document
    prompt = open_file('resources/quick_build_prompts/%s.txt' % random_prompt)
    story_format = make_gpt_call(prompt)
    text = create_story()
    two_pages = divide_text_into_two_pages(text)
    page1_text = two_pages[0]
    page2_text = two_pages[1]

    return render_template('index.html', page1_text=page1_text, page2_text=page2_text)

@app.route("/story_form", methods=['GET', 'POST'])
def story_form():

    if request.method =="POST":
        return render_template('index.html')
    else:
        return render_template('initial_story_form.html')


@app.route("/complete_story")
def complete_story():
    response = finish_story()
    text = divide_text_into_two_pages(response)
    page1_text = text[0]
    page2_text = text[1]

    return render_template('index.html', page1_text=page1_text, page2_text=page2_text)



###############################
#TEST DATA TEST DATA TEST DATA#
###############################
@app.route('/pages', methods=['GET', 'POST'])
def pages():
    if request.method == "GET":
        print("GET")
        prompt_text_array = ['action-adventure', 'comedy', 'drama', 'comedy', 'fantasy', 'historical_fiction', 'historical_romance', 'horror', 'military_war', 'mystery', 'spy', 'superhero']
        random_number = random.random()
        array_length = len(prompt_text_array)
        random_prompt_number = math.floor(random_number*array_length)
        random_prompt = prompt_text_array[random_prompt_number]
        ##extract text from document
        prompt = open_file('resources/quick_build_prompts/%s.txt' % random_prompt)
        print(prompt)
        prompt_data = prompt
        return render_template('index.html', text=prompt_data)
    
    if request.method == "POST":
        print("POST METHOD")
        author = request.form.get('author')
        genre = request.form.get('genre')
        user_books = request.form.get('books')
        prompt_document = open_file('resources/quick_build_prompts/adlib-prompt.txt').replace('<<genre>>', genre).replace('<<author>>', author).replace('<<user_books>>', user_books)
        print(prompt_document)
        return render_template('index.html', text=prompt_document)
    
@app.route('/stream')
def stream():
    value = request.args.get('prompt')
    print(value)
    response = Response(stream_response(value), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    return response

    

def stream_response(prompt, model='text-davinci-003', temp=0.8, top_p=1.0, n=1, best_of=1, tokens=3000, freq_pen=1.1, pres_pen=0.0):
    completion = openai.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=tokens,
        temperature=temp,
        top_p=1,
        n=n,
        presence_penalty=pres_pen,
        frequency_penalty=freq_pen,
        best_of=best_of,
        stream=True,
        
        )
    
    for obj in completion:
        try:
            text = obj.choices[0].text
            print(text, end="")
            yield f"data: {text}\n\n"
        except AttributeError:
            yield "data: [ERROR] No data available./n/n"

if __name__ == "__main__":
    app.run(debug=True)