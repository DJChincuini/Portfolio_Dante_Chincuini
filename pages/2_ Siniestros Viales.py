import streamlit as st 
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
hechos_reducido = hechos[['ID', 'COMUNA', 'TIPO_DE_CALLE', 'AAAA','MM','HH', 'VICTIMA', 'ACUSADO', 'pos x', 'pos y']]
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

# Creo una función para limpiar las columnas 'pos x' y 'pos y'
def limpiar_y_convertir(columna):
    # Eliminar espacios y valores no numéricos que consisten solo en '.'
    columna = columna.str.strip().replace('.', '')
    # Reemplazar valores vacíos o no válidos con NaN
    columna = pd.to_numeric(columna, errors='coerce')
    return columna

# Aplico la función a las columnas
df_final['pos y'] = limpiar_y_convertir(df_final['pos y'])
df_final['pos x'] = limpiar_y_convertir(df_final['pos x'])

# Cambio los valores nulos a 0
df_final['HH'] = df_final['HH'].fillna(0)
# Transformo los valores a flotantes
df_final['HH'] = df_final['HH'].astype(int)

# Creo dos columnas para los semestres
df_final['SEM_1'] = df_final['MM'].apply(lambda x: 1 if x <= 6 else 0)
df_final['SEM_2'] = df_final['MM'].apply(lambda x: 0 if x <= 6 else 1)

# Cambio los valores nulos por 'SIN DATO'
df_final['VICTIMA'] = df_final['VICTIMA'].fillna('DESCONOCIDO')
#---------------------------------------------------------------------------------------------------------------------
### TÍTULO
st.write("### Informe sobre siniestros viales en la ciudad de Buenos Aires") 
st.write("*Creado por Dante Chincuini* \n####")


#---------------------------------------------------------------------------------------------------------------------
### INTRODUCCIÓN
st.write("#### **Introducción** \n *¿Qué tan peligroso es viajar en Argentina?*")

st.write(
    f'''
    \n ###
Los siniestros viales es la 4ta causa de muerte más grande en toda Argentina, y la primera en dónde no hay problemas con alguna enfermedad. Viendo estos datos, me dispuse a indagar sobre cuales son los principales factores para que esto suceda, quienes están en mayor peligro y qué podemos hacer para bajar estos números. Al final de esta página podras encontrar una recreación del dashboard que llevé a cabo en Power Bi para este proyecto. Si quieres ver el dashboard original, lo podrás encontrar en: https://github.com/DJChincuini/Data_Analysis-Chincuini/tree/main.

Para este estudio, segmenté la información y me dediqué a estudiar sólo los datos provenientes de la ciudad de Buenos Aires, una de las ciudades con mayor cantidad de muertes en siniestros viales, utilizando dos datasets provistos por el Observatorio Vial de esta ciudad.

\n ###''')


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



### DESARROLLO
st.write("#### **Desarrollo del análisis** \n *Motos, Avenidas y Outliers*")

st.write(
    f'''
    \n ###
Primeramente, realicé un informe EDA (Exploratory Data Analysis), si quieres verlo lo puedes encontrar [aquí](https://github.com/DJChincuini/Data_Analysis-Chincuini/blob/main/EDA.ipynb). De este informe pude ver que las victimas más recurrentes de estos homicidios son los motociclistas y peatones. Los segundos, son más propensos en morir contra un transporte de pasajeros o un auto; si los comparamos con los números de los datos en dónde los acusados utilizan otros tipos de transporte sólo corresponde al 30% de los casos.

Los motociclistas tienen números estables con diferentes vehículos, lo que nos muestra que hay una problemática con este tipo de transporte.

Si dividimos la ciudad por sus comunas, podemos ver que la comuna 1 es la que mayor tasa de siniestros tiene. Esta, siendo la comuna más turística y sede de importantes edificios a nivel ciudad y nacional, es también la comuna más concurrida día a día, por lo que no es de extrañar que sea en dónde más casos de siniestros haya y en dónde continue siendo así. Esto es parcialmente confirmado gracias a que es también la comuna más peligrosa para el peaton.

Mientras tanto, la comuna 4 posee las avenidas *Coronel Roca* y *Coronel Francisco Ravanal* así como la avenida *Perito Moreno*, éstas al ser las arterias que comunican esta comuna con otros barrios de la ciudad pueden ser centro de siniestros viales gracias a la cantidad de vehículos que circulan a diario. Un análisis similar puede ser aplicado a la comuna 9.

También se puede ver que los números van bajando a lo largo del tiempo, esto se debe a que se han ido implementando más controles e invirtiendo en infraestructura a lo largo de los años. Los datos llegan a su punto más bajo en 2020, gracias a la pandemia de Covid-19.

En 2021, la comuna 4 y la comuna 9 superan a la comuna 1. Esto se debe a que varios rubros ya estaban funcionando con normalidad mientras que seguía habiendo grandes restricciones en el turismo, sin embargo, en el segundo semestre de este año, la cantidad de victimas fatales en la comuna 1 estaba creciendo.

Estas tres comunas son las que mayor cantidad de tráfico tienen día a día, ya sea vehicular o por peatón, sea en avenidas o en cualquier otro tipo de calles. Estas, que contienen grandes volúmenes de vehículos tienen una relación igualmente proporcional a la cantidad de motociclistas siendo *víctimas* de siniestros fatales y permaciendo cómo uno de los *acusados* con niveles más altos a lo largo de los años. Este factor nos hace preguntar ¿Por qué los datos aumentan tanto cuando se cumplen estas variables? Y ¿Qué papel juegan las motos y no necesariamente otros vehículos? 

Si investigamos fuentes exteriores a los datasets, podemos encontrar que a lo largo de los años se han llevado a cabo campañas de controles de tránsito, lo que ha ayudado a controlar los números de siniestros a lo largo de los años. En el año 2018 se ha llevado a cabo obras de remodelación en diversas avenidas, por lo que se produjeron cortes y desvíos en todo el año, lo que provocó que el año 2018 sea el año con más cantidad de siniestros, muchos de ellos en avenidas. Por lo que podríamos considerar a las avenidas en 2018 cómo un outlier, sin embargo, este tipo de calle sigue estando entre las más peligrosas en los demás años.

En el año 2019 se bajó considerablemente este número gracias a las mismas avenidas y al aumento de controles debido al gran número de homicidios que hubo el año anterior.
\n ### \n ###''')

### KPIs
st.write("#### **KPIs** \n *Indicadores claves*")

kpi1,kpi2 = st.columns(2) # Creo dos columnas para presentar los KPI

# Primera Columna
with kpi1:
    st.write(f"*Reducir en un 10% la tasa de homicidios en siniestros viales de los últimos seis meses.*")    
    # Fórmula del primer KPI    
    st.latex(
        r'''
        KPI = \frac{H actual}{{H anterior} * 0.9}
        '''
    )
    
    # Descipción de la fórmula
    st.write(f'''
    Dónde:\n
    + *H actual* es la cantidad de homicidios en siniestros en el último semestre\n
    + *H anterior* es la cantidad de homicidios en siniestros en el semestre anterior\n
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

### INTRODUCCIÓN
st.write("#### **Conclusiones** \n *Midiendo los siniestros*")

st.write(
    f'''
    \n ###

**Primer KPI:**

Para que se cumpla el primer KPI, el segundo semestre debería haber una cantidad de casos menor a 49.5. Hubo, en cambio, una cantidad de 42 casos. Este corresponde al 76.3% de los casos ocurridos en el primer semestre.

Si bien el objetivo se alcazó, bajando considerablemente los homicidios en siniestros, se debe comprender que  el valor sigue siendo alto, por lo que sería optimo que se realicen más controles e inversión en infraestructura de seguridad para bajar aún más el número de casos.

**Segundo KPI:**

Para que se cumpla el segundo KPI, en el año 2021 debió haber contado con menos de 26. Sin embargo, en este año ocurrieron 46 casos en total, el 164,2% comparado al año 2020.

Sin embargo, tengamos en cuenta que el año 2020 fue un caso excepcional gracias a la pandemia de COVID-19, esta, al obligar a las personas a permanecer aisladas, ha influenciado a la caída rotunda de homicidios en siniestros. Por lo que lo optimo para el estudio sería comparar al año 2021 con el año 2019.

En el 2019 hubo 50 casos en total, si tomamos este dato cómo 'SM anterior', deberíamos obtener menos de 46.5 para que el KPI se cumpla. Por lo que, al tener 46 casos en 2021 podemos ver que todavía hay mucho que mejorar.

Cómo en el primer KPI, se debe invvertir aún más en controles de transito e infraestructura, pero también sería buena idea invertir en campañas de concientización para motociclistas.

\n ### \n ###''')

#---------------------------------------------------------------------------------------------------------------------
### DASHBOARD
st.write("#### Dashboard")

## FILTROS
with st.popover('FILTROS',use_container_width=True):
    # Filtración por AÑO --------------------------------------------------------------------------
    # Creo una lista para almacenar los años
    años = []
    for i in df_final['AAAA']:
        if i not in años:
            años.append(i)

    # Ordeno la lista
    años.sort()

    # Filtro por AÑO
    años_filtradas = st.multiselect(
        "FILTRAR POR AÑO",
        años,
        años)
            

    # Filtración por COMUNAS -----------------------------------------------------------------------
    comunas = []
    for i in df_final['COMUNA']:
        if i not in comunas:
            comunas.append(i)

    # Filtro por COMUNAS
    comuna_filtradas = st.multiselect(
        "FILTRAR POR COMUNA",
        comunas,
        comunas,
        help='Selecciona una opción'
        )


    # Filtración por GRUPO ETARIO ------------------------------------------------------------------
    st.write('***Niño:*** Hasta 12 años // ***Adolescente:*** De 13 a 18 años // ***Joven Adulto:*** De 19 a 35 años // ***Adulto:*** De 36 a 50 años // ***Adulto Maduro:*** De 51 a 65 años // ***Adulto Mayor:*** Mayor de 65 años')

    # Filtro por GRUPO ETARIO
    edades_filtradas = st.multiselect(
        "FILTRAR POR GRUPO ETARIO",
        ['Niño', 'Adolescente', 'Joven Adulto', 'Adulto', 'Adulto Maduro', 'Adulto Mayor'],
        ['Niño', 'Adolescente', 'Joven Adulto', 'Adulto', 'Adulto Maduro', 'Adulto Mayor']
        )


    # Filtración por TIPO DE CALLE -----------------------------------------------------------------------
    calles = []
    for i in df_final['TIPO_DE_CALLE']:
        if i not in calles:
            calles.append(i)

    # Filtro por COMUNAS
    calles_filtradas = st.multiselect(
        "FILTRAR POR TIPO DE CALLE",
        calles,
        calles,
        help='Selecciona una opción'
        )


    ### DATAFRAME FILTRADO ###
    df_filtrado = df_final[(df_final['COMUNA'].isin(comuna_filtradas)) & (df_final['GRUPO ETARIO'].isin(edades_filtradas)) & (df_final['AAAA'].isin(años_filtradas)) & (df_final['TIPO_DE_CALLE'].isin(calles_filtradas))]


# ----------------------------------------------------------------------------------------------------------------------
st.write('####')
x = len(df_filtrado)

st.write(f"##### Casos totales: {x}")



fig = go.Figure() # Scatter Plot ----------------------------------------------------------------------------------------

# Creo una lista que contenga todos los años y la cantidad de casos en esos años
conteo_por_año = df_filtrado['AAAA'].value_counts().sort_index()

# Creo el gráfico
fig.add_trace(go.Scatter(x=conteo_por_año.index, y=conteo_por_año.values, mode='lines+markers'))

# Etiquetas
fig.update_layout(
    title='Cantidad de casos por año',
    xaxis_title='Año',
    yaxis_title='Cantidad de casos'
)
st.plotly_chart(fig,use_container_width=True)



# Creo dos columnas
superior = st.columns(2) 

with superior[0]: # Map Plot ----------------------------------------------------------------------------------------------

    Años = df_filtrado['AAAA']

    # Leo el token del map plot
    with open('mapbox_token.txt', 'r') as file:
        token = file.read()

    # Le doy acceso para setear un map plot
    px.set_mapbox_access_token(token)

    # Creo el gráfico
    fig = px.scatter_mapbox(
        df_filtrado,
        lat="pos y",
        lon="pos x",
        color="VICTIMA",
        color_continuous_scale=px.colors.sequential.Rainbow,
        size_max=15,
        zoom=10,
        title='Lugares de los siniestros'
        )
    
    # Muestro el gráfico
    st.plotly_chart(fig,use_container_width=True)


with superior[1]: # Bar Chart ------------------------------------------------------------------------------------------
    if df_filtrado is None or len(df_filtrado) == 0:
        
        # Creo un gráfico vacío
        fig = px.bar(title="Siniestros por comuna")
        
        fig.update_layout(
            yaxis_title='CONTEO',
            xaxis_title='COMUNA',
            width=600)
        
        st.plotly_chart(fig) 
        
    else:
        conteo_comunas = df_filtrado['COMUNA'].value_counts().sort_index()
        
        fig = px.bar(
            y=conteo_comunas.values,
            x=conteo_comunas.index,
            title="Siniestros por comuna")
        
        fig.update_layout(
            yaxis_title='CONTEO',
            xaxis_title='COMUNA',
            width=600)
        
        st.plotly_chart(fig)



# Creo dos columnas
inferior = st.columns(2)

with inferior[0]: # Pie Plot -------------------------------------------------------------------------------------------
    
    if df_filtrado is None or len(df_filtrado) == 0:
        # Creo un gráfico vacío
        fig = px.pie(title="Siniestros por comuna")
        st.plotly_chart(fig)
        
    else:   
        conteo_sexo = df_filtrado['SEXO'].value_counts()
        
        fig = px.pie(
            values=conteo_sexo.values,
            names=conteo_sexo.index,
            hole=.3,
            title="Sexo de las víctimas")
        
        fig.update_layout(
            width=600,
            height=400)
        
        st.plotly_chart(fig)
  
   
with inferior[1]: # Bar Plot -------------------------------------------------------------------------------------------
    
    fig = px.bar(
        df_filtrado,
        x='AAAA',
        y=['SEM_1','SEM_2'],
        title='Casos por semestres a lo largo de los años')
    
    st.plotly_chart(fig, use_container_width=True)



#---------------------------------------------------------------------------------------------------------------------
### ABOUT ME
st.write("#### Sobre el autor")
st.write(
    '''
        📌 Mi nombre es Dante. Soy un estudiante apasionado de programación y la estadística con un enfoque especial en el diseño, desarrollo e implementación de soluciones robustas por medio del Data Engineering 💻 así cómo también de la búsqueda de insights a través de los datos y del pensamiento analítico a la hora de la toma de decisiones 📊.

        📈 Me considero experto en la creación de arquitecturas escalables para procesamiento gracias a mí conocimientos de GCP y Python, cómo también del análisis de datos y el diseño de estrategias ayudándome con mi conocimiento de SQL y PowerBI. También poseo conocimientos en estadística y marketing gracias a mí tecnicatura en Diseño y Comunicación Multimedial.

        💪 Siempre en busca de desafíos que impulsen la innovación y la eficiencia en el mundo de la tecnología, mí objetivo es poder colaborar con profesionales tan apasionados cómo yo en pos de impulsar la toma de decisiones empresariales basándonos en lo que los datos pueden proveernos.

        🚀 Ante cualquier consulta no dudes en comunicarte conmigo por mí mail: daantechincuini42@gmail.com
    ''')
