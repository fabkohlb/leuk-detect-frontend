import streamlit as st
import requests
from PIL import Image
import pandas as pd
from collections import Counter

# base URL
base_url = "https://leukdetectdockerimage-520133089750.europe-west10.run.app"

# Make use of whole screen
st.set_page_config(layout="wide")

# Code to set background of box of diagnostic result white (st.error); CSS code done by Laia
CSS = """
.st-cx{
    background-color: white;
    color: black
    }
"""
st.write(f'<style>{CSS}</style>', unsafe_allow_html=True)
predicted = False

# Create tabs on website
tab1, tab2, tab3 = st.tabs(["Introduction", "Prediction", "Contributors"])

# #Tab 1
with tab1:
    st.markdown("""# Blood cancer prediction model
    Acute Myeloid Leukemia (AML)
    """)

    with st.expander("**Introdcution**"):
        cols = st.columns(2)
        with cols[0]:
            st.image("https://www.shutterstock.com/image-vector/comparison-between-normal-blood-leukemia-260nw-2582344449.jpg")
        with cols[1]:
            st.write('''
                     **Etiology**
                     - Cytogenetic alterations, environmental factors (e.g. pesticides)
                     - Other risk factors, e.g. smoking
                     
                     **Clinic**
                     - AML is an acute disease
                     - General symptoms (weakness, fever, night sweats) typically appear with a short medical history
                     - Leukemic cells spread to blood
                     - Susceptibility to infection due to lack of mature and functional leukocytes 
            ''')
       
    with st.expander("**Routine Analysis**"):
        cols = st.columns(2)
        with cols[0]:
            st.image("https://www.mindray.com/content/xpace/en/products/laboratory-diagnostics/hematology/5-part-differential-analyzers/bc-6000.thumb.319.319.png.thumb.png")
        with cols[1]:
            st.write('''
                     **Steps in a Routine Blood Count Analysis**
                    - Blood is loaded into an automated hematology analyzer
                    - Analyzer counts and differentiates blood cells
                    - If abnormal results are detected, a blood smear is prepared       
            ''')
    
    with st.expander("**Abnormal results**"):
        cols = st.columns(2)
        with cols[0]:
            st.image("https://www.berufsberatung.ch/web_file/getbb?id=7591&mime=image/jpeg&original_name=Tech_analyse_bio_08_MG.jpg")
        with cols[1]:
            st.write('''
                     **Verification of abnormal results**
                    - A specialist examines the smear under a microscope to check for irregularities in cell shape, size, or presence of abnormal cells
                    - 100 cells must be counted
                    - Results depend on experience of examiner
                    - Very time consuming
            ''')
            
    
## Tab 2
with tab2:
    ##### HEADER #####
    st.markdown("""# LEUK-DETECT

    Using deep learning (Transformer) to detect immature leukocytes to identify patients suffering from Acute Myeloid Leukemia (AML).

    This model is trained on >18,000 cells to discriminate 15 leukocyte subclasses provided by Munic University Hospital (MUH).

    Workflow:
    1) Upload single cell images (400x400) to streamlit
    2) Upload images to API
    3) Perform prediction""")

    ##### SPLIT WEBSITE INTO 2 SIDES #####
    cols = st.columns(2)

    # Code for column 1 (left side)
    with cols[0]:
        st.markdown("### Patient cells")

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
        
        inner_cols = st.columns(2)
        
        with inner_cols[0]:

            #####  SEND TO API BUTTON #####
            st.write("**Press button to upload images:**")
            if st.button("Upload"):
                if uploaded_files:
                    uploaded_images_urls = []  # Reset the list
                    progress_bar = st.progress(0)  # Initialize progress bar
                    total_files = len(uploaded_files)  # Total files to be uploaded

                    for index, uploaded_file in enumerate(uploaded_files):
                        img_bytes = uploaded_file.getvalue()
                        files = {"file": (uploaded_file.name, img_bytes, "image/png")}

                        response = requests.post(f"{base_url}/uploadfile/", files=files)

                        if response.status_code == 200:
                            response_data = response.json()
                        else:
                            st.write(f"Error uploading {uploaded_file.name}: {response.text}")

                        # Update progress bar
                        progress = (index + 1) / total_files
                        progress_bar.progress(progress)

                        # Optional: Simulate delay (useful for debugging)
                        #time.sleep(0.2)

                    st.write("Images uploaded to API")
                    progress_bar.empty()  # Remove the progress bar when done
                else:
                    st.write("No images uploaded")

        with inner_cols[1]:
        
            #####  PREDICTION BUTTON #####
            st.write("**Press button to run prediction:**")
            # Create a button that triggers the prediction when clicked
            if st.button("Predict", disabled=not uploaded_files):
                # Define the URL of the prediction endpoint
                url = f"{base_url}/predict"

                # Send a POST request to the API
                response = requests.get(url)

                # Check if the response was successful
                if response.status_code == 200:
                    # Parse the JSON response and extract the prediction value
                    response_data = response.json()
                    print(f"Response data: {response_data}")
                    if response_data.get("predictions") is None:
                        st.write("No files uploaded. Please click Upload button.")
                    else:
                        predicted = True
                        predictions = response_data.get("predictions", "No prediction found")
                        #print(type(predictions))
                        #print(predictions)

                        # Mapping of numbers to labels of celltypes
                        # 15 classes
                        label_mapping = {
                            0: 'BAS',
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
                        
                        # 13 classes (no LYA, no KSC)
                        # label_mapping = {
                        #     0: 'BAS',
                        #     1: 'EBO',
                        #     2: 'EOS',
                        #     3: 'LYT',
                        #     4: 'MMZ',
                        #     5: 'MOB',
                        #     6: 'MON',
                        #     7: 'MYB',
                        #     8: 'MYO',
                        #     9: 'NGB',
                        #     10: 'NGS',
                        #     11: 'PMB',
                        #     12: 'PMO'
                        # }

                        # 15 classes
                        full_name_mapping = {
                            'BAS': 'Basophil',
                            'EBO': 'Erythroblast',
                            'EOS': 'Eosinophil',
                            'KSC': 'Smudge cell',
                            'LYA': 'Lymphocyte (atypical)',
                            'LYT': 'Lymphocyte (typical)',
                            'MMZ': 'Metamyelocyte',
                            'MOB': 'Monoblast',
                            'MON': 'Monocyte',
                            'MYB': 'Myelocyte',
                            'MYO': 'Myeloblast',
                            'NGB': 'Neutrophil (band)',
                            'NGS': 'Neutrophil (segmented)',
                            'PMB': 'Promyelocyte (bilobed)',
                            'PMO': 'Promyelocyte',
                        }

                else:
                    # If there was an error, print the error message
                    st.write(f"Error: {response.status_code} - {response.text}")
            
        if predicted:    
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
                        "Celltype": full_name_mapping[full_label],
                        "Expected": filename_count,
                        "Predicted": prediction_count
                    })

            # Display DataFrame with cell label and frequency
            result = pd.DataFrame(data)
            st.write(result)
            
            container = st.container()
        
            with container:
                # Diagnostic result header
                # st.markdown("""
                st.markdown("""
                            **Diagnostic result:**
                            """)

                # Check AML condition with 15 classes
                precursor_count = prediction_counts.get(1, 0) + prediction_counts.get(6, 0) + prediction_counts.get(7, 0) + prediction_counts.get(9, 0) + prediction_counts.get(10, 0) + prediction_counts.get(13, 0) + prediction_counts.get(14, 0)
                # Check AML condition with 13 classes
                # precursor_count = prediction_counts.get(1, 0) + prediction_counts.get(4, 0) + prediction_counts.get(5, 0) + prediction_counts.get(7, 0) + prediction_counts.get(8, 0) + prediction_counts.get(11, 0) + prediction_counts.get(12, 0)

                # Diagnostic statement printed on frontend
                if precursor_count > 19:
                    st.error(f"**{precursor_count}% precursor cells found**: 🚨 patient suffers from AML 🚨")
                elif precursor_count > 0:
                    st.error(f"**{precursor_count}% precursor cells found**: ⚠️ genetic testing for AML recommended ⚠️")
                else:
                    st.error(f"**No precursor cells found**: ✅ no signs of hematologic malignancy ✅")

            
        
            st.markdown("""
            **Leukemia Risk Reference:**
            - **< 0% precursors:** No evidence of leukemia
            - **> 0% and < 20%:** Precursor cells detected, genetic tests for AML confirmation required
            - **> 20% precursors:** AML confirmed
            """)

    st.markdown("---")

# CONTRIBUTORS
with tab3:
    # Define image URLs and corresponding names
    
    img_fabian = "https://media.licdn.com/dms/image/v2/C5603AQGyQVeqi9rrJQ/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1612894128703?e=1747872000&v=beta&t=dbq7phLz7a-qOu2cgV78f7qYHWHf8XOEzTG-sXxu0FY"
    img_oskar = "https://media.licdn.com/dms/image/v2/D4D03AQGjLmAa0JoJcA/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1724488199292?e=1747872000&v=beta&t=MfqfbXpExhJ_JAbgnV51zou5Pe_7__9YxUpv6ZbYMCw"
    img_frederik = "https://media.licdn.com/dms/image/v2/D4E35AQF8FF0bl8RxuQ/profile-framedphoto-shrink_400_400/profile-framedphoto-shrink_400_400/0/1729088154728?e=1743084000&v=beta&t=kSM_w5OWFWe-HitIZwaDU0HdKal5o7BvgvIHwvUl1ww"
    img_anton = "https://media.licdn.com/dms/image/v2/C4D03AQHFsthN695zcA/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1596574176654?e=1747872000&v=beta&t=Y9CU9so15_lCyk7hpMGKRY01_BWIAkikzIk0WgBdFIA"
    
    people = [
        (img_fabian, "Fabian"),
        (img_oskar, "Oskar"),
        (img_frederik, "Frederik"),
        (img_anton, "Anton")
    ]

    st.title("Leuk-Detect Team")

    # Create columns
    cols = st.columns(len(people))

    # Loop through people and display images with names
    for col, (image, name) in zip(cols, people):
        with col:
            st.image(image, caption=name, use_container_width=True)
            st.markdown(
                f"""
                <style>
                    img {{
                        border-radius: 50%;
                    }}
                </style>
                """,
                unsafe_allow_html=True
            )