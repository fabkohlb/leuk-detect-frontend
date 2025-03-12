import streamlit as st
import requests
from PIL import Image

##### HEADER #####
st.markdown("""# Blood cancer prediction model
    Using deep learning (CNN) to detect immature leukocytes
    
    This model is trained on 18,000 cells to discriminate 15 leukocyte subclasses.""")

##### SPLIT WEBSITE INTO 2 SIDES #####
cols = st.columns(2)

# Code for column 1
with cols[0]:
    st.markdown("### Artificial patient (100 cells)")
    
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
    st.markdown("""
    **Leukemia Risk Assessment:**
    - **< 0% precursors:** No evidence of leukemia
    - **> 0% and < 20%:** Precursor cells detected, genetic tests for AML confirmation required
    - **> 20% precursors:** AML confirmed
    """)

##### IMAGE SAVE FUNCTION #####
st.write("You can upload multiple images and save them to the server.")

if st.button("Save Images"):
    if uploaded_files:
        files = [("images", (image.name, image.getvalue())) for image in uploaded_files]
        response = requests.post("http://localhost:8000/save_images/", files=files)
        st.write(response.json())
    else:
        st.write("No images uploaded")
