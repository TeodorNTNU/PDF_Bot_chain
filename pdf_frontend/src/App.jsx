// import React, { useState } from 'react';
// 
// const PDFUploader = () => {
//   const [file, setFile] = useState(null);
//   const [fileName, setFileName] = useState('');
//   const [status, setStatus] = useState('initial');
// 
//   const handleFileChange = (e) => {
//     const selectedFile = e.target.files[0];
//     // Ensure the file is a PDF
//     if (selectedFile && selectedFile.type === 'application/pdf') {
//       setFile(selectedFile);
//       setFileName(selectedFile.name); // Set default file name as the name of the file
//       setStatus('initial');
//     } else {
//       alert('Please upload a valid PDF file.');
//     }
//   };
// 
//   const handleFileNameChange = (e) => {
//     setFileName(e.target.value);
//   };
// 
//   const handleUpload = async () => {
//     if (file && fileName) {
//       setStatus('uploading');
//       const formData = new FormData();
//       formData.append('file', file); // Key 'file' must match the key expected in Django's request.FILES
//       formData.append('file_name', fileName); // Append the file name to the form data
//   
//       try {
//         const response = await fetch('http://localhost:8000/upload-pdf/', {
//           method: 'POST',
//           body: formData,
//         });
//   
//         if (response.ok) {
//           // Ensure the response is JSON
//           const contentType = response.headers.get('content-type');
//           if (contentType && contentType.includes('application/json')) {
//             const data = await response.json();
//             console.log(data);
//             setStatus('success');
//           } else {
//             setStatus('fail');
//             alert('Unexpected response format.');
//           }
//         } else {
//           setStatus('fail');
//           // Attempt to parse the error message, or provide a generic error
//           try {
//             const errorData = await response.json();
//             alert(errorData.error || 'Upload failed.');
//           } catch (err) {
//             alert('Upload failed.');
//           }
//         }
//       } catch (error) {
//         console.error(error);
//         setStatus('fail');
//       }
//     } else {
//       alert('Please select a file and enter a file name.');
//     }
//   };
//   
// 
//   return (
//     <div>
//       <input type="file" accept="application/pdf" onChange={handleFileChange} />
//       {file && (
//         <>
//           <input
//             type="text"
//             value={fileName}
//             onChange={handleFileNameChange}
//             placeholder="Enter file name"
//           />
//           <button onClick={handleUpload}>
//             {status === 'uploading' ? 'Uploading...' : 'Upload PDF'}
//           </button>
//         </>
//       )}
//       {status === 'success' && <p>✅ PDF uploaded successfully!</p>}
//       {status === 'fail' && <p>❌ PDF upload failed!</p>}
//     </div>
//   );
// };
// 
// export default PDFUploader;
// 

// import React, { useState } from 'react';
// 
// function CreateItem() {
//   // State to hold the form input values
//   const [name, setName] = useState('');
//   const [description, setDescription] = useState('');
// 
//   // Function to handle form submission
//   const handleSubmit = async (event) => {
//     event.preventDefault(); // Prevent the default form submission
// 
//     if (name.trim() === '' || description.trim() === '') {
//       alert('Name and description are required.');
//       return;
//     }
//     // Create an object to hold the data to be sent to the server
//     const newItem = {
//       name: name,
//       description: description,
//     };
// 
//     try {
//       // Send a POST request to the Django REST API
//       const response = await fetch('http://localhost:8000/api/items/', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(newItem), // Convert JavaScript object to JSON
//       });
// 
//       if (response.ok) {
//         alert('Item created successfully!');
//         setName(''); // Clear the input fields
//         setDescription('');
//       } else {
//         alert('Failed to create item.');
//         console.error('Failed to create item:', response.statusText);
//       }
//     } catch (error) {
//       console.error('Error:', error);
//     }
//   };
// 
//   return (
//     <div>
//       <h2>Create a New Item</h2>
//       <form onSubmit={handleSubmit}>
//         <div>
//           <label>
//             Name:
//             <input
//               type="text"
//               value={name}
//               onChange={(e) => setName(e.target.value)} // Update state on input change
//             />
//           </label>
//         </div>
//         <div>
//           <label>
//             Description:
//             <textarea
//               value={description}
//               onChange={(e) => setDescription(e.target.value)} // Update state on input change
//             />
//           </label>
//         </div>
//         <button type="submit">Create Item</button>
//       </form>
//     </div>
//   );
// }
// 
// export default CreateItem;
// 

import React from 'react';
import Uploader from './Uploader'; // Import the Uploader component
import QaBot from './QaBot'; // Import the QaBot component

function App() {
  return (
    <div className="App">
      <h1>PDF Uploader and QA Chat Application</h1>
      
      {/* PDF Uploader Section */}
      <div style={{ marginBottom: '50px' }}>
        <h2>Upload PDF Files</h2>
        <Uploader /> {/* Render the Uploader component */}
      </div>
      
      {/* QA Chat Section */}
      <div>
        <h2>Chat with the QA Bot</h2>
        <QaBot /> {/* Render the QaBot component */}
      </div>
    </div>
  );
}

export default App;



