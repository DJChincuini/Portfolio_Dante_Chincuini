import streamlit as st 
import pandas as pd
import numpy as np
import plotly.express as px

# Configuro para que el layout sea "wide"
st.set_page_config(layout="wide")

# BODY ---------------------------------------------------------------------------------------------------------------
# Descripción

st.write("## Sobre Mí")


st.write(
        '''
        📌 Me llamo Dante. Soy un estudiante apasionado de programación y la estadística con un enfoque especial en el diseño, desarrollo e implementación de soluciones robustas por medio del Data Engineering 💻 así cómo también de la búsqueda de insights a través de los datos y del pensamiento analítico a la hora de la toma de decisiones 📊.
        
        📈 Me considero experto en la creación de arquitecturas escalables para procesamiento gracias a mí conocimientos de GCP y Python, cómo también del análisis de datos y el diseño de estrategias ayudándome con mi conocimiento de SQL y PowerBI. También poseo conocimientos en estadística y marketing gracias a mí tecnicatura en Diseño y Comunicación Multimedial.
        
        💪 Siempre en busca de desafíos que impulsen la innovación y la eficiencia en el mundo de la tecnología, mí objetivo es poder colaborar con profesionales tan apasionados cómo yo en pos de impulsar la toma de decisiones empresariales basándonos en lo que los datos pueden proveernos.
        ''')

st.write('#')

# PROYECTOS -----------------------------------------------------------------------------------------------------------

st.write("## Proyectos")

proyectos = st.columns(2)

with proyectos[0]:
    
    # Proyecto de Siniestros Viales
    with st.container(height=200):
        st.write('##### Siniestros Viales')
        st.write('Análisis sobre los siniestros viales en la ciudad de Buenos Aires con dos datasets del Observatorio Vial de la Ciudad. \n#####')
        
        boton = st.columns(5)
        with boton[4]:
            st.page_link("./pages/2_ Siniestros Viales.py", label='VER')
    
st.write('#')


# TAIL ---------------------------------------------------------------------------------------------------------------

# Creo dos columnas
tail = st.columns(2)

with tail[0]:
    # Creo dos sub columnas
    sub = st.columns(5)

    with sub[0]:
        st.link_button("LinkedIn", "https://www.linkedin.com/in/dante-chincuini-2828b6281/", use_container_width=True)
    with sub[1]:
        st.link_button("GitHub", "https://github.com/DJChincuini", use_container_width=True)
        
with tail[1]:
    pass
