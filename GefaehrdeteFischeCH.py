from doctest import REPORT_CDIFF
import json
import time
import streamlit as st
import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow import keras

with open('index_to_class_label.json', 'r') as f:
    index_to_class_label_dict = json.load(f)
index_to_class_label_dict = {int(k): v for k, v in index_to_class_label_dict.items()}

with open('index_to_danger_state.json', 'r') as d:
    index_to_danger_state_dict = json.load(d)
index_to_danger_state_dict = {int(k): v for k, v in index_to_danger_state_dict.items()}

fish_family = pd.read_excel(r'fish_family.xlsx')
fish_detail = pd.read_excel(r'database_detail.xlsx')

myDict = {"fish_name_science": [], "fish_name_ge": [], "fish_danger_state": [], "fish_habitat": []}

def get_danger_status(status_idx):
    status_name = index_to_danger_state_dict[status_idx]
    status_name = status_name.replace("ae", "ä" ).replace("oe", "ö" ).replace("ue", "ü" )
    return status_name

#configures the default settings of the page
st.set_page_config(
    page_title="Gefährdete Fische CH",
    page_icon=":fish:",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None,
    }
)

st.title("Gefährdete Fische CH :fish: ")
st.write("Fisch gefangen und du weisst nicht, ob es sich um eine gefährdete Fischart handelt?")
st.write("Diese Fischerkennungs-App bestimmt für dich die in der Schweiz vorkommenden Fische und warnt dich vor gefährdeten Fischarten.")
st.write("Foto aufnehmen oder hochladen und den gefangenen Fisch schnell und praktisch bestimmen.")

tab1, tab2 = st.tabs(["Foto hochladen", "Foto aufnehmen"])

with tab1:
     file = st.file_uploader("", label_visibility="collapsed")

with tab2:
      picture = st.camera_input("")

st.write("")

if file is not None or picture is not None:
    img = file or picture
    show = st.checkbox('Ausgewählter Fisch anzeigen')
    if show:
        st.image(img)
    
    st.write("")
    btn = st.button('Fischerkennung starten')
    st.write("")

    if btn:
        with st.spinner('Fisch wird erkannt...'):
            time.sleep(5)
            #neues Model noch einsetzen!!
            model = tf.keras.models.load_model('trained_model_1.h5')

            img = tf.keras.utils.load_img(
                img, target_size=(224, 224)
            )
            img_array = tf.keras.utils.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)
     
            predictions = model.predict(img_array)
            score = tf.nn.softmax(predictions[0])
            result = index_to_class_label_dict[np.argmax(score)]
            for i in range(len(fish_family.index)):
                if fish_family['fam_name'][i].lower() == result:
                    result_name = fish_family['name_ge'][i]

        if np.max(score) < 0.7:
            st.error("Leider konnte der Fisch nicht erkannt werden.")
            st.error("Fisch bitte zurück in das Wasser werfen oder beim regionalen Fischereiverband nachfragen.")
        else:
            lst_name_science = []
            lst_name_ge = []
            lst_danger_state = []
            lst_fish_habitat = []

            for i in range(len(fish_detail.index)):
                if fish_detail['grp'][i] == result:
                   lst_name_science.append(fish_detail['name_science'][i])
                   lst_name_ge.append(fish_detail['name_ge'][i])
                   lst_danger_state.append(fish_detail['danger_state_ch'][i])
                   lst_fish_habitat.append(fish_detail['habitat'][i])
        
            myDict["fish_name_science"] = lst_name_science
            myDict["fish_name_ge"] = lst_name_ge
            myDict["fish_danger_state"] = lst_danger_state
            myDict["fish_habitat"] = lst_fish_habitat

            if len(list(myDict["fish_name_science"])) == 1:
                st.success("Mit einer Wahrscheinlichkeit von **{:.2f}%** handelt es sich hier um einen **{}** (_{}_)." .format(100 * np.max(score), list(myDict["fish_name_ge"])[0], list(myDict["fish_name_science"])[0]))

                col1, col2 = st.columns(2)

                with col1:
                    status = get_danger_status(list(myDict["fish_danger_state"])[0])
                    habitat = list(myDict["fish_habitat"])[0]
                    link = "https://wikipedia.org/wiki/" + list(myDict["fish_name_science"])[0].replace(" ", "_" )

                    st.caption("Gefährdungsstatus")
                    if status == "Nicht gefährdet":
                        st.success(status)
                    elif status == "Potenziell gefährdet":
                        st.warning(status)
                    else:
                        st.error(status)
                    st.caption("Einzugsgebiet")
                    st.info(habitat)
                    st.caption(f"Weitere Information: [Link]({link})")

                with col2:
                    st.image('./Images/' + list(myDict["fish_name_science"])[0].replace(" ", "_" ) + '.jpg')
            
            else:
                st.success("Mit einer Wahrscheinlichkeit von **{:.2f}%** handelt es sich hier um einen der folgenden Fische der Familie **{}**." .format(100 * np.max(score), result_name))

                for i in range(len(list(myDict["fish_name_science"]))):

                    with st.expander(list(myDict["fish_name_ge"])[i] + " (" + list(myDict["fish_name_science"])[i] + ")"):

                        col1, col2 = st.columns(2)

                        with col1:
                            status = get_danger_status(list(myDict["fish_danger_state"])[i])
                            habitat = list(myDict["fish_habitat"])[i]
                            link = "https://wikipedia.org/wiki/" + list(myDict["fish_name_science"])[i].replace(" ", "_" )

                            st.caption("Gefährdungsstatus")
                            if status == "Nicht gefährdet":
                                st.success(status)
                            elif status == "Potenziell gefährdet":
                                st.warning(status)
                            else:
                                st.error(status)
                            st.caption("Einzugsgebiet")
                            st.info(habitat)
                            st.caption(f"Weitere Information: [Link]({link})")

                        with col2:
                            st.image('./Images/' + list(myDict["fish_name_science"])[i].replace(" ", "_" ) + '.jpg')