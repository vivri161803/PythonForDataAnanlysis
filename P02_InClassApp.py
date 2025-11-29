import streamlit as st
import altair as alt
import pandas as pd

# impostazione pagina 
st.set_page_config(
    page_title="GameZone Dashboard (Studenti)",
    page_icon="🎮",
    layout="wide"
)

@st.cache_data
def get_data():
    # importazione dei dati 
    path = './examples/gamezone-orders-data.xlsx'
    data = pd.read_excel(path)

    # PROCESSING
    # funzione per il preprocessing del dataset gamezone 
    data_copy = data.copy()
    # conversione dei tipi automatica
    data_copy = data_copy.convert_dtypes()
    # conversione manuale 
    data_copy['USER_ID'] = data_copy['USER_ID'].astype('string')
    data_copy['PRODUCT_ID'] = data_copy['PRODUCT_ID'].astype('string')
    # tipizzazione campi date 
    data_copy['PURCHASE_TS'] = pd.to_datetime(data_copy['PURCHASE_TS'], errors='coerce')
    data_copy['SHIP_TS'] = pd.to_datetime(data_copy['SHIP_TS'], errors='coerce')
    # formattazione dei valori nella colonna PRODUCT_NAME
    product_mapping = {
    '27in 4K gaming monitor': '27in 4k Gaming Monitor',
    '27inches 4k gaming monitor': '27in 4k Gaming Monitor',
    }
    data_copy['PRODUCT_NAME'] = data_copy['PRODUCT_NAME'].replace(product_mapping)
    # rimozione valori mancanti None dalla colonna MARKETING_CHANNEL e ACCOUNT_CREATION_METHOD
    data_copy['MARKETING_CHANNEL'] = data_copy['MARKETING_CHANNEL'].fillna('unknown')
    data_copy['ACCOUNT_CREATION_METHOD'] = data_copy['ACCOUNT_CREATION_METHOD'].fillna('unknown')

    # aggiunta di nuovi campi 
    # A1. Estrazione Granularità Temporale
    data_copy['PURCHASE_YEAR'] = data_copy['PURCHASE_TS'].dt.year
    data_copy['PURCHASE_MONTH'] = data_copy['PURCHASE_TS'].dt.month_name()
    # A2. Nuova Metrica: Time to Ship (Giorni tra acquisto e spedizione)
    data_copy['TIME_TO_SHIP_DAYS'] = (data_copy['PURCHASE_TS'] - data_copy['PURCHASE_TS']).dt.days
    data_copy = data_copy.sample(5000)
    return data_copy

# carichiamo i dati
# alt.data_transformers.disable_max_rows()
data = get_data()


min_date = data['PURCHASE_TS'].min()
max_default_date = min_date + pd.Timedelta(days=90) # Default: selezione di 3 mesi
        
# Convertiamo in oggetti datetime standard per compatibilità
default_interval = [min_date.to_pydatetime(), max_default_date.to_pydatetime()]


# Disabilitiamo il limite PRIMA di creare qualsiasi grafico
alt.data_transformers.disable_max_rows()
# definizione dei grafici
def create_dashboard(data):
    # da riempire con 4 grafici differenti, secondo il gusto e le idee degli studenti 
    return None

# da levare come commento una volta che i grafici sono stati creati 
# t, r, h, p = create_dashboard(data)

# --- BARRA LATERALE PER NAVIGAZIONE ---
st.sidebar.title("Navigazione")
scelta = st.sidebar.radio(
    "Vai a:",
    ["Dashboard Completa", "Grafici Singoli", "Metadati Dataset"]
)

# --- LOGICA DELLE PAGINE ---

if scelta == "Dashboard Completa":
    col1, col2 = st.columns(2)

    with col1:
        # use_container_width=True adatta il grafico alla larghezza della colonna
        st.altair_chart(t, use_container_width=True)

    with col2:
        st.altair_chart(r, use_container_width=True)

    # Divisore visivo
    st.divider() 

    # SECONDA RIGA
    col3, col4 = st.columns(2)

    with col3:
        st.altair_chart(h, use_container_width=True)

    with col4:
        st.altair_chart(p, use_container_width=True)    


elif scelta == "Grafici Singoli":
    st.title("📈 Analisi Dettagliata")
    st.markdown("Esplora i singoli aspetti del dataset separatamente.")
        
    # Creazione Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["⏱️ Tempo", "🌍 Geografia", "📢 Marketing", "🏆 Prodotti"])
    
    with tab1:
        st.subheader("Andamento Temporale")
        st.altair_chart(t, use_container_width=True, theme='streamlit')
    
    with tab2:
        st.subheader("Performance Regionali")
        st.altair_chart(r, use_container_width=True, theme='streamlit')
    
    with tab3:
        st.subheader("Analisi Canali & Piattaforme")
        st.altair_chart(h, use_container_width=True, theme='streamlit')
        
    with tab4:
        st.subheader("Best Sellers")
        st.altair_chart(p, use_container_width=True, theme='streamlit')

elif scelta == "Metadati Dataset":
    st.title("🗂️ Metadati del Dataset")
    st.markdown("""
    Di seguito una descrizione delle colonne presenti nel dataset `orders.csv` utilizzato per questa analisi.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Informazioni sull'Ordine**")
        st.markdown("""
        - **USER_ID**: Identificativo univoco dell'utente (anonimizzato).
        - **ORDER_ID**: Identificativo univoco della transazione.
        - **USD_PRICE**: Valore della transazione in dollari statunitensi.
        - **PRODUCT_NAME**: Nome commerciale del prodotto acquistato.
        - **PRODUCT_ID**: Codice SKU del prodotto.
        """)
        
    with col2:
        st.success("**Informazioni Temporali e Canale**")
        st.markdown("""
        - **PURCHASE_TS**: Timestamp dell'acquisto (Data e Ora).
        - **SHIP_TS**: Timestamp di spedizione della merce.
        - **PURCHASE_PLATFORM**: La piattaforma usata per l'acquisto (es. *website, mobile app*).
        - **MARKETING_CHANNEL**: Il canale che ha portato l'utente all'acquisto (es. *social media, direct, affiliate*).
        - **ACCOUNT_CREATION_METHOD**: Metodo usato per creare l'account utente.
        """)
    
    st.warning("Nota: I dettagli geografici specifici risultano mancanti.")
    
    st.subheader("Anteprima Dati (Prime 5 righe)")
    st.dataframe(data.head())