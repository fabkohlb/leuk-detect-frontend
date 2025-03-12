import streamlit as st
import requests
from PIL import Image
import io

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

# Code for column 1
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
                    st.image(images[row][col], caption=f"Image {row * grid_size + col + 1}", use_container_width=True)
                else:
                    st.write("⬜")  # Placeholder for empty cells

# Code for column 2
with cols[1]:
    
    #####  PREDICTION BUTTON #####
    st.write("Prediction")
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
            prediction = response_data.get("prediction", "No prediction found")
            
            # Print the prediction result
            st.write(f"Prediction: {prediction}")
            
            ### DUMMY - NEEDS TO BE ADAPTED TO REAL RESULT ###
            if prediction > 8:
                st.write("Dummy result: AML confirmed - patient suffers from AML")
            elif prediction > 3:
                st.write("Dummy result: Precursor cells found - genetic testing for AML recommended")
            else:
                st.write("Dummy result: No precursor cells found - no signs of hematologic malignancy")

        else:
            # If there was an error, print the error message
            st.write(f"Error: {response.status_code} - {response.text}")
        
        print(type(prediction))
        print(prediction)
        
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
            files = {"file": (uploaded_file.name, img_bytes, "image/jpeg")}

            response = requests.post("http://127.0.0.1:8000/uploadfile/", files=files)

            if response.status_code == 200:
                response_data = response.json()
            else:
                st.write("Error:", response.text)

        st.write("Images uploaded to API")
    else:
        st.write("No images uploaded")
        
st.markdown("---")

