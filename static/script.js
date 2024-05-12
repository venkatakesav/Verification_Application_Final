document.addEventListener('DOMContentLoaded', function() {
  let currentEntry = 0; // Variable to keep track of the current entry number

  // Function to fetch image data from Flask backend
  function getImageData(entryNumber) {
      fetch(`/image_data/${entryNumber}`)
          .then(response => response.json())
          .then(data => {
              console.log(data)
              console.log('Entry Nunber', data)
              // Set image source dynamically
              document.getElementById('displayedImage').src = data.image;

              // Clear previous questions and answers
              const qaList = document.getElementById('qaList');
              qaList.innerHTML = '';
              console.log('data.qa_labels', data.qa_labels)

              // Populate questions and answers
              data.questions_answers.forEach((qa, index) => {
                  const questionItem = document.createElement('li');
                  const questionHeader = document.createElement('h3');
                  questionHeader.textContent = qa.question;
                  questionItem.appendChild(questionHeader);

                  const answerParagraph = document.createElement('p');
                  answerParagraph.textContent = qa.answer;
                  questionItem.appendChild(answerParagraph);

                  // Add checkboxes for each question
                  const typeCheckboxes = createCheckboxGroup('Type', ['Abstractive', 'Extractive'], `type-${index}`);
                  const layoutCheckboxes = createCheckboxGroup('Layout Region', ['Signature Block', 'Circular ID', 'Reference Block', 'Table Block', 'Subject Block', 'Header Block', 'Copy Forwarded To Block', 'Addressed To Block', 'Address of Issuing Authority', 'Date Block', 'Address Block', 'Stamps and Seals Block', 'Logo Block', 'Body Block'], `layout-${index}`);
                  const languageCheckboxes = createCheckboxGroup('Language', ['Hindi', 'English', 'Other'], `language-${index}`);
                  const complexityCheckboxes = createCheckboxGroup('Complexity', ['Simple', 'Complex', 'Layout Based'], `complexity-${index}`);
                  const removeCheckboxes = createCheckboxGroup('REMOVE', ['Remove'], `remove-${index}`);

                  // Check checkboxes based on qa_labels data
                  data.qa_labels.forEach(qa_label => {
                      if (qa_label.question === qa.question) {
                          // Check Type checkbox
                          typeCheckboxes.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                              if (checkbox.value === qa_label.Type) {
                                  checkbox.checked = true;
                              }
                          });

                          // Check Layout Region checkbox
                          layoutCheckboxes.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                              if (checkbox.value === qa_label['Layout Region']) {
                                  checkbox.checked = true;
                              }
                          });

                          // Check Language checkbox
                          languageCheckboxes.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                              if (checkbox.value === qa_label.Language) {
                                  checkbox.checked = true;
                              }
                          });

                          // Check Complexity checkbox
                          complexityCheckboxes.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                              if (checkbox.value === qa_label.Complexity) {
                                  checkbox.checked = true;
                              }
                          });

                          // Check REMOVE checkbox
                          removeCheckboxes.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                              if (checkbox.value === qa_label.REMOVE) {
                                  checkbox.checked = true;
                                  questionItem.style.textDecoration = 'line-through';
                              }
                          });
                      }
                  });

                  questionItem.appendChild(typeCheckboxes);
                  questionItem.appendChild(layoutCheckboxes);
                  questionItem.appendChild(languageCheckboxes);
                  questionItem.appendChild(complexityCheckboxes);
                  questionItem.appendChild(removeCheckboxes);

                  qaList.appendChild(questionItem);
              });

              // Update the displayed entry number
              document.getElementById('entryNumber').textContent = `Entry Number: ${entryNumber}`;
          })
          .catch(error => console.error('Error fetching image data:', error));
  }

    function createCheckboxGroup(label, options, groupName) {
      const container = document.createElement('div');
      const groupLabel = document.createElement('h4');
      groupLabel.textContent = label;
      container.appendChild(groupLabel);
  
      options.forEach(option => {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = `${groupName}-${label.replace(' ', '')}`;
        checkbox.value = option;
  
        const labelElement = document.createElement('label');
        labelElement.textContent = option;
  
        // Add event listener for the "REMOVE" checkbox group
        if (label === 'REMOVE') {
          checkbox.addEventListener('change', function() {
            const questionItem = this.parentElement.parentElement;
            if (this.checked) {
              questionItem.style.textDecoration = 'line-through';
            } else {
              questionItem.style.textDecoration = 'none';
            }
          });

          // Add a class to the container for the "REMOVE" group
          container.classList.add('remove-checkbox-group');
        }
  
        container.appendChild(checkbox);
        container.appendChild(labelElement);
      });
  
      return container;
    }
  
    // Fetch initial image data when the page loads
    getImageData(currentEntry);
  
    // Function to handle fetching image data for a specific entry
    function goToEntry() {
      const entryNumberInput = document.getElementById('entryNumberInput').value;
      if (entryNumberInput !== '') {
        currentEntry = parseInt(entryNumberInput);
        getImageData(currentEntry);
      }
    }
  
    // Event listener for the "Go to Entry" button
    const goToEntryButton = document.getElementById('goToEntryButton');
    goToEntryButton.addEventListener('click', goToEntry);
  
    // Button to fetch next image data
    const nextButton = document.getElementById('nextButton');
    nextButton.addEventListener('click', function() {
      currentEntry++; // Increment the current entry number
      getImageData(currentEntry);
    });
  
    // Button to fetch previous image data
    const previousButton = document.getElementById('previousButton');
    previousButton.addEventListener('click', function() {
      if (currentEntry > 0) {
        currentEntry--; // Decrement the current entry number
        getImageData(currentEntry);
      }
    });

    const logCheckedButton = document.getElementById('logCheckedButton');
    logCheckedButton.addEventListener('click', function() {
        const checkedCheckboxes = document.querySelectorAll('input[type="checkbox"]:checked');
        const checkedValues = Array.from(checkedCheckboxes).map(checkbox => {
            const groupName = checkbox.name.split('-')[0];
            const groupLabel = checkbox.parentElement.querySelector('h4').textContent;
            const value = checkbox.value;
            const question = checkbox.parentElement.parentElement.querySelector('h3').textContent;
            return {
                question: question,
                answer: checkbox.parentElement.parentElement.querySelector('p').textContent,
                [groupLabel]: value
            };
        });

        console.log('Checked Values:', checkedValues);

        // Log checked checkboxes
        if (checkedValues.length > 0) {
            const formData = new FormData();
            formData.append('file_name', `File_${currentEntry}.txt`);
            checkedValues.forEach(value => formData.append('checked_values[]', JSON.stringify(value)));
            console.log("Logging", formData)
            fetch('/log_checked_checkboxes', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    console.log('Checked checkboxes logged successfully.');
                } else {
                    console.error('Failed to log checked checkboxes.');
                }
            })
            .catch(error => console.error('Error logging checked checkboxes:', error));
        } else {
            console.log('No checkboxes are checked.');
        }
    });
});
