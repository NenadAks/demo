import os
from mistralai import Mistral
import tempfile
from dotenv import load_dotenv
import streamlit as st

st.set_page_config(page_title = "Sonepar Demo")

load_dotenv()

api_key = st.secrets["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

st.title("Analyse et Comparaison des Documents")

# Create two columns for file uploaders
col1, col2 = st.columns(2)

with col1:
    st.subheader("Document 1")
    uploaded_file1 = st.file_uploader("Téléchargez le premier fichier PDF", type="pdf", key="file1")

with col2:
    st.subheader("Document 2")
    uploaded_file2 = st.file_uploader("Téléchargez le deuxième fichier PDF", type="pdf", key="file2")

if (st.button("Analyser et Comparer")):
    if uploaded_file1 is None or uploaded_file2 is None:
        st.error("Veuillez télécharger les deux documents")
    else:
        model = "mistral-large-latest"
        
        # Process both files
        def process_file(uploaded_file):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            uploaded_pdf = client.files.upload(
                file={
                    "file_name": uploaded_file.name,
                    "content": open(tmp_file_path, "rb")
                },
                purpose="ocr"
            )
            os.unlink(tmp_file_path)
            return client.files.get_signed_url(file_id=uploaded_pdf.id)

        # Get signed URLs for both files
        signed_url1 = process_file(uploaded_file1)
        signed_url2 = process_file(uploaded_file2)

        # Define messages for comparison
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyse et compare les deux documents suivants. Pour chaque document, extrait:
                                1. Type d'emballage
                                2. Numéro DET
                                3. Prix
                                
                                Pour le premier doc, je vais juste avoir besion de 4 premières articles.
                                Le prix pour les deux documents est calculée en millième (si c'est 1128, le prix est 1.128)
                                Présente les résultats sous forme de tableau comparatif et indique les différences significatives entre les deux documents. 
                                Je veux avoir le comparaison des diffèrence de prix par article dépendant de la taille (en %) dans le même tableau ((doc1-doc2)/doc2). (171346A1 et 171346C correspond au MEDIUM du doc 2 et 171347A1 et 171347C au LARGE du doc 2)"""
                    },
                    {
                        "type": "document_url",
                        "document_url": signed_url1.url
                    },
                    {
                        "type": "document_url",
                        "document_url": signed_url2.url
                    }
                ]
            }
        ]

        with st.spinner('Analyse en cours...'):
            # Get the chat response
            chat_response = client.chat.complete(
                model=model,
                messages=messages
            )

            # Display results
            st.subheader("Résultats de la comparaison")
            st.write(chat_response.choices[0].message.content)