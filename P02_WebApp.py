import streamlit as st
import altair as alt
import pandas as pd

# impostazione pagina 
st.set_page_config(
    page_title="GameZone Dashboard",
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
    brush = alt.selection_interval(encodings=['x'], value = {'x' : default_interval})

    t = alt.Chart(data).mark_line(point=True).encode(
        x=alt.X('yearmonth(PURCHASE_TS):T', title='Data Acquisto'),
        y=alt.Y('sum(USD_PRICE):Q', title='Fatturato Totale ($)'),
        tooltip=['yearmonth(PURCHASE_TS)', 'sum(USD_PRICE)']
    ).properties(
        width=800,
        height=300,
        title='Andamento Temporale del Fatturato (Seleziona un intervallo qui)'
    ).add_params(
        brush
    )

    r = alt.Chart(data).mark_bar().transform_aggregate(
        Gross = 'sum(USD_PRICE)', groupby=['COUNTRY_CODE']
    ).encode(
    x=alt.X('Gross:Q', title='Fatturato ($)'),
    y=alt.Y('COUNTRY_CODE:N', sort='-x', title='Regione'),
    color=alt.Color('COUNTRY_CODE:N', legend=None, scale=alt.Scale(scheme='blues')),
    tooltip=['COUNTRY_CODE', 'Gross:Q', 'count()']
    ).transform_filter(
        'datum.Gross > 13000'
    ).properties(
        width=350,
        height=350,
        title='Fatturato per Macro-Regione (>13000$)'
    )

    h = alt.Chart(data).mark_rect().encode(
        x=alt.X('MARKETING_CHANNEL:N', title='Canale Marketing'),
        y=alt.Y('PURCHASE_PLATFORM:N', title='Piattaforma'),
        color=alt.Color('sum(USD_PRICE):Q', title='Fatturato ($)', scale=alt.Scale(scheme='plasma')),
        tooltip=['MARKETING_CHANNEL', 'PURCHASE_PLATFORM', 'sum(USD_PRICE)', 'count()']
    ).properties(
        width=400,
        height=300,
        title='Efficacia Canali e Piattaforme'
    )    

    p = alt.Chart(data).mark_bar().encode(
        x=alt.X('count():Q', title='Numero Ordini'),
        y=alt.Y('PRODUCT_NAME:N', sort='-x', title='Prodotto'),
        color=alt.Color('PRODUCT_NAME:N', legend=None, scale = alt.Scale(scheme = 'blues'))
    ).transform_window(
           rank='rank(count())',
        sort=[alt.SortField('count()', order='descending')]
    ).transform_filter(
        alt.datum.rank <= 5
    ).properties(
        width=800,
        height=200,
        title='Top 5 Prodotti Più Venduti (nel periodo selezionato)'
    )

    return t, r, h, p


t, r, h, p = create_dashboard(data)

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