# Flask Annotation Application

This Flask-based web application enables users to annotate images with questions and answers, supporting concurrent access and real-time updates. The application uses Flask for the backend, JavaScript for dynamic client-side functionality, and Flask-SocketIO for real-time communication.

## Features

- User authentication and redirection to unannotated documents.
- Dynamic loading and annotation of images based on questions and answers.
- Real-time updates across multiple sessions using WebSockets.
- Indexing and display of document names and questions/answers for clarity.

## Getting Started

### Prerequisites

Before you start, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Node.js and npm (for JavaScript dependencies)

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

2. **Set Up a Python Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Python Dependencies**

   ```bash
   pip install Flask flask-socketio eventlet
   ```

4. **Install JavaScript Dependencies**

   Navigate to the directory containing your `package.json`, then run:

   ```bash
   npm install
   ```

### Directory Structure

Ensure your project directory is structured as follows:

```
/your-repository
    /static
        /images               # Folder to store images for annotation
    /templates
        1.html                # Main annotation interface template
        login.html            # Login page template
    app.py                    # Flask main application file
    checked_checkboxes.json   # Logs of annotations
    package.json              # Node.js dependencies and scripts
    README.md
```

### Preparing Data

1. **Add Images**

   Place all images you want to annotate in the `/static/images` directory.

   ```plaintext
   /static/images
       image1.png
       image2.jpg
       ...
   ```

2. **Prepare the JSON Data**

   Create a JSON file that contains the mappings between images and their corresponding questions and answers. The structure should be as follows:

   ```json
   [
     {
       "file_name": "image1.png",
       "question_answer_pairs": [
         {
           "question": "What is shown in the image?",
           "answer": "A cat sitting on a mat."
         },
         {
           "question": "What color is the cat?",
           "answer": "The cat is orange."
         }
       ]
     },
     {
       "file_name": "image2.jpg",
       "question_answer_pairs": [
         {
           "question": "What time of day is it in the image?",
           "answer": "It looks like dusk."
         },
         {
           "question": "What is in the background?",
           "answer": "There are mountains in the background."
         }
       ]
     }
   ]
   ```

   Save this file as `test_set1.json` in a suitable directory. Update the `app.py` `JSON_FILE` path accordingly.

   ```python
   JSON_FILE = './path/to/your/test_set1.json'
   ```

### Usage

1. **Start the Flask Application**

   Run the following command in the root of your project directory:

   ```bash
   python app.py
   ```

2. **Access the Application**

   Open a web browser and navigate to `http://localhost:5001/login`. Log in with a username to start annotating images.

## Contributing

Contributions to this project are welcome! Here are some ways you can contribute:
- Reporting bugs
- Suggesting enhancements
- Sending pull requests with fixes and new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.