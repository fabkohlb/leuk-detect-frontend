import streamlit as st
import requests
from PIL import Image
import pandas as pd
from collections import Counter

# Make use of whole screen
st.set_page_config(layout="wide")

##### HEADER #####
st.markdown("""# Blood cancer prediction model
    Using deep learning (CNN) to detect immature leukocytes to identify patients suffering from Acute Myeloid Leukemia (AML).
    
    This model is trained on >18,000 cells to discriminate 15 leukocyte subclasses.
    
    Workflow
    1) Upload images
    2) Send images to API
    3) Perform prediction""")

##### SPLIT WEBSITE INTO 2 SIDES #####
cols = st.columns(2)

# Code for column 1 (left side)
with cols[0]:
    st.markdown("### Artificial patient (100 random selected cells)")
    
    # Create a 10x10 grid
    grid_size = 10
    grid_cols = [st.columns(grid_size) for _ in range(grid_size)]  # Store in a separate variable
    
    # Create an empty grid
    images = [[None for _ in range(grid_size)] for _ in range(grid_size)]
    
    ##### IMAGE UPLOAD #####
    uploaded_files = st.file_uploader("Upload Images", type=["jpg", "png", "jpeg", "tiff"], accept_multiple_files=True)
    
    if uploaded_files:
        uploaded_images = [Image.open(file) for file in uploaded_files[:100]]
        
        # Fill the grid with uploaded images
        index = 0
        for row in range(grid_size):
            for col in range(grid_size):
                if index < len(uploaded_images):
                    images[row][col] = uploaded_images[index]
                    index += 1
    
    # Display the grid
    for row in range(grid_size):
        for col in range(grid_size):
            with grid_cols[row][col]:
                if images[row][col]:
                    st.image(images[row][col], use_container_width=True) #caption=f"Image {row * grid_size + col + 1}", 
                else:
                    st.write("⬜")  # Placeholder for empty cells

# Code for column 2 (right side)
with cols[1]:
    
    #####  PREDICTION BUTTON #####
    st.write("**Prediction**")
    # Create a button that triggers the prediction when clicked
    if st.button("Predict"):
        # Define the URL of the prediction endpoint
        url = "http://127.0.0.1:8000/predict"

        # Send a POST request to the API
        response = requests.get(url)

        # Check if the response was successful
        if response.status_code == 200:
            # Parse the JSON response and extract the prediction value
            response_data = response.json()
            predictions = response_data.get("predictions", "No prediction found")
            #print(type(predictions))
            #print(predictions)
            
            # Mapping of numbers to labels of celltypes
            label_mapping = {0: 'BAS',
                            1: 'EBO',
                            2: 'EOS',
                            3: 'KSC',
                            4: 'LYA',
                            5: 'LYT',
                            6: 'MMZ',
                            7: 'MOB',
                            8: 'MON',
                            9: 'MYB',
                            10: 'MYO',
                            11: 'NGB',
                            12: 'NGS',
                            13: 'PMB',
                            14: 'PMO'
                            }
            
            # Prediction result header (for DataFrame) on frontend
            st.markdown("""
                        **Prediction result:**
                        """)
            
            # Count occurrences of filename prefixes (before '_')
            prefix_counts = Counter([item['filename'].split('_')[0] for item in predictions])

            # Count occurrences of predictions (numeric values)
            prediction_counts = Counter([item['prediction'] for item in predictions])

            # Convert prediction counts to full labels using label_mapping
            prediction_counts_full = {label_mapping.get(int(prediction), prediction): count for prediction, count in prediction_counts.items()}

            # Get all unique labels from both sources (filenames and predictions)
            all_labels = set(prefix_counts.keys()).union(set(prediction_counts_full.keys()))

            # Create a structured list for DataFrame
            data = []
            for label in all_labels:
                filename_count = prefix_counts.get(label, 0)  # Count from filenames
                prediction_count = prediction_counts_full.get(label, 0)  # Count from predictions
                
                # Only add row if at least one count is nonzero
                if filename_count > 0 or prediction_count > 0:
                    # Check if the prefix is in the label_mapping and use the full label
                    if label in label_mapping.values():
                        full_label = label
                    else:
                        full_label = label_mapping.get(int(label), label) if label.isdigit() else label
                    data.append({
                        "Label": full_label,
                        "Filename Count": filename_count,
                        "Prediction Count": prediction_count
                    })
            
            # Display DataFrame with cell label and frequency
            result = pd.DataFrame(data)
            st.write(result)
            
            # Diagnostic result header
            st.markdown("""
                        **Diagnostic result:**
                        """)
    
            # Check AML condition
            precursor_count = prediction_counts.get(1, 0) + prediction_counts.get(3, 0) + prediction_counts.get(6, 0) + prediction_counts.get(7, 0) + prediction_counts.get(9, 0) + prediction_counts.get(10, 0) + prediction_counts.get(13, 0) + prediction_counts.get(14, 0)  
            
            # Diagnostic statement printed on frontend
            if precursor_count > 20:
                st.write(f"**{precursor_count}% precursor cells found**: 🚨 patient suffers from AML 🚨")
            elif precursor_count > 0:
                st.write(f"**{precursor_count}% precursor cells found**: ⚠️ genetic testing for AML recommended ⚠️")
            else:
                st.write(f"**No precursor cells found**: ✅ no signs of hematologic malignancy ✅")

        else:
            # If there was an error, print the error message
            st.write(f"Error: {response.status_code} - {response.text}")
        
    st.markdown("""
    **Leukemia Risk Reference:**
    - **< 0% precursors:** No evidence of leukemia
    - **> 0% and < 20%:** Precursor cells detected, genetic tests for AML confirmation required
    - **> 20% precursors:** AML confirmed
    """)

st.markdown("---")

#####  SEND TO API BUTTON #####
st.write("Press button to send images to API")
if st.button("Send to API"):
    if uploaded_files:
        uploaded_images_urls = []  # Reset the list

        for uploaded_file in uploaded_files:
            img_bytes = uploaded_file.getvalue()
            files = {"file": (uploaded_file.name, img_bytes, "png")}

            response = requests.post("http://127.0.0.1:8000/uploadfile/", files=files)

            if response.status_code == 200:
                response_data = response.json()
            else:
                st.write("Error:", response.text)

        st.write("Images uploaded to API")
    else:
        st.write("No images uploaded")
        
st.markdown("---")

