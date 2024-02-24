import streamlit as st
import requests
import time
import streamlit_authenticator as stauth
from streamlit_authenticator import Authenticate
import yaml
from yaml.loader import SafeLoader


st.set_page_config(layout="wide")
token = "cTAD1TIT7wYa6yK5KlayxLvv0WqIiHiRFEPZjPFdeVXSRqELeTt6iTUI5lC2AakW"

def get_draft(payload: dict):

    endpoint = f"http://localhost:8080/generate_draft?token={token}"

    headers = {"accept": "application/json", "Content-Type": "application/json"}

    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def main():
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    name, authentication_status, username = authenticator.login("Login", "main")
    if authentication_status:
        authenticator.logout("Logout", "main")

        st.title("Content Generation Assistant")
        st.markdown(
            "This is a Content Generation Assistant that generates a draft for a given title/seed sentence/keywords and other parameters."
        )
        title = st.text_input(
            "Initial text/seed sentence/keywords", "Clean energy is a Danish passion"
        )

        c1, c2, c3 = st.columns(3, gap="large")

        tone = c1.radio(
            "Tone", ("Formal", "Creative", "Playful/Quirky", "Technical"), index=1
        )
        content_format = c2.radio(
            "Content Format",
            ("Blogpost", "Research Article", "Social Media", "Product documentation"),
            index=0,
        )
        vertical = c3.radio(
            "Vertical", ("Banking", "Healthcare", "Legal", "Energy"), index=3
        )
        min_length = c1.slider("Min Length", 10, 1000, 400)
        max_length = c2.slider("Max Length", 100, 5000, 1000)
        top_k = 50
        top_p = 0.95

        if max_length < min_length:
            st.error("Max Length should be greater than Min Length")
            return

        payload = {
            "title": title,
            "tone": tone,
            "content_format": content_format,
            "max_length": max_length,
            "min_length": min_length,
            "top_k": top_k,
            "top_p": top_p,
            "do_sample": True,
            "vertical": vertical,
        }

        res_ = st.button("Generate Draft")
        if res_:
            with st.spinner("Generating Draft..."):
                start = time.time()
                response = get_draft(payload=payload)
                if response["draft"] == "":
                    st.error("Error generating draft")
                else:
                    st.success("Draft Generated Successfully")
                end = time.time()
                time_taken = end - start

            st.markdown("## Generated Draft")
            st.markdown(response["draft"])
            st.markdown(
                "#### Hostname\n This indicates the load balancing of the deployed App. Three replicas of the containerized API are running on GKE."
            )
            st.text(response["hostname"])
            st.markdown("#### Time Taken")
            st.text(f"{time_taken:.2f} seconds")

        st.markdown(
            """
                    ### Details of implementation.

                    #### 1. API Development & Deployment:
                    - **Framework**:  The API is developed using the `FastAPI` framework.
                    - **Containerization**: The API is containerized using Docker and the image is stored in the Docker Hub registry.
                    - **Deployment**: Deployed on a Google Kubernetes Engine (GKE) cluster with CPU-based machines.
                    - **Replication**: Three replicas of the API running on the GKE cluster for high availability.
                    - **Region**: The API is deployed in the `eu-west` region in compliance with GDPR regulations.
                    - **Access & Authentication**: The public endpoint is exposed via Ingress with a fixed token authentication mechanism.

                    #### 2. Front-end Deployment:
                    - **Framework**: I am utilizing `Streamlit` for the front-end UI.
                    - **Containerization**: The Streamlit front-end is also containerized.
                    - **Deployment**: Like the API, it's deployed on the GKE cluster.
                    - **Interaction**: This UI interacts with our backend API to fetch and display results.

                    #### 3. Model Details:
                    - **Model Used**: I have used the `flan-T5 base` model with 250M parameters.
                    - **Fine-Tuning**: There's no fine-tuning done on the model.
                    - **Performance**: On CPU, the model's response time varies between 20-30 seconds based on the word count.

                    #### 4. Current Limitations:
                    - **Vector DB Approach**: I am yet to implement the vector DB approach for prompt enrichment. Potential implementations could used managed services, Milvus, or the faiss index.
                    """
        )
    elif authentication_status == False:
        st.error("Username/password is incorrect")
    elif authentication_status == None:
        st.warning("Please enter your username and password")


if __name__ == "__main__":
    main()
