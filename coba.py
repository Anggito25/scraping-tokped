import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS

# Pengaturan halaman
st.set_page_config(page_title="Dashboard Analisis Tokopedia", layout="wide")
st.title("📊 Dashboard Analisis Review Tokopedia")

# Upload file
with st.expander("📁 4. Upload Dataset dan Analisis", expanded=True):
    st.markdown("Upload file CSV hasil scraping (wajib ada kolom 'ulasan')")
    uploaded_file = st.file_uploader("Upload file CSV di sini", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        st.warning("⚠️ Silakan upload file CSV terlebih dahulu.")
        st.stop()

# ========================
# 1. Data Overview
# ========================
with st.expander("📋 1. Data Review Tokopedia", expanded=False):
    st.subheader("Preview Data")
    st.dataframe(df.head())
    st.info(f"Total data: {len(df)} baris")

# ========================
# 2. Visualisasi Rating
# ========================
with st.expander("⭐ 2. Analisis Rating Produk", expanded=False):
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df.dropna(subset=['Rating'], inplace=True)

    col1, col2 = st.columns(2)
    col1.metric("Rata-rata Rating", f"{df['Rating'].mean():.2f} / 5")
    col2.metric("Jumlah Ulasan", f"{df.shape[0]}")

    st.subheader("Distribusi Rating Produk")
    plt.figure(figsize=(8, 4))
    sns.histplot(df['Rating'], bins=5, kde=True, color='skyblue')
    plt.xlabel("Rating")
    plt.ylabel("Jumlah")
    st.pyplot(plt)
    plt.clf()

# ========================
# 3. Analisis Sentimen
# ========================
with st.expander("💬 3. Analisis Sentimen Ulasan", expanded=False):
    def get_sentiment(text):
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity
        if polarity > 0:
            return "Positif"
        elif polarity < 0:
            return "Negatif"
        else:
            return "Netral"

    df['Sentimen'] = df['Ulasan'].apply(get_sentiment)

    st.subheader("Contoh Data Sentimen")
    st.dataframe(df[['Ulasan', 'Rating', 'Sentimen']].head())

    st.subheader("Distribusi Sentimen")
    sentiment_counts = df['Sentimen'].value_counts()
    fig, ax = plt.subplots()
    sentiment_counts.plot(kind="bar", color=["green", "gray", "red"], ax=ax)
    plt.title("Distribusi Sentimen")
    plt.xlabel("Sentimen")
    plt.ylabel("Jumlah")
    st.pyplot(fig)

# ========================
# 4. WordCloud
# ========================
with st.expander("☁️ 4. WordCloud Review", expanded=False):
    st.subheader("WordCloud Semua Review")
    all_text = " ".join(df['Ulasan'].dropna().astype(str).str.lower())
    stopwords = set(STOPWORDS)
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords).generate(all_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)
    plt.clf()

    st.subheader("WordCloud Review Negatif")
    neg_text = " ".join(df[df['Sentimen'] == 'Negatif']['Ulasan'].dropna().astype(str).str.lower())
    if neg_text.strip():
        wordcloud_neg = WordCloud(width=800, height=400, background_color='black',
                                  stopwords=stopwords, colormap='Reds').generate(neg_text)
        st.image(wordcloud_neg.to_array(), caption='Word Cloud Sentimen Negatif')
    else:
        st.info("Tidak ada data sentimen negatif untuk divisualisasikan.")

# ========================
# 5. Daftar Ulasan Negatif
# ========================
with st.expander("😠 5. Ulasan Negatif", expanded=False):
    ulasan_negatif = df[df['Sentimen'] == 'Negatif']
    if not ulasan_negatif.empty:
        st.dataframe(ulasan_negatif[['Nama', 'Tipe Barang', 'Ulasan', 'Rating']])
    else:
        st.info("Tidak ditemukan ulasan negatif.")
