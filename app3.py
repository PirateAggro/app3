# Install required libraries
# Run these commands in your terminal or command prompt
# pip install streamlit
# pip install gspread
# pip install oauth2client

import streamlit as st
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_option_menu import option_menu
from datetime import datetime, timezone, timedelta, date
from google.cloud import firestore
import gspread
#from gspread_dataframe import set_with_dataframe



# Authenticate to Firestore with the JSON account key.
# db = firestore.Client.from_service_account_json("firestore-key.json")

# Streamlit app
# df_products loaded
# df_clients loaded
# df_bookings = loaded

# Function to read data from Google
@st.cache_data
def read_google_sheet_x(sheet_url):
    
    # Use credentials to create a client to interact with Google Drive API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("hola-407517-a0a85576df69.json", scope)
    gc = gspread.authorize(credentials)

    # Open the Google Sheet using its URL
    worksheet = gc.open_by_url(sheet_url).sheet1

    # Get the data as a Pandas DataFrame
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    return df

def write_google_sheet_x(dt):

    sheet_url = "https://docs.google.com/spreadsheets/d/16AbAcJcrp5RL-dEO5EjddgqJlwu9JUo-DjzS5tZlzUU/edit?pli=1#gid=1859943936"

    # Google Sheets credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("hola-407517-a0a85576df69.json", scope)
    gc = gspread.authorize(credentials)

    sheet = gc.open_by_url(sheet_url).sheet1
    last_row = len(sheet.get_all_values())+1
    st.write(dt)

    for i, row in dt.iterrows():  
        if row['Codi Material'] != "":
            words = row['Reservat per'].split("-")
            # Access each word separately
            word1 = words[0]
            word2 = words[1]

            sheet.update_cell(last_row,1, words[0])  #codi client
            sheet.update_cell(last_row,2, words[1])  #nom client
            sheet.update_cell(last_row,3, row['0'])  #TIPUS
            sheet.update_cell(last_row,4, row['Codi Material'])  #codi material
            # sheet.update_cell(last_row,5,  )  #descripcio material
            sheet.update_cell(last_row,6, row['Quantitat'])  #quantitat
            sheet.update_cell(last_row,7, datetime.now().strftime('%d/%m/%Y'))  #data reserva
            sheet.update_cell(last_row,8, row['Data Inici'].strftime('%d/%m/%Y'))  #data inici
            sheet.update_cell(last_row,9, row['Data Final'].strftime('%d/%m/%Y') )    #data fi
            sheet.update_cell(last_row,10, 'pendent' )  #estat
            sheet.update_cell(last_row,11, row['Docent'])  #rebut per
            # sheet.update_cell(last_row,12, )  #estat
            # sheet.update_cell(last_row,13, )  #comentari
            last_row = last_row+1



def check_reserva(product_code_selected,quantitat, start_date2, end_date2):

    # Recuperar full reserves actualitzat
    sheet_url = "https://docs.google.com/spreadsheets/d/16AbAcJcrp5RL-dEO5EjddgqJlwu9JUo-DjzS5tZlzUU/edit#gid=0"
    if 'df_reserves' not in st.session_state:
        st.session_state.df_reserves = None
    df_reserves = read_google_sheet_x(sheet_url)
    #st.session_state.df_clients = df_clients
    #st.write(df_reserves)
    #st.write("Reloaded reserves")

    Assigned_flag = " "

    # Recuperar tots els productes del tipus seleccionat
    #filtered_df_reserves_1 = df_reserves[df_reserves['estat']=="pendent"]
    #filtered_df_reserves = filtered_df_reserves_1[filtered_df_reserves_1['TIPUS']==product_code_selected]
    filtered_df_productes_0 = df_products[df_products['Producte']==product_code_selected]
    filtered_df_productes_1 = filtered_df_productes_0[filtered_df_productes_0['estat']=="disponible"]
    #st.write(filtered_df_productes_1)
  
    # si algun producte no te reserva, s'assigna

    for i in range(1,quantitat+1):
        next_loop = False
        Assigned_flag = " "

        for index, row in filtered_df_productes_1.iterrows(): 
            next_loop = False
            producte = row['Codi']

            #if producte in Assigned_product:   # el producte ja ha estat prèviament assignat
            #    next_loop = True
            #    st.write(producte, "ja assignat prèviament")
            #st.write(row['Codi'], " - ", Assigned_product)
            for row in Assigned_product:
                if row[1] == producte:
                    next_loop = True
                    #st.write(producte, "ja assignat prèviament")

            if next_loop == False:
                filtered_df_reserves_1 = df_reserves[df_reserves['estat']=="pendent"]
                filtered_df_reserves = filtered_df_reserves_1[filtered_df_reserves_1['material']==producte]
                #st.write(filtered_df_reserves)     
                if filtered_df_reserves.empty and Assigned_flag == " ":
                    new_row = [product_code_selected, producte]
                    Assigned_product.append(new_row)
                    Assigned_flag = "x"
                    #st.write(Assigned_product)


            if Assigned_flag == " " and next_loop == False:  # tots els codis tenen alguna reserva --> mirar dates

                flag_check_data = ""
                flag_validesa_reserva = False
                product_assigned = ""
                # reserves pendents d'aquell tipus de codi
                filtered_df_reserves_1 = df_reserves[df_reserves['estat']=="pendent"]
                #filtered_df_reserves = filtered_df_reserves_1[filtered_df_reserves_1['TIPUS']==product_code_selected]
                filtered_df_reserves = filtered_df_reserves_1[filtered_df_reserves_1['material']==producte]

                #query_check = db.collection('Reserves').where('Material', '==', product_code_selected).where('Estat_entrega', '==', 'pendent')
                flag_check_data = ""
                for index, row in filtered_df_reserves.iterrows(): 
                #for doc in query_check.stream():

                    Data_Inici = row['data_inici']
                    Data_Inici2 = pd.to_datetime(Data_Inici, format='%d/%m/%Y')
                    #st.write(Data_Inici2)
                    Data_Final = row['data_fi']
                    Data_Final2 = pd.to_datetime(Data_Final, format='%d/%m/%Y')
                    #st.write(Data_Final2)
                    #if flag_validesa_reserva == False:
                    #st.write("dins loop", row['material'])
                    # només que hi hagi un cas de Fals --> fals 
                    if Data_Inici2.date() <= start_date2 <= Data_Final2.date() or Data_Inici2.date() <= end_date2 <= Data_Final2.date():
                        #st.write("La reserva no és possible.")
                        flag_validesa_reserva = False
                        flag_check_data = "X"
                    elif start_date2 <= Data_Inici2.date() and end_date2 >= Data_Final2.date():
                        #st.write("La reserva no és possible.")
                        flag_validesa_reserva = False
                        flag_check_data = "X"
                        #Assigned_product = " "
                    else:
                        if flag_check_data == "":
                            flag_validesa_reserva = True 
                            #st.write("La reserva sí és possible.")
                    
                if flag_validesa_reserva == True:    
                    new_row = [product_code_selected, row['material']]
                    Assigned_product.append(new_row)
                    Assigned_flag = "X"

    return Assigned_product

# LOAD RESERVES FROM GOOGLE SHEET

sheet_url = "https://docs.google.com/spreadsheets/d/16AbAcJcrp5RL-dEO5EjddgqJlwu9JUo-DjzS5tZlzUU/edit#gid=0"
if 'df_reserves' not in st.session_state:
    st.session_state.df_reserves = None
df_reserves = read_google_sheet_x(sheet_url)
#st.session_state.df_clients = df_clients
st.write("Reserves loaded")

# LOAD CLIENTS FROM GOOGLE SHEET
sheet_url = "https://docs.google.com/spreadsheets/d/1uMANAvFf14030QZHner0incZyE2Tj9ex04Uiu1H-ldE/edit#gid=0"
if 'df_clients' not in st.session_state:
    st.session_state.df_clients = None
df_clients = read_google_sheet_x(sheet_url)
#st.session_state.df_clients = df_clients
st.write("Clients loaded")


sheet_url = "https://docs.google.com/spreadsheets/d/10OJjKforD1t0VSG1ynpa5QlQ2WbvmXDCGz8R4yxkoXM/edit#gid=0"

if 'df_products' not in st.session_state:
    st.session_state.df_products = None
df_products = read_google_sheet_x(sheet_url)
st.session_state.df_products = df_products
st.write("Products loaded")

# VARIABLES DEFINITION

unique_clients_code = []
unique_clients_code.append(" ")

unique_docents_code = []
unique_docents_code.append(" ")

unique_clients_name = []
unique_clients_name.append(" ")

unique_products_code = []
unique_products_code.append(" ")

unique_products_type = []
unique_products_type.append(" ")

unique_products_docents_type = []
unique_products_docents_type.append(" ")

Assigned_product = []

reserves_check = ""

ambit = " "
data = []

# LAYOUT DEFINITION 

esquerra, dreta = st.columns(2)

# STYLE OF TABLE CLIENTS

# style
th_props = [
('font-size', '14px'),
('text-align', 'center'),
('font-weight', 'bold'),
('color', '#6d6d6d'),
('background-color', '#c4ffff')
]
                            
td_props = [
    
('font-size', '12px'),
('background-color', '#f0f0f0')
]

td_props_senar = [
('font-size', '12px'),
('background-color', '#000000')
]
                                
styles = [
dict(selector="th", props=th_props),
dict(selector="td", props=td_props)
]

# END STYLE CLIENTS TABLE

# -------------------------------------------------------
# GENERATE SELECTBOX PER RESERVADOR I DOCENT

for index, row in df_clients.iterrows():
    for column in df_clients.columns:
        
        if column == "Nom":
            nom = row[column]
            #st.write(f"Element at index {index} and column {column}: {row[column]}")
            #st.write(nom)
        if column == "Alumne":
            alumne = row[column]
            #st.write(f"Element at index {index} and column {column}: {row[column]}")
            #st.write(alumne)
        if column == "AP":
            ambit =row[column]
            
    concat = str(alumne) + " - "+ nom
    if ambit == "P":
        concatp = str(alumne) + " - "+ nom
        unique_docents_code.append(concatp)
    #st.write(concat)
    unique_clients_code.append(concat)



    
with esquerra:
    selected_codi = st.selectbox('Reserva a nom de:', unique_clients_code)
    if selected_codi:
        #parts = selected_codi.split('-')
        position = selected_codi.find('-')
        if position != -1:
            substring = selected_codi[:position]    
            # st.write(substring)
            subint = int(substring.strip())
            # st.write(substring)
            filtered_df = df_clients[df_clients['Alumne']==subint]
            nom_codi = filtered_df['Nom']
            ambit_a = filtered_df['AP']
            ambit_1 = ambit_a.iloc[0]
            for idx in filtered_df.index:
                nom_codi_index = idx
            
            #filtered_df_prod = df_products[df_products['Tipus']==ambit_a]
            #st.write(filtered_df_prod)


# for row in df_clients.itertuples(index=False):
#     for value in row:

with dreta:       
        selected_docent = st.selectbox('Docent que autoritza:', unique_docents_code)
        #button_clicked_docent = st.button("Seleccionat")
        if selected_docent != " ":
            position_d = selected_docent.find('-')
            if position != -1:
                substring_d = selected_docent[:position_d]    
                #st.write(substring_d)
                subint_d = int(substring_d.strip())
                #st.write(substring_d)
                filtered_df_d = df_clients[df_clients['Alumne']==subint_d]
                nom_codi_d = filtered_df_d['Nom']
                #st.write("nom_codi_d :", nom_codi_d)
                for idx_d in filtered_df_d.index:
                    nom_codi_d_index = idx_d


if selected_codi != "" and selected_codi != " " and selected_docent != " ":
    
    if ambit_1 == "A":
        filtered_df_prod = df_products[df_products['TIPUS']==ambit_1]
    else:
        filtered_df_prod = df_products

    filtered_df_prod.sort_values(by='TIPUS')

    edited_values = []
   
    unique_products_list = filtered_df_prod['Producte'].unique()
    #unique_df = pd.DataFrame(unique_products_list, columns=['Tipus Material'])

   
    unique_df = pd.DataFrame(unique_products_list)
    for index, row in unique_df.iterrows(): 
        unique_df['Quantitat'] = 1
        unique_df['Data Inici'] = datetime.now().date()
        unique_df['Data Final'] = datetime.now().date() + timedelta(days=7) 
        unique_df['Reserva'] = False

 # USUARI SELECCIONA TIPUS MATERIAL I QUANTITAT A RESERVAR

    edited_df = st.data_editor(unique_df,
                    column_config={
                    "favorite": st.column_config.CheckboxColumn(
                        "Your favorite?",
                        help="Select your **favorite** widgets",
                        default=False,
                    )
                },
                disabled=["widgets"],
                hide_index=True,
                num_rows="dynamic",
                height = 700
                )  

# LLISTA MATERIALS A RESERVAR
    reserva_df = edited_df[edited_df['Reserva']==True]
    #st.write("LLISTA MATERIALS A RESERVAR")
    #st.write(reserva_df)
    
    codi_assignat = []
    
    for index, row in reserva_df.iterrows(): 
        index_original = index
        product_code_selected = row['0']
        quantitat = row['Quantitat']
        inici = row['Data Inici']
        final = row['Data Final']

        #st.write(index)
        # Codis de producte 
        #for i in range(1, quantitat): 
        #st.write("Cerca del producte : ",product_code_selected, "Quantitat", quantitat)
        codi_assignat =  check_reserva(product_code_selected, quantitat, inici, final)

        #st.write("despres check_reserva : ",codi_assignat[0])
        #filtered_df_productes_1 = df_products[df_products['Codi'] == codi_assignat[index]]
        #st.write("A gs reserva : codi client: ", subint, "Nom client: ", nom_codi, "docent : ", subint_d, "Nom Docent ", nom_codi_d )
        #st.write("A gs reserva : TIPUS: ", product_code_selected, "Codi Material: ", codi_assignat, "Descripció : ", row['descripció'], "Quantitat ", quantitat )
        #st.write("A gs reserva : Data Reserva: ", datetime.now().date(), "Data Inici: ", inici, "Data fi : ", final)        
        

        # si reserva_flag = true ---> Algun producte cumpleix
    if len(codi_assignat) == 0:
        st.write('RESERVA NO DISPONIBLE')
    else:
        #st.write(codi_assignat)

    # st.write(codi_assignat[0])
        number_of_items = len(reserva_df)
        number_of_docents = len(nom_codi_d)

    # for i in range (0,number_of_items):
    #     reserva_df.loc[i,'Codi_Material'] = codi_assignat[i]
    # st.write(reserva_df)
        
        codi_enviar = []
        codi_ass = ""
        index_1 = 90
        count = 0
        data_ini = datetime.now().date()
        data_fini = datetime.now().date()

        st.write("-------------------------")
        #st.write(reserva_df)
        #st.write(codi_assignat_df)
        for index, row in reserva_df.iterrows():  # index 0 i 1
            if row['Quantitat'] == 1:
                for i, row_as in enumerate(codi_assignat):
                    #for j, value in enumerate(row):
                        if codi_assignat[i][0] == row['0']:
                            reserva_df.loc[index, 'Codi Material'] = codi_assignat[i][1]
                            reserva_df.loc[index, 'Reservat per'] = selected_codi
                            reserva_df.loc[index, 'Docent'] = selected_docent
                            reserva_df.loc[index, 'Reserva'] = False
                            codi_assignat[i][0] = "assignat"
                            #st.write(codi_assignat)
            else:
                #st.write("quantitat = ", row['Quantitat'])
                for j in range(0, row['Quantitat']):
                    #st.write("j = ",j)
                    if j == 0:
                        codi_ass = ""
                        for i, row_as in enumerate(codi_assignat):
                            if codi_assignat[i][0] == row['0']:
                                if codi_ass == "":
                                    reserva_df.loc[index, 'Codi Material'] = codi_assignat[i][1]   
                                    reserva_df.loc[index, 'Quantitat'] = 1            
                                    data_ini = reserva_df.loc[index, 'Data Inici']  
                                    data_fini = reserva_df.loc[index, 'Data Final']  
                                    reserva_df.loc[index, 'Reservat per'] = selected_codi
                                    reserva_df.loc[index, 'Docent'] = selected_docent 
                                    reserva_df.loc[index, 'Reserva'] = False
                                    codi_assignat[i][0] = "assignat"
                                    #st.write("codi assignat", i, "0 :",codi_assignat[i][1] , " row[0]:", row[0])
                                codi_ass = "X"
                                #st.write(codi_assignat)

                    else:  # crear nova entrada a reserva_df
                        codi_ass = ""
                        index_1 = index_1 + 1
                        reserva_df.loc[index+index_1,'0'] = row[0]
                        reserva_df.loc[index+index_1, 'Quantitat'] = 1  
                        reserva_df.loc[index+index_1, 'Data Inici'] = data_ini
                        reserva_df.loc[index+index_1, 'Data Final'] = data_fini
                        reserva_df.loc[index+index_1, 'Reservat per'] = selected_codi
                        reserva_df.loc[index+index_1, 'Docent'] = selected_docent
                        reserva_df.loc[index+index_1, 'Reserva'] = False
                        codi_ass = ""
                        for k, row_k in enumerate(codi_assignat):
                            if  row_k[0]== row['0'] and row_k[1] != "assignat" and codi_ass == "":
                                reserva_df.loc[index+index_1, 'Codi Material'] = row_k[1] 
                                #st.write("codi assignat ", k, "0 :", row_k[1] , " row[0]:", row[0])  
                                codi_assignat[k][0] = "assignat"                         
                                codi_ass = "X"
                                #st.write(codi_assignat)
        
        pd.set_option('display.max_columns', None)  # Display all columns


        reserva_df_sorted = reserva_df.sort_values(by='0')
        #st.write(reserva_df_sorted)
        st.write(" Material proposat. Podeu modificar-lo (verifiqueu les dades)")
        edited_reserva_sorted = st.data_editor(reserva_df_sorted)

        
    # WRITE A RESERVES 
        
        #write_google_sheet_x(reserva_df)
        if st.button('FER LA RESERVA'):
            # Open the Google Sheet by title
            #sheet = gc.open_by_url(sheet_url).sheet1
            #last_row = len(sheet.get_all_values())+1

            #for index, row in reserva_df_sorted.iterrows():  
            write_google_sheet_x(edited_reserva_sorted)
                    

 