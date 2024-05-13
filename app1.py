from flask import Flask, render_template, jsonify, request, redirect
from flask_socketio import SocketIO, emit
import os
import json

app = Flask(__name__, static_url_path='/static')
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration variables
IMAGES_FOLDER = './static/images'
JSON_FILE = '/data/circulars/DATA/SyntheticDataGeneration/old_src/test_set/test_set1.json'
LOG_FILE = './checked_checkboxes.json'

# Load data from JSON file
with open(JSON_FILE, 'r') as file:
    data = json.load(file)
    entries = list(enumerate(data))

if os.path.exists(LOG_FILE) and os.path.isfile(LOG_FILE):
    with open(LOG_FILE, 'r') as file:
        checked_checkboxes = json.load(file)
else:
    checked_checkboxes = {}
    with open(LOG_FILE, 'w') as file:
        json.dump(checked_checkboxes, file)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def index():
    username = request.args.get('username')
    if not username:
        return redirect('/login')
    return render_template('1.html', username=username)

@app.route('/image_data/<int:entry_number>')
def get_image_data(entry_number):
    if entry_number < 0 or entry_number >= len(entries):
        return jsonify({'error': 'Invalid entry number'})

    entry = entries[entry_number]
    image_filename = entry[1]['file_name']
    questions_answers = entry[1]['question_answer_pairs']

    with open(LOG_FILE, 'r') as log_file:
        checked_checkboxes = json.load(log_file)

    if image_filename in checked_checkboxes:
        qa_labels = checked_checkboxes[image_filename]
    else:
        qa_labels = {}

    response = {
        'image': f'./static/images/{image_filename}',
        'questions_answers': questions_answers,
        'entry_number': entry_number,
        'qa_labels': qa_labels
    }
    return jsonify(response)

@app.route('/total_entries')
def get_total_entries():
    return jsonify({'total_entries': len(entries)})

@app.route('/log_checked_checkboxes', methods=['POST'])
def log_checked_checkboxes():
    try:
        username = request.form['username']
        file_name = request.form['file_name']
        file_number = int(file_name.split('_')[1].split('.')[0])
        doc_id = entries[file_number][1]['file_name']

        checked_values = request.form.getlist('checked_values[]')

        with open(LOG_FILE, 'r') as log_file:
            checked_checkboxes = json.load(log_file)

        if doc_id not in checked_checkboxes:
            checked_checkboxes[doc_id] = {}

        for checked_value in checked_values:
            checked_value = eval(checked_value)
            question = checked_value['question']
            answer = checked_value['answer']
            annotation = list(checked_value.keys())[-1]

            edited_question = checked_value['edited_q']
            edited_answer = checked_value['edited_a']

            existing_qa_pair_index = None
            for qa_index, data in checked_checkboxes[doc_id].items():
                if data['q_a_pair']['original_question'] == question:
                    existing_qa_pair_index = qa_index
                    break

            if existing_qa_pair_index is not None:
                checked_checkboxes[doc_id][existing_qa_pair_index][annotation] = checked_value[annotation]
                checked_checkboxes[doc_id][existing_qa_pair_index]['q_a_pair']['edited_question'] = edited_question
                checked_checkboxes[doc_id][existing_qa_pair_index]['q_a_pair']['edited_answer'] = edited_answer
            else:
                qa_index = len(checked_checkboxes[doc_id])
                qa_pair = {
                    'original_question': question,
                    'original_answer': answer,
                    'edited_question': '', 
                    'edited_answer': '',
                    'username': username
                }
                checked_checkboxes[doc_id][qa_index] = {'q_a_pair': qa_pair}
                checked_checkboxes[doc_id][qa_index][annotation] = checked_value[annotation]

        with open(LOG_FILE, 'w') as log_file:
            json.dump(checked_checkboxes, log_file)

        # Notify all clients about the update
        socketio.emit('update', {'file_name': file_name, 'checked_checkboxes': checked_checkboxes[doc_id]}, broadcast=True)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)
