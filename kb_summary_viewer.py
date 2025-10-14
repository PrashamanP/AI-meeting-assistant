import streamlit as st
import requests
import os
import json
from datetime import datetime
 
# CONFIG
DJANGO_API = os.getenv("DJANGO_API", "http://localhost:8000")
 
# Load KB Config
kb_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "api", "services", "kb_config.json")
)
with open(kb_config_path) as f:
    KB_CONFIG = json.load(f)
kb_list = list(KB_CONFIG.keys())
 
def extract_date_from_title(title):
    """Extract date from title if it contains date information"""
    # Common date patterns in titles
    import re
    date_patterns = [
        r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
        r'(\d{4}-\d{1,2}-\d{1,2})',  # YYYY-MM-DD
        r'(\w+ \d{1,2},? \d{4})',    # Month DD, YYYY
        r'(\d{1,2}-\d{1,2}-\d{4})',  # MM-DD-YYYY
    ]
   
    for pattern in date_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1)
    return None
 
def parse_date(date_str):
    """Parse date string to datetime object for sorting"""
    if not date_str:
        return datetime.min
   
    try:
        # Try different date formats
        formats = [
            '%m/%d/%Y', '%Y-%m-%d', '%B %d, %Y', '%B %d %Y',
            '%m-%d-%Y', '%d/%m/%Y', '%Y/%m/%d'
        ]
       
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
       
        # If no format matches, return min date
        return datetime.min
    except:
        return datetime.min
 
def main():
    st.set_page_config(page_title="Knowledge Base Summary Viewer", layout="wide")
    st.title("📚 Knowledge Base Summary Viewer")
 
    # Sidebar for controls
    st.sidebar.header("🎛️ Controls")
   
    kb_id = st.sidebar.selectbox("Select Knowledge Base", kb_list)
    if not kb_id:
        st.warning("Please select a KB ID.")
        return
 
    # Fetch summaries
    with st.spinner("Fetching summaries from Django backend..."):
        try:
            res = requests.get(f"{DJANGO_API}/api/kb/{kb_id}/summaries/")
            if res.status_code != 200:
                st.error("Failed to fetch summaries.")
                return
            summaries = res.json()
        except Exception as e:
            st.error(f"Error fetching summaries: {e}")
            return
 
    if not summaries:
        st.info("No summaries found for this KB.")
        return
 
    # Process summaries to extract dates and prepare for display
    processed_summaries = []
    for summary in summaries:
        # Extract date from title
        extracted_date = extract_date_from_title(summary['title'])
       
        processed_summaries.append({
            **summary,
            'extracted_date': extracted_date,
            'parsed_date': parse_date(extracted_date)
        })
 
    # Sidebar controls
    st.sidebar.markdown("---")
   
    # Sort options
    sort_by = st.sidebar.selectbox(
        "Sort by",
        ["Recording ID", "Title", "Date (if available)", "Summary Length"],
        index=0
    )
   
    sort_order = st.sidebar.radio("Sort Order", ["Ascending", "Descending"], index=1)
   
    # Search/filter
    search_term = st.sidebar.text_input("🔍 Search in titles", "").lower()
   
    # Filter by date range (if dates are available)
    dates_with_summaries = [s['extracted_date'] for s in processed_summaries if s['extracted_date']]
    if dates_with_summaries:
        st.sidebar.markdown("---")
        st.sidebar.markdown("🗓️ **Date Filter**")
        min_date = st.sidebar.date_input("From Date", value=min(parse_date(d) for d in dates_with_summaries))
        max_date = st.sidebar.date_input("To Date", value=max(parse_date(d) for d in dates_with_summaries))
 
    # Apply filters and sorting
    filtered_summaries = processed_summaries.copy()
   
    # Apply search filter
    if search_term:
        filtered_summaries = [
            s for s in filtered_summaries
            if search_term in s['title'].lower() or search_term in s['recording_id'].lower()
        ]
   
    # Apply date filter
    if dates_with_summaries:
        filtered_summaries = [
            s for s in filtered_summaries
            if not s['extracted_date'] or (
                min_date <= parse_date(s['extracted_date']).date() <= max_date
            )
        ]
   
    # Apply sorting
    reverse_sort = sort_order == "Descending"
   
    if sort_by == "Recording ID":
        filtered_summaries.sort(key=lambda x: x['recording_id'], reverse=reverse_sort)
    elif sort_by == "Title":
        filtered_summaries.sort(key=lambda x: x['title'].lower(), reverse=reverse_sort)
    elif sort_by == "Date (if available)":
        filtered_summaries.sort(key=lambda x: x['parsed_date'], reverse=reverse_sort)
    elif sort_by == "Summary Length":
        filtered_summaries.sort(key=lambda x: len(x['summary_markdown']), reverse=reverse_sort)
 
    # Display statistics
    st.sidebar.markdown("---")
    st.sidebar.markdown("📊 **Statistics**")
    st.sidebar.markdown(f"Total Meetings: {len(processed_summaries)}")
    st.sidebar.markdown(f"Filtered: {len(filtered_summaries)}")
   
    if dates_with_summaries:
        st.sidebar.markdown(f"With Dates: {len(dates_with_summaries)}")
 
    # Main content area
    st.header(f"📋 Meeting Summaries ({len(filtered_summaries)} meetings)")
   
    if not filtered_summaries:
        st.info("No meetings match your current filters.")
        return
 
    # Display options
    display_mode = st.radio(
        "Display Mode",
        ["Compact Cards", "Detailed View", "List View"],
        horizontal=True,
        index=0
    )
 
    if display_mode == "Compact Cards":
        display_compact_cards(filtered_summaries)
    elif display_mode == "Detailed View":
        display_detailed_view(filtered_summaries)
    else:
        display_list_view(filtered_summaries)
 
def display_compact_cards(summaries):
    """Display meetings in compact card format"""
    cols = st.columns(2)
   
    for idx, summary in enumerate(summaries):
        col_idx = idx % 2
        with cols[col_idx]:
            with st.container():
                st.markdown("---")
               
                # Header
                st.markdown(f"### 📌 {summary['recording_id']}")
                st.markdown(f"**{summary['title']}**")
               
                # Date if available
                if summary['extracted_date']:
                    st.caption(f"📅 {summary['extracted_date']}")
               
                # Summary preview (first 200 chars)
                preview = summary['summary_markdown'][:200] + "..." if len(summary['summary_markdown']) > 200 else summary['summary_markdown']
                st.markdown(f"*{preview}*")
               
                # Action buttons
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("🔍 View Full", key=f"view_{summary['recording_id']}"):
                        st.session_state[f"show_summary_{summary['recording_id']}"] = True
                with col2:
                    st.markdown(f"[📥 Transcript]({summary['transcript_url']})")
                with col3:
                    st.markdown(f"[🎥 Video]({summary['video_url']})")
               
                # Expandable full summary
                if st.session_state.get(f"show_summary_{summary['recording_id']}", False):
                    with st.expander("📋 Full Summary", expanded=True):
                        st.markdown(summary["summary_markdown"])
 
def display_detailed_view(summaries):
    """Display meetings in detailed format"""
    for summary in summaries:
        with st.container():
            st.markdown("---")
           
            # Header with recording ID and title
            st.markdown(f"## 📌 {summary['recording_id']}: {summary['title']}")
           
            # Metadata row
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                if summary['extracted_date']:
                    st.caption(f"📅 **Date:** {summary['extracted_date']}")
                else:
                    st.caption("📅 **Date:** Not specified")
            with col2:
                st.caption(f"📝 **Summary Length:** {len(summary['summary_markdown']):,} characters")
            with col3:
                # Toggle summary visibility
                if st.button("📋 Toggle Summary", key=f"toggle_{summary['recording_id']}"):
                    st.session_state[f"show_summary_{summary['recording_id']}"] = not st.session_state.get(f"show_summary_{summary['recording_id']}", False)
           
            # Download links
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"[📥 Download Transcript]({summary['transcript_url']})")
            with col2:
                st.markdown(f"[🎥 Download Video]({summary['video_url']})")
           
            # Expandable summary
            if st.session_state.get(f"show_summary_{summary['recording_id']}", False):
                with st.expander("📋 Meeting Summary", expanded=True):
                    st.markdown(summary["summary_markdown"])
 
def display_list_view(summaries):
    """Display meetings in a simple list format"""
    for summary in summaries:
        with st.container():
            st.markdown("---")
           
            # Simple header
            st.markdown(f"### 📌 {summary['recording_id']}: {summary['title']}")
           
            # Date if available
            if summary['extracted_date']:
                st.caption(f"📅 {summary['extracted_date']}")
           
            # Quick actions
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔍 Show Summary", key=f"list_view_{summary['recording_id']}"):
                    st.session_state[f"show_summary_{summary['recording_id']}"] = True
            with col2:
                st.markdown(f"[📥 Transcript]({summary['transcript_url']})")
            with col3:
                st.markdown(f"[🎥 Video]({summary['video_url']})")
           
            # Show summary if requested
            if st.session_state.get(f"show_summary_{summary['recording_id']}", False):
                st.markdown(summary["summary_markdown"])
 
if __name__ == "__main__":
    main()