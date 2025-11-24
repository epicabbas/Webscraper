"""
Web Scraper Pro - Smart Auto-Detection
Users don't need to know CSS selectors!
"""

import streamlit as st
import pandas as pd
from scraper import WebScraper
import requests
from bs4 import BeautifulSoup
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="Web Scraper Pro",
    page_icon="🕷️",
    layout="wide"
)

# Helper function to auto-detect containers
def auto_detect_containers(url):
    """Automatically detect repeating containers on a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all elements with classes
        elements_with_classes = soup.find_all(class_=True)
        
        # Count class occurrences
        class_counter = Counter()
        for elem in elements_with_classes:
            classes = elem.get('class', [])
            for cls in classes:
                class_counter[cls] += 1
        
        # Find classes that appear multiple times (likely containers)
        candidates = []
        for cls, count in class_counter.most_common(20):
            if count >= 3:  # Appears at least 3 times
                selector = f".{cls}"
                elements = soup.select(selector)
                
                # Check if elements have children (likely containers)
                if elements and len(elements[0].find_all()) > 2:
                    candidates.append({
                        'selector': selector,
                        'count': count,
                        'sample': str(elements[0])[:200]
                    })
        
        # Also check for common container patterns
        common_patterns = [
            'article', 'div.item', 'div.card', 'div.product', 
            'div.post', 'li', '.listing', '.entry'
        ]
        
        for pattern in common_patterns:
            elements = soup.select(pattern)
            if len(elements) >= 3:
                candidates.insert(0, {
                    'selector': pattern,
                    'count': len(elements),
                    'sample': str(elements[0])[:200]
                })
        
        return candidates[:5]  # Return top 5
        
    except Exception as e:
        return []

# Title
st.title("🕷️ Web Scraper Pro")
st.markdown("### Extract data from any website - No coding needed!")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Scraper Mode")

mode = st.sidebar.radio(
    "Choose mode:",
    ["📚 Pre-built Scrapers", "🤖 Smart Custom Scraper"]
)

st.sidebar.markdown("---")

# =============================================================================
# MODE 1: PRE-BUILT SCRAPERS (Same as before)
# =============================================================================

if mode == "📚 Pre-built Scrapers":
    
    st.sidebar.header("Settings")
    
    scraper_type = st.sidebar.selectbox(
        "Choose what to scrape:",
        ["Quotes", "Books"]
    )
    
    if scraper_type == "Books":
        num_pages = st.sidebar.slider("Number of pages", 1, 10, 3)
    else:
        num_pages = 1
    
    if st.sidebar.button("🚀 Start Scraping", type="primary"):
        
        with st.spinner("Scraping in progress..."):
            
            if scraper_type == "Quotes":
                st.info("📚 Scraping quotes from quotes.toscrape.com...")
                scraper = WebScraper("http://quotes.toscrape.com", delay=0.5)
                data = scraper.scrape_quotes()
                filename = "quotes_data.csv"
                
            else:
                st.info(f"📖 Scraping {num_pages} pages of books...")
                scraper = WebScraper("http://books.toscrape.com", delay=0.5)
                data = scraper.scrape_books(num_pages=num_pages)
                filename = "books_data.csv"
            
            if data:
                df = pd.DataFrame(data)
                
                st.success(f"✅ Successfully scraped {len(data)} items!")
                
                # Statistics
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
                
                st.markdown("### 📋 Scraped Data")
                st.dataframe(df, use_container_width=True)
                
                if scraper_type == "Books":
                    st.markdown("### ⭐ Rating Distribution")
                    rating_counts = df['rating'].value_counts()
                    st.bar_chart(rating_counts)
                
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
        st.info("👈 Configure settings and click 'Start Scraping'")

# =============================================================================
# MODE 2: SMART CUSTOM SCRAPER
# =============================================================================

else:
    
    st.markdown("### 🤖 Smart Custom Scraper")
    st.markdown("Just enter a URL and let AI find the data for you!")
    
    # Step 1: URL Input
    st.markdown("#### Step 1: Enter Website URL")
    url = st.text_input(
        "🌐 Website URL",
        placeholder="https://example.com",
        help="Enter the website you want to scrape"
    )
    
    # Initialize session state
    if 'detected_containers' not in st.session_state:
        st.session_state.detected_containers = []
    if 'selected_container' not in st.session_state:
        st.session_state.selected_container = None
    
    # Auto-detect button
    if url:
        if st.button("🔍 Auto-Detect Data", type="primary"):
            with st.spinner("🤖 Analyzing webpage..."):
                candidates = auto_detect_containers(url)
                
                if candidates:
                    st.session_state.detected_containers = candidates
                    st.success(f"✅ Found {len(candidates)} potential data containers!")
                else:
                    st.warning("⚠️ Couldn't auto-detect containers. Try manual mode below.")
    
    # Show detected containers
    if st.session_state.detected_containers:
        st.markdown("#### Step 2: Select Container Type")
        st.info("👇 Choose which items you want to scrape:")
        
        for idx, candidate in enumerate(st.session_state.detected_containers):
            with st.expander(f"Option {idx+1}: {candidate['selector']} ({candidate['count']} items found)"):
                st.code(candidate['sample'], language="html")
                
                if st.button(f"✅ Use This Container", key=f"select_{idx}"):
                    st.session_state.selected_container = candidate['selector']
                    st.success(f"Selected: {candidate['selector']}")
                    st.rerun()
    
    # If container selected, show field detection
    if st.session_state.selected_container:
        st.markdown("#### Step 3: Extract Data")
        
        container_selector = st.session_state.selected_container
        st.info(f"Using container: `{container_selector}`")
        
        # How many items to scrape
        max_items = st.slider("Number of items to scrape", 1, 50, 10)
        
        if st.button("🚀 Scrape Data Now", type="primary"):
            with st.spinner("Extracting data..."):
                try:
                    response = requests.get(url, timeout=15)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    containers = soup.select(container_selector)[:max_items]
                    
                    if not containers:
                        st.error("No items found!")
                    else:
                        # Extract ALL text from each container
                        data = []
                        
                        for idx, container in enumerate(containers):
                            # Get all text elements
                            text_elements = container.find_all(string=True, recursive=True)
                            text_elements = [t.strip() for t in text_elements if t.strip()]
                            
                            # Create item with numbered fields
                            item = {}
                            for i, text in enumerate(text_elements[:10]):  # Max 10 fields
                                if len(text) > 2:  # Ignore very short text
                                    item[f'field_{i+1}'] = text
                            
                            if item:
                                data.append(item)
                        
                        if data:
                            df = pd.DataFrame(data)
                            
                            st.success(f"✅ Successfully scraped {len(data)} items!")
                            
                            # Show statistics
                            st.metric("Total Items", len(df))
                            
                            # Display data
                            st.markdown("### 📋 Scraped Data")
                            st.dataframe(df, use_container_width=True)
                            
                            # Download
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv,
                                file_name="custom_scrape.csv",
                                mime="text/csv",
                                type="primary"
                            )
                        else:
                            st.warning("No data extracted")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Manual mode option
    with st.expander("🔧 Advanced: Manual Selector Mode"):
        st.markdown("For experienced users who know CSS selectors")
        
        manual_container = st.text_input("Container Selector", placeholder="div.item")
        manual_field1 = st.text_input("Field 1 Selector", placeholder="h2.title")
        manual_field2 = st.text_input("Field 2 Selector", placeholder="p.description")
        
        if st.button("Scrape with Manual Selectors"):
            st.info("Manual scraping mode - Coming soon!")
    
    # Help section
    with st.expander("❓ How It Works"):
        st.markdown("""
        ### 🤖 Smart Scraping in 3 Steps:
        
        1. **Enter URL** - Just paste the website link
        2. **Auto-Detect** - AI finds repeating data patterns
        3. **Select & Scrape** - Choose what you want and download!
        
        ### ✨ Features:
        
        - ✅ No CSS knowledge needed
        - ✅ Automatic pattern detection
        - ✅ Preview before scraping
        - ✅ Export to CSV
        - ✅ Works on most websites
        
        ### 💡 Tips:
        
        - Works best on pages with lists (products, articles, posts)
        - Try scraping listing/category pages, not individual pages
        - If auto-detect fails, use manual mode
        """)

# Footer
st.markdown("---")
st.markdown("🤖 Powered by AI | Made with ❤️ using Streamlit")