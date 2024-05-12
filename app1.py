from flask import Flask, render_template, jsonify, request
import os
import json

app = Flask(__name__, static_url_path='/static')

# Configuration variables
IMAGES_FOLDER = './static/images'
JSON_FILE = '/data/circulars/DATA/SyntheticDataGeneration/old_src/test_set/test_set1.json'
LOG_FILE = './checked_checkboxes1.log'  # Path to the log file

# Load data from JSON file
with open(JSON_FILE, 'r') as file:
    data = json.load(file)
    # Convert data to a list of (image_name, questions_answers) tuples
    entries = list(enumerate(data))  # Enumerate to assign numbers to entries
    print("Entries: ", len(entries))

# Check if the log file exists and is a regular file
if os.path.exists(LOG_FILE) and os.path.isfile(LOG_FILE):
    # Check if the file is empty
    if os.path.getsize(LOG_FILE) == 0:
        # Write initial log data for each entry
        with open(LOG_FILE, 'w') as file:
            for i in range(len(entries)):
                file.write(f"File_{i}.txt:\n")
    else:
        # Read existing log data
        with open(LOG_FILE, 'r') as file:
            existing_content = file.readlines()

        # Append new content if needed
        with open(LOG_FILE, 'a') as file:
            if len(existing_content) < len(entries):
                for i in range(len(existing_content), len(entries)):
                    file.write(f"File_{i}.txt:\n")
else:
    # File doesn't exist, create a new file and write initial log data for each entry
    with open(LOG_FILE, 'w') as file:
        for i in range(len(entries)):
            file.write(f"File_{i}.txt:\n")

# Route to render the HTML template
@app.route('/')
def index():
    return render_template('1.html')

# API endpoint to get image and corresponding questions/answers by entry number
@app.route('/image_data/<int:entry_number>')
def get_image_data(entry_number):
    global entries
    # Ensure the entry number is within range
    if entry_number < 0 or entry_number >= len(entries):
        return jsonify({'error': 'Invalid entry number'})

    entry = entries[entry_number]
    image_filename = entry[1]['file_name']
    questions_answers = entry[1]['question_answer_pairs']

    print("File name: ", image_filename)

    qa_labels = []

    # Load the checkbox log file
    checked_checkboxes = {}
    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            lines = log_file.readlines()
            if lines[entry_number].strip() != f"File_{entry_number}.txt:":
                line = lines[entry_number]
                content = line.strip().split('.txt:')[-1].strip()
                content = content.split(',')
                print("CONTENT", content)
                print("Line", line.strip().split('.txt:')[-1])
                for i in range(len(content)):
                    print("Content: ", content[i])
                    question = content[i].split("?:")[0].strip()
                    answer = content[i].split(":")[-1].strip()
                    if answer == "Extractive" or answer == "Abstractive":
                        q_type = "Type"
                    if answer == "English" or answer == "Hindi":
                        q_type = "Language"
                    if answer == "Complex" or answer == "Simple" or answer == "Layout Based":
                        q_type = "Complexity"
                    if answer == "Table Block" or answer == "Reference Block" or answer == "Circular ID" or answer == "Text Block" or answer == "Subject Block" or answer == "Header Block" or answer == "Copy Forwarded To Block" or answer == "Addressed To Block" or answer == "Address of Issuing Authority" or answer == "Date Block" or answer == "Address Block" or answer == "Stamps and Seals Block" or answer == "Logo Block" or answer == "Body Block":
                        q_type = "Layout Region"
                    if answer == "Remove":
                        q_type = "REMOVE"

                    # print("Question: ", question)
                    # print("Answer: ", answer)
                    print("Type: ", q_type)
                    if qa_labels == []:
                            qa_labels.append({'question': question + '?', q_type: answer})
                    else:
                        # Check if q_type already exists in qa
                        for qa in qa_labels:
                            if qa['question'] == question + '?':
                                qa[q_type] = answer  # Corrected assignment operator
                                break
                        else:
                            qa_labels.append({'question': question + '?', q_type: answer})  # Add new qa if not found

    # Check if the current document has any checked checkboxes
    checked_values = checked_checkboxes.get(image_filename, [])

    # Construct response
    response = {
        'image': f'./static/images/{image_filename}',
        'questions_answers': questions_answers,
        'entry_number': entry_number,  # Include the entry number in the response
        'qa_labels': qa_labels
    }

    # print("Response", response)

    return jsonify(response)


# API endpoint to get the total number of entries
@app.route('/total_entries')
def get_total_entries():
    global entries
    return jsonify({'total_entries': len(entries)})

# Route to handle logging checked checkboxes
@app.route('/log_checked_checkboxes', methods=['POST'])
def log_checked_checkboxes():
    try:
        file_name = request.form['file_name']
        checked_values = request.form.getlist('checked_values[]')

        # Check if the log file exists
        if not os.path.isfile(LOG_FILE):
            # Create the log file if it doesn't exist
            with open(LOG_FILE, 'w') as log_file:
                log_file.write('')  # Write an empty string to create the file

        # Read existing log entries
        updated_lines = []
        entry_exists = False
        with open(LOG_FILE, 'r') as log_file:
            lines = log_file.readlines()

        # Update or add the new entry
        for line in lines:
            if line.startswith(file_name):
                updated_lines.append(f'{file_name}: {", ".join(checked_values)}\n')
                entry_exists = True
            else:
                updated_lines.append(line)

        if not entry_exists:
            updated_lines.append(f'{file_name}: {", ".join(checked_values)}\n')

        # Write updated entries back to the log file
        with open(LOG_FILE, 'w') as log_file:
            log_file.writelines(updated_lines)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


#change to port 5001
if __name__ == '__main__':
    app.run(debug=True, port=5001)
# if __name__ == '__main__':
#     app.run(debug=True)
