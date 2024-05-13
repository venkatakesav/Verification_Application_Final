from flask import Flask, render_template, jsonify, request, redirect
import os
import json

app = Flask(__name__, static_url_path='/static')

# Configuration variables
IMAGES_FOLDER = './static/images'
JSON_FILE = '/data/circulars/DATA/SyntheticDataGeneration/old_src/test_set/test_set1.json'
LOG_FILE = './checked_checkboxes.json'  # Path to the log file

# Load data from JSON file
with open(JSON_FILE, 'r') as file:
    data = json.load(file)
    # Convert data to a list of (image_name, questions_answers) tuples
    entries = list(enumerate(data))  # Enumerate to assign numbers to entries

# Check if the log file exists and is a regular file
if os.path.exists(LOG_FILE) and os.path.isfile(LOG_FILE):
    # Read existing log data
    with open(LOG_FILE, 'r') as file:
        checked_checkboxes = json.load(file)
else:
    # File doesn't exist, create a new file and write initial log data for each entry
    checked_checkboxes = {}
    with open(LOG_FILE, 'w') as file:
        json.dump(checked_checkboxes, file)

# Route to render the login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route to render the HTML template after successful login
@app.route('/')
def index():
    # Check if username is provided in the query parameters
    username = request.args.get('username')
    print("THE USERNAME IS", username)
    if not username:
        return redirect('/login')  # Redirect to login page if username is not provided
    return render_template('1.html', username=username)

# API endpoint to get image and corresponding questions/answers by entry number
@app.route('/image_data/<int:entry_number>')
def get_image_data(entry_number):
    global entries, checked_checkboxes

    # Ensure the entry number is within range
    if entry_number < 0 or entry_number >= len(entries):
        return jsonify({'error': 'Invalid entry number'})

    entry = entries[entry_number]
    image_filename = entry[1]['file_name']
    questions_answers = entry[1]['question_answer_pairs']

    # Load the checkbox log file dynamically
    with open(LOG_FILE, 'r') as log_file:
        checked_checkboxes = json.load(log_file)

    # Check if the image filename exists in the checked_checkboxes
    if image_filename in checked_checkboxes:
        qa_labels = checked_checkboxes[image_filename]
    else:
        qa_labels = {}

    # Construct response
    response = {
        'image': f'./static/images/{image_filename}',
        'questions_answers': questions_answers,
        'entry_number': entry_number,  # Include the entry number in the response
        'qa_labels': qa_labels
    }

    return jsonify(response)

# API endpoint to get the total number of entries
@app.route('/total_entries')
def get_total_entries():
    global entries
    return jsonify({'total_entries': len(entries)})

# Flask Route to Handle Logging Checked Checkboxes
@app.route('/log_checked_checkboxes', methods=['POST'])
def log_checked_checkboxes():
    try:
        print("Request Form", request.form) 

        username = request.form['username']  # Get username from request arguments
        print("The UserName is", username)
        # if not username:
        #     return jsonify({'success': False, 'error': 'Username not provided'})

        file_name = request.form['file_name']
        file_number = int(file_name.split('_')[1].split('.')[0])
        doc_id = entries[file_number][1]['file_name']
        print("Hello")

        checked_values = request.form.getlist('checked_values[]')

        # Load the checkbox log file
        with open(LOG_FILE, 'r') as log_file:
            checked_checkboxes = json.load(log_file)

        # Update the log data
        if doc_id not in checked_checkboxes:
            checked_checkboxes[doc_id] = {}

        for checked_value in checked_values:
            checked_value = eval(checked_value)
            question = checked_value['question']
            answer = checked_value['answer']
            annotation = list(checked_value.keys())[-1]

            edited_question = checked_value['edited_q']
            edited_answer = checked_value['edited_a']

            # Check if the question already exists
            existing_qa_pair_index = None
            for qa_index, data in checked_checkboxes[doc_id].items():
                if data['q_a_pair']['original_question'] == question:
                    existing_qa_pair_index = qa_index
                    break

            if existing_qa_pair_index is not None:
                # Update annotation for existing question-answer pair
                checked_checkboxes[doc_id][existing_qa_pair_index][annotation] = checked_value[annotation]
                checked_checkboxes[doc_id][existing_qa_pair_index]['q_a_pair']['edited_question'] = edited_question
                checked_checkboxes[doc_id][existing_qa_pair_index]['q_a_pair']['edited_answer'] = edited_answer
            else:
                # Assign a new index if the question is not found
                qa_index = len(checked_checkboxes[doc_id])

                # Store QA pair along with annotations
                qa_pair = {
                    'original_question': question,
                    'original_answer': answer,
                    'edited_question': '', 
                    'edited_answer': '',
                    'username': username  # Include the username in the QA pair
                }
                checked_checkboxes[doc_id][qa_index] = {'q_a_pair': qa_pair}

                # Store annotations
                checked_checkboxes[doc_id][qa_index][annotation] = checked_value[annotation]

        # Write the updated log data back to the file
        with open(LOG_FILE, 'w') as log_file:
            json.dump(checked_checkboxes, log_file)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Change to port 5001
if __name__ == '__main__':
    app.run(debug=True, port=5001)