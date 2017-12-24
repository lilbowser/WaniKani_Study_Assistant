"""


"""


import logging
import re

import utils


from flask import Flask, render_template, json, request, redirect, url_for

from crabigator.wanikani import WaniKani



app = Flask(__name__)

data = None
""":type : Data"""


class Data:

    def __init__(self, file_name=None):
        key = utils.load_api_config('/secrets.yaml')['wanikani']
        self.wani = WaniKani(key)
        self.data = []
        self.file_name = file_name
        self.index = 0
        self.mode = 'vocab'
        self.generate_list_from_wanikani()


    def generate_list_from_wanikani(self):
        data_store = []

        vocab_study_list = []
        kanji_study_list = []
        for vocab in self.wani.vocabulary:
            if vocab.user_specific is not None:
                if vocab.user_specific.srs_numeric < 4:
                    vocab_study_list.append(vocab)

        for kanji in self.wani.kanji:
            if kanji.user_specific is not None:
                if kanji.user_specific.srs_numeric < 4:
                    kanji_study_list.append(kanji)

        if self.mode == 'vocab':
            self.data = vocab_study_list
        elif self.mode == 'kanji':
            self.data = kanji_study_list


    def generate_list_from_file(self):
        data_store = []

        with open(self.file_name + ".txt", encoding="utf-16") as data:  # , errors='replace'
            for line in data:
                # print(line)

                match = re.findall('(.*)\t(.*)', line)
                if len(match) > 0:
                    try:
                        if len(match[0][0]) > 0:
                            data_store.append((match[0][0], match[0][1]))
                        else:
                            # new char class
                            pass
                    except:
                        print(match)
                        raise RuntimeError(match)

            self.data = data_store

    def current_quest(self):
        if self.mode == 'vocab':
            return self.data[self.index].character
        elif self.mode == "kanji":
            raise NotImplementedError

    def current_kana_answer(self):
        if self.mode == 'vocab':
            return self.data[self.index].kana
        elif self.mode == "kanji":
            raise NotImplementedError

    def inc_index(self):

        if self.index < len(self.data)-1:
            self.index += 1
        else:
            self.index = 0


    def dec_index(self):

        if self.index == 0:
            self.index = len(self.data) - 1
        else:
            self.index -= 1

    def next(self):

        if self.index == len(self.data)-1:
            # At end of data
            return "End"
        else:
            self.inc_index()
            return self.index


    def previous(self):
        if self.index == 0:
            # At start of data
            return "Start"
        else:
            self.dec_index()
            return self.index


    def current_item(self):
        return self.data[self.index]


@app.route('/hello')
def hello_world():
    #  こんにちわ
    # return "Hello World!"

    if 'act' in request.args:
        if request.args['act'] == "next":
            data.inc_index()
        elif request.args['act'] == "previous":
            data.dec_index()

    html = """
    <body>
    <center>
        <h1>{}</h1>
        <form action="/test" target="_self" autocomplete="off">
            <br>
            <input type="text" name="answer" autofocus>
            <br>
            <input type="submit" value="Submit">
                        
        </form>
    </center>
    </body>
    
    """.format(data.current_item()[1])
    return html


@app.route('/')
def main_route():
    return hello_world()


@app.route('/test')
def test():

    if 'answer' in request.args:
        if request.args['answer'] == data.current_item()[0]:
            # return "Correct!"
            status = "Correct!"
        else:
            # return "Wrong!!!!!"
            status = """Wrong!
            Correct answer: {}""".format(data.current_item()[0])

        # data.inc_index()

        html = """
            <body>
            <center>
                <h1>{}</h1>
                <form action="/hello" target="_self" autocomplete="off">
                    <button name="act" type="submit" value="previous">Previous</button> 
                    <button name="act" type="submit" value="next" autofocus>Next</button> 
                    
                </form>
            </center>
            </body>

            """.format(status)
        return html

    else:
        return "No Answer Sent!"

    # return "こんにちわ"


@app.route("/refresh")
def refresh():
    data.wani.get_vocabulary()
    data.wani.get_level_progression()
    data.wani.get_kanji()
    data.wani.get_critical_items()
    data.wani.get_srs_distribution()
    data.generate_list_from_wanikani()
    return "Data Refreshed"


@app.route("/vocab", methods=['GET', 'POST'])
def vocab():
    func_name = "vocab"
    status = "Error!!!"
    correct = False

    if request.method == 'POST':

        if 'act' in request.form:
            # An action was submitted.
            action = request.form['act']
            if action == "next":
                data.inc_index()
            elif action == "previous":
                data.dec_index()
            return redirect(url_for(func_name))

        elif 'answer' in request.form:# and len(request.form['answer']) > 0:
            # an answer was submitted. Handle it and send user to next screen.
            if request.form['answer'] == data.current_kana_answer()[0]:  #TODO: Fix this to iterate over all posible answers
                status = "Correct!"
                correct = True
                data.inc_index()
                return redirect(url_for(func_name))
            else:
                status = """Incorrect<br>
                Correct answer: {}<br> Your answer: {}""".format(data.current_kana_answer()[0], request.form['answer'])

                html = """
                       <body>
                       <center>
                           <h1>{status}</h1>
                           <form action="/{loc}" target="_self" autocomplete="off" method="POST">
                               <button name="act" type="submit" value="previous">Previous</button> 
                               <button name="act" type="submit" value="next" autofocus>Next</button> 
                           </form>
                       </center>
                       </body>

                       """.format(status=status, loc=func_name)
                return html


    elif request.method == 'GET':

        html = """
           <body>
           <center>
               <h1>{status}</h1>
               <form action="/{loc}" target="_self" autocomplete="off" method="POST">
                   <input type="text" name="answer" autofocus>
                   <br>
                   <input type="submit" value="Submit">
                   <button name="act" type="submit" value="previous">Previous</button> 
                   <button name="act" type="submit" value="show">Show</button> 

               </form>
           </center>
           </body>

           """.format(status=data.current_quest(), loc=func_name)
        return html


@app.route("/post", methods=['GET', 'POST'])
def post():

    status = "Error!!!"
    if request.method == 'GET':
        status = "Choose One"

    if request.method == 'POST':
        status = request.form['act']

    html = """
                       <body>
                       <center>
                           <h1>{}</h1>
                           <form action="/post" target="_self" autocomplete="off" method="POST">
                               <button name="act" type="submit" value="previous">Previous</button> 
                               <button name="act" type="submit" value="next" autofocus>Next</button> 

                           </form>
                       </center>
                       </body>

                       """.format(status)
    return html


if __name__ == '__main__':

    data = Data("BaseInfo2")
    app.run(host="0.0.0.0", port=5000, debug=True)

