from flask import Flask, render_template, request
#from flask_ngrok import run_with_ngrok
from model_processing import Model
from image_processing import ImageProcessing
from tts_api import TTSHandler
from PIL import Image
from difflib import SequenceMatcher
from itertools import product
import base64
import io
import csv

DETECT_PATH = 'models/detect_dialect_vgg16.h5'
MODEL_PATH = ['models/hanunuo_model_vgg16.h5', 'models/tagalog_model_vgg16.h5', 'models/tagbanwa_model_vgg16.h5']
#MODEL_PATH = ['models/hanunuo_model.h5', 'models/tagalog_model.h5', 'models/tagbanwa_model.h5']
CLASS_PATH = ['hanunuo_classes.txt', 'tagalog_classes.txt', 'tagbanwa_classes.txt']
DIALECT = ['Hanunuo', 'Tagalog', 'Tagbanwa']
API_KEY = '14f3d8372a47419ca51681c347744614'
app = Flask(__name__)
#run_with_ngrok(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        f = request.files['img']
        img = Image.open(io.BytesIO(f.read()))
        out, dialect = process_input(img)
        i = io.BytesIO()
        img.save(i, "PNG")
        enc_img = base64.b64encode(i.getvalue())
        tts = TTSHandler(API_KEY)
        speech = tts.convert_to_speech(out)
        return render_template('display.html', img=enc_img.decode('utf-8'), out=out, tts=speech, dialect=dialect)
    else:
        return render_template('capture.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


def process_input(input_img):
    img = ImageProcessing()

    # Comment out below if you want to test models manually
    # Convert Image to Array
    bounding_boxes = img.get_rect(input_img)
    chars = img.separate_chars(input_img, bounding_boxes)

    # Comment out below if you want to test models manually
    # Detect Dialect
    dialect_detect = Model(DETECT_PATH)

    # detect dialect using the first character
    dialect = dialect_detect.get_prediction(chars[0])
    # dialect = 1

    # change dialect var to corresponding index number for MODEL_PATH and CLASS_PATH
    # OCR
    ocr = Model(MODEL_PATH[dialect])
    print(MODEL_PATH[dialect])

    translation = ocr.get_prediction(chars, class_file=CLASS_PATH[dialect])

    # change machine prediction to the proper word via dictionary
    if 'e' in translation or 'i' in translation or 'o' in translation or 'u' in translation or 'd' in translation or 'r' in translation:
        print(translation)

        # get all possible word combinations using a dictionary and the zip() and itertools product()
        # needs further improvements to add more combinations
        word_dict = {'e': ['i'], 'o': ['u'], 'd': ['r']}
        trans_res = []  # list for all possible combinations of translation
        for key in word_dict.keys():
            if key not in word_dict[key]:
                word_dict[key].append(key)

        for sub in [zip(word_dict.keys(), chr) for chr in product(*word_dict.values())]:
            temp = translation
            for repls in sub:
                temp = temp.replace(*repls)
            if temp not in trans_res:
                trans_res.append(temp)

        # data dictionary part
        # compares the trans_res to the data dictionary
        # gets the ratio of each word comparison and picks the highest ratio among all of it
        temp = 0.0
        with open('dictionary.csv', 'rt') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                for field in row:
                    if len(field) == len(translation):
                        for tr in trans_res:
                            matcher = SequenceMatcher(a=field, b=tr).ratio()
                            if matcher > temp:
                                temp = matcher
                                tempWord = field
                                print(temp, tempWord)
        translation = tempWord

    # use for detecting the number of characters, for testing and can be seen in the terminal
    print("number of detected characters:", len(chars))

    return translation, DIALECT[dialect]


if __name__ == '__main__':
    app.run(debug=True)
    #app.run()  # tried with debug=true but not working with ngrok
