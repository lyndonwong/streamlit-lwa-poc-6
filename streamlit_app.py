# LWA POC 6 2025-09-08
# Pursues code changes to connect streamlit LWA POC app to Menlo Park City Council data.

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
# add pin clustering
from folium.plugins import MarkerCluster
# add audio stream support
import io
# add video stream support
from streamlit_player import st_player
# add altair charting
import altair as alt
import requests

# FUNCTIONS

# Generalized function for user feedback on app features
def submit_feedback_widget(context_label):
    """Reusable feedback widget that clears itself after submission."""
    
    # Define keys for session state
    rating_key = f"rating_{context_label}"
    feedback_key = f"feedback_{context_label}"
    submitted_key = f"submitted_{context_label}"

    # The callback function to handle the form submission
    def handle_submission():
        # Retrieve values from session state
        rating_value = st.session_state[rating_key]
        feedback_value = st.session_state[feedback_key]
        
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfpNBurxpNOKliavTR5l8b-QABvXrD7dH-wlaWRCNGYWkGGGg/formResponse"
        form_data = {
            "entry.407434206": context_label,
            "entry.1395096716": str(rating_value + 1), # Convert 0-4 to 1-5 string
            "entry.1507719363": feedback_value if feedback_value else "No additional comments"
        }
        
        try:
            response = requests.post(form_url, data=form_data, timeout=5)
            if response.ok:
                st.session_state[submitted_key] = True # Set a flag for success
                # --- FIX: Clear the widgets by resetting their session state values ---
                st.session_state[rating_key] = None 
                st.session_state[feedback_key] = ""
            else:
                st.session_state[submitted_key] = f"Error: {response.status_code}"
        except Exception as e:
            st.session_state[submitted_key] = f"Error: {e}"

    with st.expander("💬 Please rate the " + context_label, expanded=False):
        st.feedback("stars", key=rating_key)
        st.text_area(
            "How could we improve it?", 
            key=feedback_key,
            placeholder="Optional: Share specific suggestions..."
        )
        
        # Disable the button if no rating is selected
        is_disabled = st.session_state.get(rating_key) is None
        
        st.button(
            "Submit Feedback", 
            key=f"submit_{context_label}", 
            on_click=handle_submission,
            disabled=is_disabled
        )

        if is_disabled and st.session_state.get(f'button_clicked_{context_label}', False):
             st.warning("⭐ Please select a star rating before submitting.")

    # Display submission status outside the expander, based on the session state flag
    if submitted_key in st.session_state:
        result = st.session_state[submitted_key]
        if result is True:
            st.success("✅ Thank you for your feedback!")
        else:
            st.error(f"❌ Submission failed. {result}")
        # Clean up the flag so the message disappears on the next interaction
        del st.session_state[submitted_key]


# DEPRECATE for this test
# # Bypass streamlit_folium component, which has bug that causes empty space at bottom of map
# import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.logo("images/LWA-v2-square.png", size="large")    
# st.image("images/LWA_demolab_1920x360px.png", use_container_width=True )
st.title("Menlo Park City Council Recap")

# decorative image of the town
# st.image("images/Menlo_Park_960px.jpg", use_container_width=True) # TBD replace with high-level metrics or other value-add analytic summary

# Short overview
# [2025-08-25] TO DO: should modify to scan external .md file for this content, instead of hardcoding
# [2025-09-01] Copied and lightly edited MPPC summary from LLM response
st.markdown('''
            ##### Overview of Council meetings 1H 2025:
            A prominent theme across Menlo Park's City Council meetings is **housing development**, particularly the controversial proposal for **affordable housing on downtown parking lots**, which elicits significant public comment both in favor and opposition due to concerns about parking, business impact, and alternative sites like the Civic Center. Additionally, the council actively discusses **environmental and infrastructure issues**, including **climate action, flood control projects like Safer Bay, and updates to the Bayfront Recycled Water Facility**. **Fiscal matters, such as budget adoption, capital improvement plans, and aquatic center funding**, are also recurring topics, reflecting the city's financial planning and resource allocation. Finally, **transportation and community engagement** are consistently addressed, highlighting discussions around **safe routes, bike lanes, and the role of advisory bodies** like the Youth Advisory Committee. 
            ''')

# ANALYSES FROM VARIOUS PERSPECTIVES
st.header("Interpretations")

# # Explainer video
# st.subheader("The Explainer")
# st.write("Your 7 minute video on Palo Alto's real estate investment climate in mid 2025.")
# st_player("https://player.vimeo.com/video/1109170740")

# Select explainers via tabs
tab_homeowners, tab_renters, tab_investors = st.tabs(["For Homeowners", "For Renters", "For Investors"])

with tab_homeowners:
    st.subheader("For Homeowners")
    st.write("A 7-minute video on how 1H 2025 City Council activity may affect homeowners.")
    st_player("https://player.vimeo.com/video/1117583808")

with tab_renters:
    st.subheader("For Renters")
    st.write("A 7-minute video on how 1H 2025 City Council activity may affect renters.")
    st_player("https://player.vimeo.com/video/1117597380")

with tab_investors:
    st.subheader("For Investors")
    st.write("A 7-minute video on how 1H 2025 City Council activity may affect investors.")
    st_player("https://player.vimeo.com/video/1117612952")

# Feedback on interpretive videos feature
submit_feedback_widget("interpretive_videos")

# SUMMARY VISUALIZATIONS ON TOPICS, PROJECTS, COMMISSIONERS


# PROJECT MAP
# INTERACTIVE MAP of projects discussed
st.subheader("Project Map", anchor="project-map")
st.write("Hover over the pins to see detailed project information. Click on a pin for a popup and to see the project name below.")
st.markdown("[CLICK HERE FOR DETAILS on each project](#project-details)")

# Load the data from the uploaded CSV file
# Ensure the CSV file 'MPPC_projects_1H2025_2025-08-06_map_source.csv' is available in the environment.
try:
    # Using the exact filename provided by the user
    df = pd.read_csv("mpcc_projects_2025-09-08_geocoded_fixed.csv")
except FileNotFoundError:
    st.error("Error: The CSV file 'mpcc_projects_2025-09-08_geocoded_fixed' was not found.")
    st.stop()

# --- Data Preprocessing and Handling Missing Values ---

# Rename columns for easier access (optional, but good practice)
df.rename(columns={
    'project_name': 'project',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'street_address': 'address',
    'city': 'city',
    'project_description': 'description',
    'project_url': 'url', 
    'first_mention_date': 'earliest_mention_date', # Renamed
    'last_mention_date': 'latest_mention_date'    # Renamed
}, inplace=True)

# Convert latitude and longitude to numeric, coercing errors to NaN
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

# Filter out rows where latitude or longitude are missing, as these cannot be plotted
initial_rows = len(df)
df.dropna(subset=['latitude', 'longitude'], inplace=True)
if len(df) < initial_rows:
    st.warning(f"Removed {initial_rows - len(df)} rows due to missing Latitude or Longitude data.")

# Further filter to ensure only Menlo Park projects are shown (if 'City' column exists and is needed)
if 'city' in df.columns:
    df = df[df['city'].astype(str).str.contains('Menlo Park', case=False, na=False)]
    if df.empty:
        st.warning("No projects found for Menlo Park after filtering.")
        st.stop()
else:
    st.warning("The 'City' column was not found in the CSV. Displaying all projects with valid coordinates.")

# Center the map around Menlo Park, CA
# Using the mean of the available Menlo Park coordinates for a more accurate center
if not df.empty:
    map_center = [df['latitude'].mean(), df['longitude'].mean()]
else:
    # Fallback to a default Menlo Park center if no valid data points
    map_center = [37.45398, -122.184425] # Kepler's Plaza, Menlo Park

# Create a Folium map object
map_height = 800  # Set the height of the map
m = folium.Map(location=map_center, zoom_start=13, height=map_height, control_scale=True)

# Create a MarkerCluster object
marker_cluster = MarkerCluster().add_to(m) # <--- Create the cluster layer

# Add markers for each location -> TO THE CLUSTER 2025-09-10
for idx, row in df.iterrows():
    project_name = row.get('project', 'N/A')
    project_description = row.get('description', 'No description available.')
    street_address = row.get('address', 'N/A')
    public_url = row.get('url')
    earliest_date = row.get('earliest_mention_date', 'N/A') # Get earliest date
    latest_date = row.get('latest_mention_date', 'N/A')   # Get latest date

    # Handle missing URL gracefully
    url_link = ""
    if pd.notna(public_url) and public_url.strip() != '' and public_url.strip().lower() != 'n/a':
        # Ensure URL starts with http:// or https:// for proper linking
        if not public_url.startswith(('http://', 'https://')):
            public_url = 'https://' + public_url # Prepend https if missing
        url_link = f"<br><a href='{public_url}' target='_blank'>More Information</a>"
    else:
        url_link = "<br>No public URL available."

    # Format dates for display, handling potential NaN or 'N/A'
    formatted_earliest_date = str(earliest_date) if pd.notna(earliest_date) and str(earliest_date).strip().lower() != 'n/a' else 'N/A'
    formatted_latest_date = str(latest_date) if pd.notna(latest_date) and str(latest_date).strip().lower() != 'n/a' else 'N/A'

    # Construct the tooltip text with detailed information and the URL link
    # [DEPRECATED] <b>Description:</b> {project_description}<br>
    # [DEPRECATED] {url_link}
    tooltip_html = f"""
    <h4>{project_name}</h4>
    <b>Address:</b> {street_address}<br>
    <b>Earliest Mention:</b> {formatted_earliest_date}<br>
    <b>Latest Mention:</b> {formatted_latest_date}<br>
    <b>Coordinates:</b> ({row['latitude']:.4f}, {row['longitude']:.4f})<br>
    <p><small>Click for more info</small></p>
    """

    # Construct the popup text (appears on click)
    popup_html = f"""
    <b>{project_name}</b><br>
    {project_description}<br>
    <b>Earliest Mention:</b> {formatted_earliest_date}<br>
    <b>Latest Mention:</b> {formatted_latest_date}<br>
    {url_link.replace('<br>', '')}
    """

    # Add a marker with the tooltip and popup
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        tooltip=folium.Tooltip(tooltip_html, sticky=True, max_width=400),
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color='green', icon='info-sign') # Changed icon color and type for San Carlos projects
    ).add_to(marker_cluster) # <-- 2025-09-10 Change this from .add_to(m)

# Display the map in Streamlit
# Add st.container and key to st_folium to control rendering
# --- DEPRECATED 8/1/2025 to eliminate empty space bug ---
# --- RESTORED 8/7/2025 to see if folium v 0.25.1 fixes empty space bug
with st.container():
     st_data = st_folium(m, width=900, height=600, key="menlo_park_map")

# --- DEPRECATED 8/1/2025 to simplify functionality of app ---
# st.subheader("Selected Project (on click):")
# if st_data and st_data.get("last_object_clicked_popup"):
#     # Extract the project name from the popup HTML for display
#     clicked_popup_content = st_data['last_object_clicked_popup']
#     # A simple way to get the bolded project name from the popup HTML
#     import re
#     match = re.search(r'<b>(.*?)</b>', clicked_popup_content)
#     if match:
#         st.info(f"You clicked on: {match.group(1)}")
#     else:
#         st.info(f"You clicked on: {clicked_popup_content.split('<br>')[0]}")
# else:
#     st.write("Click on a marker to see its project name here.")

# DEPRECATED 8/7/2025 to try streamlit_folium v. 0.25.1
# # --- RENDER MAP USING st.components.v1.html ---
# # This is a workaround to avoid the empty space issue at the bottom of the map
# # Get raw HTML from the Folium map
# map_html = m._repr_html_()
# # Render the map HTML with st.components.v1.html
# components.html(map_html, height=map_height + 2)

# Instructions to use interactive map
if st.checkbox("Show instructions for interactive map"):
    st.markdown("""
    #### Map Usage Note: 
    - **Hover** over a pin to see its `tooltip` information.
    - **Click** on a pin to see `popup` with more details, including a public URL link when available.
    - Rows with missing Latitude or Longitude values are automatically excluded from the map.
    - If a Public URL or Date information is missing or 'N/A', the relevant field will indicate that.
    - [CLICK HERE FOR DETAILS on each project](#project-details)        
    """)



# Feedback on interactive map feature
submit_feedback_widget("project_map")

# COMMISSIONER STANCES AND POSITIONS
# Commissioners policy stances data frame
stances_df = pd.read_csv('mpcc_stances_2025-09-08.csv')

# --- Add this CSS style block to force text color to black ---
st.markdown("""
<style>
    .stDataFrame .css-1qf2o1z p {
        color: #333333 !important; /* A dark gray is often easier on the eyes than pure black */
    }
</style>
""", unsafe_allow_html=True)
# --- End of CSS block ---

# Commissioner Stances Overview
st.subheader("Stances Overview", anchor="commissioner-stances-heatgrid")
st.markdown("[CLICK HERE for Council Members' Specific Stances](#commissioner-specific-positions)")

# Detect current theme: "light" or "dark"
theme_type = st.context.theme.type

# display stances columns using st.dataframe for horizontal scrolling
stances_summary_df = stances_df.drop(columns=['Key Positions'])
# add color-coding on stances (pro, neutral, opposed or mixed)

# DEPRECATED v1 palette
# def highlight_stances(val):
#     color= 'white'
#     if val == 'Pro':
#         color = '#70FA97'
#     elif val == 'Mixed':
#         color = '#B1EAF0'
#     elif val == 'Neutral':
#         color = '#E5FAA0'
#     elif val == 'Opposed':
#         color = '#FFDC78'
#     return f'background-color: {color}'

# v2 palette per ChatGPT suggestions 2025-08-20

# def highlight_stances(val):
#     color= 'white'
#     if val == 'Pro':
#         color = '#D5F5E3'
#     elif val == 'Mixed':
#         color = '#F9E79F'
#     elif val == 'Neutral':
#         color = '#D6EAF8'
#     elif val == 'Opposed':
#         color = '#FAD7A0'
#     return f'background-color: {color}'

# Enable responsive highlight colors for light or dark screen mode.

def highlight_stances(val):
    if theme_type == "dark":
        if val == 'Pro':
            return 'background-color: #27AE60; color: white;'   # darker green
        elif val == 'Mixed':
            return 'background-color: #B7950B; color: white;'   # olive
        elif val == 'Neutral':
            return 'background-color: #2874A6; color: white;'   # medium blue
        elif val == 'Opposed':
            return 'background-color: #CA6F1E; color: white;'   # dark orange
    else:  # light mode
        if val == 'Pro':
            return 'background-color: #D5F5E3; color: black;'   # pastel green
        elif val == 'Mixed':
            return 'background-color: #F9E79F; color: black;'   # pastel yellow
        elif val == 'Neutral':
            return 'background-color: #D6EAF8; color: black;'   # pastel blue
        elif val == 'Opposed':
            return 'background-color: #FAD7A0; color: black;'   # pastel orange
    return ''

styled_stances_df = stances_summary_df.style.applymap(highlight_stances)
st.dataframe(styled_stances_df)

# Feedback on council member stances feature
submit_feedback_widget("stances_overview")

# MEETING HIGHLIGHTS
# BAR CHART WITH Meeting Highlights for 1H 2025
st.subheader("Meeting Highlights", anchor="meeting-highlights")

chart_df = pd.read_csv('mpcc_topics_2025-09-06_v2_with_youtube_links.csv')
chart_df["Date"] = pd.to_datetime(chart_df["Date"]).dt.strftime('%Y-%m-%d')
chart_df["Duration (min)"] = pd.to_numeric(chart_df["Length_Minutes"], errors='coerce')
chart_df["Topic Count"] = chart_df["Topic_Count"]
chart_df["Topics"] = chart_df["Major_Topics"]
chart_df["Youtube link"] = chart_df["youtube-link"]

# DEPRECATED simple streamlit bar chart since this does not support clickable link
# # basic streamlit bar_chart
# st.bar_chart(chart_df, x="date", y="duration", use_container_width=True) 

# ADDED enhanced altair interactive chart
mtg_chart = alt.Chart(chart_df).mark_bar().encode(
    x='Date',
    y= 'Duration (min)',
    color=alt.value('#A9CCE3'),
    # href='youtube-link',  DEPRECATED for ux reasons
    tooltip=['Date', 'Duration (min)', 'Topic Count', 'Major_Topics'] # removed "'Youtube link' from list"
).properties(title="Rollover any bar for meeting highlights by date")

st.altair_chart(mtg_chart, use_container_width=True)

st.markdown("[CLICK HERE for Meeting Details](#meeting-details)")



# DEPRECATED 8/8/2025
# Somewhat redundant with explainer video. Also a bug in the audio file prevents playback
# # Podcast player
# st.subheader("Deep Dive - July 2025 Podcast")
# st.write("Your 5 minute podcast on the big themes and impacts of Menlo Park planning commission actions in 1H 2025")
# try:
#     with open("MPPC_podcast_source.m4a", "rb") as audio_file:
#         audio_bytes = audio_file.read()
#     st.audio(audio_bytes, format="audio/m4a")
# except FileNotFoundError:
#     st.error("Error: The audio file 'MPPC_podcast_source.m4a' was not found. Please ensure the file is in the correct directory.")  

# INFORMATION TABLES WITH MORE DETAILS ON TOPICS, PROJECTS AND COMMISSIONERS

# Key Projects table
st.subheader("Project Details", anchor="project-details")

#columns_to_show = ['Project', 'Address', 'Description', 'First Mention', 'Last Mention']
# columns_to_show = ['project', 'address', 'description', 'earliest_mention_date', 'latest_mention_date', 'url'] #need to remove url column for now 9/2/2025.
columns_to_show = ['project', 'address', 'description', 'earliest_mention_date', 'latest_mention_date']

# st.dataframe(df) # DEPRECATED 2025-08-16
# use st.table instead, to show multi-row description field
if st.checkbox("Show Project Details"):
    st.table(df[columns_to_show])

st.markdown("[RETURN to Project Map](#project-map)")

# COMMISSIONER SPECIFIC POSITIONS
# display subset of columns using st.table for bulleted list in cells
st.subheader("Stances Details", anchor="commissioner-specific-positions")

positions_view = ['Council Member', 'Key Positions']
positions_list_df = stances_df[positions_view]

if st.checkbox("Show Key Stances of each Council Member"):
    st.table(positions_list_df)

st.markdown("[RETURN to Council Member Stances overview](#commissioner-stances-heatgrid)")

# Meeting Details table
st.subheader("Meeting Details", anchor="meeting-details")

# List of columns you want to display
selected_columns = ['Date', 'Topics', 'Youtube link']
# Create a new DataFrame with only the selected columns
df_to_display = chart_df[selected_columns]

# DEPRECATED 2025-08-16
# st.dataframe(df_to_display) 
# use st.table instead, to render markdown in table cells

if st.checkbox("Show Meeting Details"):
    st.table(df_to_display)

st.markdown("[RETURN to Meeting Highlights Chart](#meeting-highlights)")

# DEPRECATED - replaced by above 2 separate tables
# display all columns using st.dataframe for horizontal scrolling
# st.dataframe(stances_df)

# # Planning Commission detailed activity highlights
# DEPRECATED tbd if useful to retain a long-form bullet point narrative summary
# st.subheader("Fine Print")
# st.write("Click the checkbox to dig deeper.")       
# # Get markdown content for the Planning Commission highlights
# def read_markdown_file(file_path):
#     """Reads the content of a markdown file."""
#     with open(file_path, "r", encoding="utf-8") as file:
#         return file.read()

# markdown_content = read_markdown_file("SCPT_1H2025_Milestones.md")

# # Display the markdown content in Streamlit, with user control to show/hide
# if st.checkbox("See Planning Commission 1H 2025 Activity Details"):
#     st.markdown(markdown_content)

# General Feedback
st.divider()
st.subheader("Please share your feedback")
submit_feedback_widget("overall_experience")
