import React, { useState } from 'react';

function Uploader() {
  const [pdfFiles, setPdfFiles] = useState([]);

  const handleFileChange = (event) => {
    setPdfFiles(event.target.files); // Update state with the selected files
  };

  const handleSubmit = async (event) => {
    event.preventDefault(); // Prevent default form submission

    if (pdfFiles.length === 0) {
      alert('Please select at least one PDF file to upload.');
      return;
    }

    // Create a FormData object to hold the files
    const formData = new FormData();
    for (let i = 0; i < pdfFiles.length; i++) {
      formData.append('pdf_files', pdfFiles[i]); // Append each file to form data
    }

    try {
      // Send a POST request to the Django REST API
      const response = await fetch('http://localhost:8000/api/pdfs/', {  // Ensure this matches your Django API URL
        method: 'POST',
        body: formData, // Send the form data
      });

      if (response.ok) {
        alert('PDFs uploaded successfully!');
        setPdfFiles([]); // Clear the file input
      } else {
        alert('Failed to upload PDFs.');
        console.error('Failed to upload PDFs:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <h2>Upload PDF Files</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            PDF Files:
            <input
              type="file"
              accept="application/pdf"
              multiple // Allow multiple file selection
              onChange={handleFileChange}
            />
          </label>
        </div>
        <button type="submit">Upload PDFs</button>
      </form>
    </div>
  );
}

export default Uploader;
