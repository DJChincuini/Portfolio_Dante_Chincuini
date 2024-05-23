import streamlit as st 
import pandas as pd
import numpy as np
import plotly.express as px

# Configuro para que el layout sea "wide"
st.set_page_config(layout="wide")

# BODY ---------------------------------------------------------------------------------------------------------------
# Descripción

st.write(
    '''
    📌 Mi nombre es Dante. Soy un estudiante apasionado de programación y la estadística con un enfoque especial en el diseño, desarrollo e implementación de soluciones robustas por medio del Data Engineering 💻 así cómo también de la búsqueda de insights a través de los datos y del pensamiento analítico a la hora de la toma de decisiones 📊.
    
    
    '''
)

# TAIL ---------------------------------------------------------------------------------------------------------------

# Creo dos columnas
tail = st.columns(2)

with tail[0]:
    pass

with tail[1]:
    # Creo dos sub columnas
    sub = st.columns(4)
    
    with sub[0]:
        pass
    with sub[1]:
        pass
    with sub[2]:
        st.link_button("LinkedIn", "https://www.linkedin.com/in/dante-chincuini-2828b6281/")
    with sub[3]:
        st.link_button("GitHub", "https://github.com/DJChincuini")