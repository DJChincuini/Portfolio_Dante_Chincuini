import streamlit as st 
import pandas as pd
import numpy as np
import plotly.express as px

# Configuro para que el layout sea "wide"
st.set_page_config(layout="wide")

#---------------------------------------------------------------------------------------------------------------------
# Cargo los Datasets
hechos = pd.read_csv('./Datasets/Hechos.csv')
victimas = pd.read_csv('./Datasets/Victimas.csv')

# Mini ETL
# Reemplazo valores SD (Sin Dato) por valores None
victimas = victimas.replace("SD",np.nan)
hechos = hechos.replace("SD",np.nan)

# Creo listas con las columnas que necesito
hechos_reducido = hechos[['ID', 'COMUNA', 'TIPO_DE_CALLE', 'AAAA', 'VICTIMA', 'ACUSADO', 'pos x', 'pos y']]
victimas_reducido = victimas[['ID_hecho', 'SEXO', 'EDAD']]

# Renombro 'ID_hecho'
victimas_reducido = victimas_reducido.rename(columns={'ID_hecho': 'ID'})

# Merge para crear el dataset final
df_final = pd.merge(hechos_reducido, victimas_reducido, on='ID', how='inner')

# Transformo la columna 'EDAD' a numérico
df_final['EDAD'] = pd.to_numeric(df_final['EDAD'], errors='coerce')

# Creo una columna con el grupo etario en base a 'EDAD'
bins = [0, 12, 18, 35, 50, 65, 100]  # Definir los rangos de edad
labels = ['Niño', 'Adolescente', 'Joven Adulto', 'Adulto', 'Adulto Maduro', 'Adulto Mayor']  # Definir los nombres de los grupos etarios
df_final['GRUPO ETARIO'] = pd.cut(df_final['EDAD'], bins=bins, labels=labels, right=False)

# Elimino la columna EDAD
df_final = df_final.drop(columns=['EDAD'])

# Ordeno la columna 'COMUNA'
df_final.sort_values(by='COMUNA', inplace=True)

# Le agrego la palabra 'COMUNA' a cada palabra de la columna comuna.
df_final['COMUNA'] = df_final['COMUNA'].apply(lambda x: f'COMUNA {str(x)}')

 # Reemplazo la 'COMUNA 0' por Desconocido.
df_final['COMUNA']  = df_final['COMUNA'].apply(lambda x: 'DESCONOCIDO' if x == 'COMUNA 0' else x)


#---------------------------------------------------------------------------------------------------------------------
### TÍTULO
st.write("### Informe sobre siniestros viales en la ciudad de Buenos Aires") 
st.write("*Creado por Dante Chincuini* \n####")


#---------------------------------------------------------------------------------------------------------------------
### INTRODUCCIÓN
st.write("#### **Introducción**")

st.write(
    f'''
    En este proyecto abordaré realicé un análisis sobre los siniestros viales en la ciudad autónoma de Buenos Aires. 
Primeramente, realicé un informe EDA para ver las relaciones de los datos, los nulos que contiene y buscar outliers que pueden condicionar al posterior análisis. Todo este proceso lo pueden encontrar en mi repositorio de github en el siguiente link: https://github.com/DJChincuini/Data_Analysis-Chincuini/blob/main/EDA.ipynb.
\n ###''')


#---------------------------------------------------------------------------------------------------------------------
### KPIs
st.write("#### **KPIs**")

kpi1,kpi2 = st.columns(2) # Creo dos columnas para presentar los KPI

# Primera Columna
with kpi1:
    st.write(f"*Reducir en un 10% la tasa de homicidios en siniestros viales de los últimos seis meses.*")    
    # Fórmula del primer KPI    
    st.latex(
        r'''
        KPI = \frac{\left(\frac{H actual}{S actual}\right)}{\left(\frac{H anterior}{S anterior}\right) * 0.9}
        '''
    )
    
    # Descipción de la fórmula
    st.write(f'''
    Dónde:\n
    + *H actual* es la cantidad de homicidios en siniestros en el último semestre\n
    + *S actual* es la cantidad total de siniestros en el último semestre\n
    + *H anterior* es la cantidad de homicidios en siniestros en el semestre anterior\n
    + *S anterior* es la cantidad total de siniestros en el semestre anterior
    ''')

# Segunda Columna
with kpi2:
    st.write(f"*Reducir en un 7% la cantidad de accidentes mortales de motociclistas en el último año*")
    st.latex(
        r'''
        KPI = \frac{SM actual}{SM anterior * 0.7}
        '''
    )

    # Descripción de la fórmula
    st.write(f'''
    Dónde:\n
    + *SM actual* es la cantidad de siniestros dónde estén implicadas motocicletas en el último año\n
    + *SM anterior* es la cantidad de siniestros dónde estén implicadas motocicletas en el año anterior         
    ''')
st.write("##")


#---------------------------------------------------------------------------------------------------------------------
### DATASETS
st.write('#### **Datasets**')

st.write(
    '''
    Para poder llevar a cabo esta investigación, utilicé los datos pertenecientes del datasets de homicidios.xlsx provisto por el Observatorio de Movilidad y Seguridad Vial de la ciudad autónoma de Buenos Aires.
    '''
)

# Datasets Hechos
with st.expander("Hechos"):
    st.write("En este Dataset se registran los datos sobre el lugar geográfico y la hora de cada siniestro")
    st.dataframe(hechos,column_config={
        "AAAA": st.column_config.NumberColumn("AÑO",format="%d"),
        "MM": st.column_config.NumberColumn("MES"),
        "DD": st.column_config.NumberColumn("DIA"),
        "FECHA":st.column_config.DateColumn(format="DD.MM.YYYY")
    })
    
# Datasets Victimas
with st.expander("Victimas"):
    st.write("En este Dataset se registran los datos centrados en los participantes de los siniestros, el estado de las victimas y los vehículos implicados")
    st.dataframe(victimas, column_config={
        "FECHA":st.column_config.DateColumn(format="DD.MM.YYYY"),
        "FECHA_FALLECIMIENTO":st.column_config.DatetimeColumn(format="DD.MM.YYYY h:mm a")
    })
st.write("##")


#---------------------------------------------------------------------------------------------------------------------
### DASHBOARD
st.write("#### Dashboard")

# Filtración por COMUNAS -----------------------------------------------------------------------
comunas = []
for i in df_final['COMUNA']:
    if i not in comunas:
        comunas.append(i)
        
## FILTROS

# Columnas para los filtros.
col1, col2 = st.columns(2)

st.write('***Niño:*** Hasta 12 años // ***Adolescente:*** De 13 a 18 años // ***Joven Adulto:*** De 19 a 35 años // ***Adulto:*** De 36 a 50 años // ***Adulto Maduro:*** De 51 a 65 años // ***Adulto Mayor:*** Mayor de 65 años')
    
# Filtro por GRUPO ETARIO
edades_filtradas = st.multiselect(
    "FILTRAR POR GRUPO ETARIO",
    ['Niño', 'Adolescente', 'Joven Adulto', 'Adulto', 'Adulto Maduro', 'Adulto Mayor'],
    ['Niño', 'Adolescente', 'Joven Adulto', 'Adulto', 'Adulto Maduro', 'Adulto Mayor']
    )

# Filtro por COMUNAS
comuna_filtradas = st.multiselect(
    "FILTRAR POR COMUNA",
    comunas,
    ['COMUNA 1', 'COMUNA 2'],
    help='Selecciona una opción'
    )

df_filtrado = df_final[(df_final['COMUNA'].isin(comuna_filtradas)) & (df_final['GRUPO ETARIO'].isin(edades_filtradas))]

# Filtro por grupo Etario
# ----------------------------------------------------------------------------------------------

# Creo dos columnas
superior = st.columns(2) 

with superior[0]: # Columna con el pie chart
    
    
    if df_filtrado is None or len(df_filtrado) == 0:
        # Creao un gráfico vacío
        fig = px.pie(title="Siniestros por comuna")
        st.plotly_chart(fig)
        
    else:   
        conteo_sexo = df_filtrado['SEXO'].value_counts()
        fig = px.pie(values=conteo_sexo.values, names=conteo_sexo.index, hole=.3, title="Sexo de las víctimas")
        fig.update_layout(width=600, height=400)
        st.plotly_chart(fig)


with superior[1]:  # Columna del bar chart
    if df_filtrado is None or len(df_filtrado) == 0:
        # Creao un gráfico vacío
        fig = px.bar(title="Siniestros por comuna")
        fig.update_layout(yaxis_title='CONTEO', xaxis_title='COMUNA', width=600)
        st.plotly_chart(fig) 
        
    else:
        conteo_comunas = df_filtrado['COMUNA'].value_counts().sort_index()
        fig = px.bar(y=conteo_comunas.values, x=conteo_comunas.index, title="Siniestros por comuna")
        fig.update_layout(yaxis_title='CONTEO', xaxis_title='COMUNA', width=600)
        st.plotly_chart(fig)


#---------------------------------------------------------------------------------------------------------------------
### ABOUT ME
st.write("#### Sobre el autor")
st.write(
    '''
    👋 Hola, me llamo Dante.
    
    📌 Soy un estudiante apasionado de programación y la estadística con un enfoque especial en el diseño, desarrollo e implementación de soluciones robustas por medio del Data Engineering 💻 así cómo también de la búsqueda de insights a través de los datos y del pensamiento analítico a la hora de la toma de decisiones 📊.

    📈 Me considero experto en la creación de arquitecturas escalables para procesamiento gracias a mí conocimientos de GCP y Python, cómo también del análisis de datos y el diseño de estrategias ayudándome con mi conocimiento de SQL y PowerBI. También poseo conocimientos en estadística y marketing gracias a mí tecnicatura en Diseño y Comunicación Multimedial.

    💪 Siempre en busca de desafíos que impulsen la innovación y la eficiencia en el mundo de la tecnología, mí objetivo es poder colaborar con profesionales tan apasionados cómo yo en pos de impulsar la toma de decisiones empresariales basándonos en lo que los datos pueden proveernos.
    ''')