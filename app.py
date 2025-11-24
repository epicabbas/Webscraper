"""
Web Scraper - Streamlit Web Interface
A user-friendly interface for the web scraper
"""

import streamlit as st
import pandas as pd
from scraper import WebScraper
import time

# Page configuration
st.set_page_config(
    page_title="Web Scraper Pro",
    page_icon="🕷️",
    layout="wide"
)

# Title and description
st.title("🕷️ Web Scraper Pro")
st.markdown("### Extract data from websites with ease!")
st.markdown("---")

# Sidebar for options
st.sidebar.header("⚙️ Scraper Settings")

# Select scraper type
scraper_type = st.sidebar.selectbox(
    "Choose what to scrape:",
    ["Quotes", "Books"]
)

# Settings based on type
if scraper_type == "Books":
    num_pages = st.sidebar.slider("Number of pages", 1, 10, 3)
else:
    num_pages = 1

# Add a run button
if st.sidebar.button("🚀 Start Scraping", type="primary"):
    
    # Show progress
    with st.spinner("Scraping in progress..."):
        
        if scraper_type == "Quotes":
            st.info("📚 Scraping quotes from quotes.toscrape.com...")
            scraper = WebScraper("http://quotes.toscrape.com", delay=0.5)
            data = scraper.scrape_quotes()
            filename = "quotes_data.csv"
            
        else:  # Books
            st.info(f"📖 Scraping {num_pages} pages of books...")
            scraper = WebScraper("http://books.toscrape.com", delay=0.5)
            data = scraper.scrape_books(num_pages=num_pages)
            filename = "books_data.csv"
        
        # Check if data was scraped
        if data:
            df = pd.DataFrame(data)
            
            # Success message
            st.success(f"✅ Successfully scraped {len(data)} items!")
            
            # Display statistics
            st.markdown("### 📊 Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", len(df))
            
            with col2:
                if scraper_type == "Books":
                    st.metric("Average Price", f"£{df['price'].mean():.2f}")
                else:
                    st.metric("Unique Authors", df['author'].nunique())
            
            with col3:
                if scraper_type == "Books":
                    st.metric("Most Expensive", f"£{df['price'].max():.2f}")
                else:
                    st.metric("Total Tags", df['tags'].str.split(',').explode().nunique())
            
            # Display the data
            st.markdown("### 📋 Scraped Data")
            st.dataframe(df, use_container_width=True)
            
            # Additional analysis for books
            if scraper_type == "Books":
                st.markdown("### ⭐ Rating Distribution")
                rating_counts = df['rating'].value_counts()
                st.bar_chart(rating_counts)
            
            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=filename,
                mime="text/csv",
                type="primary"
            )
            
        else:
            st.error("❌ Failed to scrape data. Please try again.")

else:
    # Instructions when not running
    st.info("👈 Configure settings in the sidebar and click 'Start Scraping'")
    
    st.markdown("""
    ### 🎯 How to Use:
    
    1. **Choose what to scrape** from the sidebar
    2. **Adjust settings** (number of pages for books)
    3. **Click "Start Scraping"** button
    4. **View results** and download CSV
    
    ### 📚 Available Scrapers:
    
    - **Quotes:** Inspirational quotes with authors and tags
    - **Books:** Book titles, prices, ratings, and availability
    
    ### ✨ Features:
    
    - Real-time scraping
    - Data visualization
    - CSV export
    - No coding required!
    """)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit | [View Source on GitHub](https://github.com/epicabbas/Webscraper.git)")