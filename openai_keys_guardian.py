import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List

# Set page configuration
st.set_page_config(
    page_title="OpenAI Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
st.markdown("""
<style>
    /* Main elements */
    .main-header {
        font-size: 2.5rem;
        color: #0f52ba;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
        padding-top: 1rem;
    }
    .sub-header {
        font-size: 1.6rem;
        color: #1e88e5;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }

    /* Custom cards */
    .dashboard-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        border-left: 5px solid #1e88e5;
    }
    .dashboard-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
        border-top: 4px solid #1e88e5;
    }
    .api-key-card {
        background-color: #f0f7ff;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        border-left: 4px solid #2196f3;
        transition: background-color 0.2s;
    }
    .api-key-card:hover {
        background-color: #e3f2fd;
    }

    /* Status indicators */
    .warning { color: #ff5252; font-weight: bold; }
    .success { color: #4caf50; font-weight: bold; }
    .info { color: #2196f3; font-weight: bold; }

    /* Other elements */
    .key-info {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    .key-label {
        color: #5f6368;
        font-size: 0.9rem;
    }
    .key-value {
        font-weight: 500;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
        color: #5f6368;
        font-size: 0.9rem;
        border-top: 1px solid #e0e0e0;
    }
    .help-text {
        font-size: 0.85rem;
        color: #5f6368;
        font-style: italic;
        margin-top: 0.3rem;
    }

    /* Sidebar customization */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    [data-testid="stSidebar"] {
        background-color: #f0f7ff!important;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: background-color 0.3s, transform 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
    }
    .primary-btn {
        background-color: #1e88e5;
        color: white;
    }

    /* Charts container */
    .chart-container {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-active {
        background-color: #e3f8e9;
        color: #4caf50;
    }
    .status-revoked {
        background-color: #ffe8e8;
        color: #ff5252;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        border-radius: 6px 6px 0 0;
        padding: 0 1rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e3f2fd !important;
        color: #1e88e5 !important;
    }

    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced sidebar with better organization and help text
with st.sidebar:
    st.markdown("# 🛡️ OpenAI Guardian")
    st.markdown("---")

    # API Key input with improved styling and help
    st.markdown("### API Authentication")

    # Add help text for API key
    st.markdown("""
    <div class="help-text">
        Enter your OpenAI Admin API Key to access your projects and usage data.
    </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input("OpenAI Admin API Key", type="password",
                           help="Your OpenAI Admin API Key with organization-wide access")

    show_key = st.checkbox("Show API Key", help="Toggle visibility of your API key")
    if show_key and api_key:
        st.code(api_key, language="text")
    elif show_key:
        st.caption("No API key entered")

    st.markdown("---")

    # Improved date selection
    st.markdown("### 📅 Date Range")

    # Quick date range selector with better organization
    st.markdown("""
    <div class="help-text">
        Select a predefined date range or customize your own
    </div>
    """, unsafe_allow_html=True)

    date_range_options = {
        "Last 7 days": 7,
        "Last 30 days": 30,
        "Last 90 days": 90,
        "Last 180 days": 180,
        "Last 365 days": 365
    }

    selected_range = st.selectbox(
        "Quick select",
        options=list(date_range_options.keys()),
        index=1  # Default to 30 days
    )

    # Initialize session state if needed
    if 'start_date' not in st.session_state:
        st.session_state.start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    if 'end_date' not in st.session_state:
        st.session_state.end_date = datetime.now().strftime('%Y-%m-%d')

    # Apply button with better styling
    if st.button("Apply Range", use_container_width=True):
        days = date_range_options[selected_range]
        st.session_state.start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        st.session_state.end_date = datetime.now().strftime('%Y-%m-%d')
        st.rerun()

    # Custom date range with better organization
    st.markdown("#### Custom Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start",
            value=datetime.strptime(st.session_state.start_date, '%Y-%m-%d'),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "End",
            value=datetime.strptime(st.session_state.end_date, '%Y-%m-%d'),
            max_value=datetime.now()
        )

    # Update session state with selected dates
    st.session_state.start_date = start_date.strftime('%Y-%m-%d')
    st.session_state.end_date = end_date.strftime('%Y-%m-%d')

    # Add a note about the date range
    if (end_date - start_date).days > 90:
        st.markdown("""
        <div class="warning">
            Large date ranges may take longer to process.
        </div>
        """, unsafe_allow_html=True)

    # Refresh button with better styling
    st.markdown("---")
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.session_state.refresh_counter = st.session_state.get('refresh_counter', 0) + 1
        st.rerun()

    # About section with more detailed information
    st.markdown("---")
    st.markdown("### About OpenAI Guardian")
    st.markdown("""
    Monitor and optimize your OpenAI API usage:

    - 📊 Track API usage across projects
    - 💰 Monitor costs and spending
    - 🔑 Manage API keys securely
    - 📈 Analyze usage trends over time

    <div class="help-text">
        v1.2.0 - For help, contact support@example.com
    </div>
    """, unsafe_allow_html=True)

# Initialize session state for storing project data
if 'projects' not in st.session_state:
    st.session_state.projects = []
    st.session_state.project_ids_map = {}
    st.session_state.selected_project_id = None
    st.session_state.api_keys = []
    st.session_state.usage_data = {}

# Improved API interaction functions
@st.cache_data(ttl=300)
def make_api_request(url: str, api_key: str, params: Dict = None) -> Dict:
    """Generic function to make API requests to OpenAI"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params or {})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # More detailed error handling
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            if status_code == 401:
                st.error("Authentication error: Invalid API key or insufficient permissions")
            elif status_code == 403:
                st.error("Authorization error: Your API key doesn't have access to this resource")
            elif status_code == 404:
                st.error("Resource not found: The requested endpoint doesn't exist")
            elif status_code == 429:
                st.error("Rate limit exceeded: Too many requests, please try again later")
            elif status_code >= 500:
                st.error("OpenAI server error: Please try again later")
            else:
                st.error(f"API Error ({status_code}): {str(e)}")
        else:
            st.error(f"Connection Error: {str(e)}")
        return {"data": []}

@st.cache_data(ttl=300)
def fetch_projects(api_key: str) -> List[Dict]:
    """Fetch all projects from the OpenAI API."""
    url = "https://api.openai.com/v1/organization/projects"
    params = {"limit": 100, "include_archived": False}
    response = make_api_request(url, api_key, params)
    return response.get('data', [])

@st.cache_data(ttl=300)
def fetch_project_api_keys(api_key: str, project_id: str) -> List[Dict]:
    """Fetch API keys for a specific project."""
    url = f"https://api.openai.com/v1/organization/projects/{project_id}/api_keys"
    response = make_api_request(url, api_key, {"limit": 100})
    return response.get('data', [])

@st.cache_data(ttl=300)
def fetch_usage_data(api_key: str, project_id: str, start_date: str, end_date: str) -> Dict:
    """Fetch usage data for a project."""
    url = "https://api.openai.com/v1/organization/usage/completions"

    # Convert dates to timestamps
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) + 86400  # Add one day

    params = {
        "start_time": start_timestamp,
        "end_time": end_timestamp,
        "project_ids": [project_id],
        "bucket_width": "1d",
        "limit": 31,
        "group_by": ["project_id", "model"]
    }

    return make_api_request(url, api_key, params)

@st.cache_data(ttl=300)
def fetch_costs_data(api_key: str, project_id: str, start_date: str, end_date: str) -> Dict:
    """Fetch cost data for a project."""
    url = "https://api.openai.com/v1/organization/costs"

    # Convert dates to timestamps
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) + 86400  # Add one day

    params = {
        "start_time": start_timestamp,
        "end_time": end_timestamp,
        "project_ids": [project_id],
        "bucket_width": "1d",
        "limit": 180,  # Maximum allowed to get all data
        "group_by": ["project_id", "line_item"]
    }

    return make_api_request(url, api_key, params)

@st.cache_data(ttl=300)
def fetch_api_key_usage(api_key: str, project_id: str, api_key_ids: List[str], start_date: str, end_date: str) -> Dict:
    """Fetch usage data for specific API keys."""
    url = "https://api.openai.com/v1/organization/usage/completions"

    # Convert dates to timestamps
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) + 86400  # Add one day

    params = {
        "start_time": start_timestamp,
        "end_time": end_timestamp,
        "project_ids": [project_id],
        "api_key_ids": api_key_ids,
        "bucket_width": "1d",
        "limit": 31,
        "group_by": ["api_key_id"]
    }

    return make_api_request(url, api_key, params)

def revoke_api_key(api_key: str, project_id: str, key_id: str) -> bool:
    """Revoke an API key with improved error handling."""
    url = f"https://api.openai.com/v1/organization/projects/{project_id}/api_keys/{key_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            if status_code == 401:
                st.error("Authentication error: Invalid API key")
            elif status_code == 403:
                st.error("Authorization error: You don't have permission to revoke this key")
            else:
                st.error(f"Error revoking key: {str(e)}")
        else:
            st.error(f"Connection error: {str(e)}")
        return False

# Enhanced data processing functions
def estimate_cost(usage_data: Dict) -> Dict:
    """Estimate cost based on usage data and model pricing with improved structure."""
    # Pricing model with latest rates
    pricing = {
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4o': {'input': 0.005, 'output': 0.015},
        'default': {'input': 0.01, 'output': 0.02}
    }

    costs = {'daily': {}, 'total': 0, 'models': {}}

    # Check if we have the expected data structure
    if 'data' in usage_data and isinstance(usage_data['data'], list):
        # Process data buckets
        buckets = usage_data.get('data', [])

        for bucket in buckets:
            date = bucket.get('start_time', 0)
            date_str = datetime.fromtimestamp(date).strftime('%Y-%m-%d')

            # Initialize daily cost for this date if not exists
            if date_str not in costs['daily']:
                costs['daily'][date_str] = 0

            # Process results in this bucket
            for result in bucket.get('results', []):
                model = result.get('model', 'default')
                model_pricing = pricing.get(model, pricing['default'])

                input_tokens = result.get('input_tokens', 0)
                output_tokens = result.get('output_tokens', 0)

                # Calculate costs
                input_cost = (input_tokens / 1000) * model_pricing['input']
                output_cost = (output_tokens / 1000) * model_pricing['output']
                total_cost = input_cost + output_cost

                # Update costs
                if model not in costs['models']:
                    costs['models'][model] = 0

                costs['daily'][date_str] += total_cost
                costs['total'] += total_cost
                costs['models'][model] += total_cost

    # Ensure all dates in range are included even with zero values
    start_date = datetime.strptime(st.session_state.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(st.session_state.end_date, '%Y-%m-%d')
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        if date_str not in costs['daily']:
            costs['daily'][date_str] = 0
        current_date += timedelta(days=1)

    # Sort the daily costs by date
    costs['daily'] = dict(sorted(costs['daily'].items()))

    return costs

def process_costs_data(costs_data: Dict) -> Dict:
    """Process the cost data from the API with enhanced error handling."""
    processed_costs = {'daily': {}, 'total': 0, 'line_items': {}}

    # Check if we have the expected data structure
    if 'data' in costs_data and isinstance(costs_data['data'], list):
        # Process data buckets
        buckets = costs_data.get('data', [])

        for bucket in buckets:
            date = bucket.get('start_time', 0)
            date_str = datetime.fromtimestamp(date).strftime('%Y-%m-%d')

            # Initialize daily cost for this date if not exists
            if date_str not in processed_costs['daily']:
                processed_costs['daily'][date_str] = 0

            # Process results in this bucket
            for result in bucket.get('results', []):
                if not isinstance(result, dict):
                    continue

                # Get line item (could be under different keys)
                line_item = result.get('line_item', result.get('model', 'Unknown'))

                # Get cost (could be under different keys)
                cost = result.get('cost', result.get('amount', 0))

                # Handle case where cost is a dictionary
                if isinstance(cost, dict):
                    # Try to extract a numeric value from the dictionary
                    if 'amount' in cost:
                        cost = cost.get('amount', 0)
                    elif 'value' in cost:
                        cost = cost.get('value', 0)
                    else:
                        cost = 0

                # Try to convert to float if it's a string
                if isinstance(cost, str):
                    try:
                        cost = float(cost)
                    except ValueError:
                        cost = 0

                # Ensure cost is a number
                if not isinstance(cost, (int, float)):
                    cost = 0

                # Update costs
                if line_item not in processed_costs['line_items']:
                    processed_costs['line_items'][line_item] = 0

                processed_costs['daily'][date_str] += cost
                processed_costs['total'] += cost
                processed_costs['line_items'][line_item] += cost

    # Ensure all dates in range are included even with zero values
    start_date = datetime.strptime(st.session_state.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(st.session_state.end_date, '%Y-%m-%d')
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        if date_str not in processed_costs['daily']:
            processed_costs['daily'][date_str] = 0
        current_date += timedelta(days=1)

    # Sort the daily costs by date
    processed_costs['daily'] = dict(sorted(processed_costs['daily'].items()))

    return processed_costs

def process_api_key_usage(api_key_usage: Dict, api_keys: List[Dict]) -> Dict:
    """Process the API key usage data with improved structure."""
    # Create a mapping of API key IDs to names
    key_id_to_name = {key.get('id'): key.get('name', 'Unnamed Key') for key in api_keys if key.get('id')}

    # Initialize the processed data structure
    processed_data = {'daily': {}, 'keys': {}}

    # Check if we have the expected data structure
    if 'data' in api_key_usage and isinstance(api_key_usage['data'], list):
        # Process data buckets
        buckets = api_key_usage.get('data', [])

        for bucket in buckets:
            date = bucket.get('start_time', 0)
            date_str = datetime.fromtimestamp(date).strftime('%Y-%m-%d')

            # Process results in this bucket
            for result in bucket.get('results', []):
                key_id = result.get('api_key_id')
                requests = result.get('num_model_requests', 0)

                if key_id:
                    key_name = key_id_to_name.get(key_id, f"Key {key_id[:8]}...")

                    # Initialize data structures if needed
                    if key_name not in processed_data['keys']:
                        processed_data['keys'][key_name] = {'daily': {}, 'total': 0}

                    if date_str not in processed_data['keys'][key_name]['daily']:
                        processed_data['keys'][key_name]['daily'][date_str] = 0

                    # Update the data
                    processed_data['keys'][key_name]['daily'][date_str] += requests
                    processed_data['keys'][key_name]['total'] += requests

    # Ensure all keys have data for all dates in range
    start_date = datetime.strptime(st.session_state.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(st.session_state.end_date, '%Y-%m-%d')

    all_dates = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        all_dates.append(date_str)
        current_date += timedelta(days=1)

    # Fill in missing dates for each key
    for key_name in processed_data['keys']:
        for date_str in all_dates:
            if date_str not in processed_data['keys'][key_name]['daily']:
                processed_data['keys'][key_name]['daily'][date_str] = 0

    return processed_data

@st.cache_data(ttl=300)
def fetch_project_rate_limits(api_key: str, project_id: str) -> List[Dict]:
    """Fetch rate limits for a specific project."""
    url = f"https://api.openai.com/v1/organization/projects/{project_id}/rate_limits"
    response = make_api_request(url, api_key, {"limit": 100})
    return response.get('data', [])

# Enhanced header with animation
st.markdown("<h1 class='main-header'>🛡️ OpenAI Guardian</h1>", unsafe_allow_html=True)

# Display enhanced Project Management section if API key is provided
if api_key:
    # Improved project selection UI
    st.markdown("""
    <div class="dashboard-card">
        <h2>Project Selection</h2>
        <p>Select a project to analyze and manage its API usage and costs</p>
    </div>
    """, unsafe_allow_html=True)

    # Project fetch and selection UI
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔍 Fetch Projects", use_container_width=True):
            with st.spinner("Fetching your projects..."):
                projects = fetch_projects(api_key)

                if projects:
                    # Create a mapping of project names to IDs
                    project_names = []
                    project_ids_map = {}

                    for project in projects:
                        project_name = project.get('name', 'Unnamed Project')
                        project_id = project.get('id', '')

                        if project_id:
                            project_names.append(project_name)
                            project_ids_map[project_name] = project_id

                    st.session_state.projects = project_names
                    st.session_state.project_ids_map = project_ids_map
                    st.success(f"✅ Found {len(projects)} projects")
                else:
                    st.error("❌ No projects found. Check your API key and permissions.")

    # Project selection dropdown with improved UX
    with col2:
        if st.session_state.projects:
            selected_project_name = st.selectbox(
                "Select a project to analyze",
                options=st.session_state.projects,
                help="Choose the project you want to view data for"
            )

            # Show project ID below selection
            if selected_project_name in st.session_state.project_ids_map:
                st.session_state.selected_project_id = st.session_state.project_ids_map[selected_project_name]
                st.caption(f"Project ID: `{st.session_state.selected_project_id}`")

                # Load button with improved styling
                if st.button("📊 Load Dashboard Data", use_container_width=True):
                    # Add progress indicators
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Step 1: Fetch API keys
                    status_text.text("Fetching API keys...")
                    api_keys = fetch_project_api_keys(api_key, st.session_state.selected_project_id)
                    st.session_state.api_keys = api_keys
                    progress_bar.progress(25)

                    # Step 2: Fetch usage data
                    status_text.text("Fetching usage data...")
                    usage_data = fetch_usage_data(
                        api_key,
                        st.session_state.selected_project_id,
                        st.session_state.start_date,
                        st.session_state.end_date
                    )
                    st.session_state.usage_data = usage_data
                    progress_bar.progress(50)

                    # Step 3: Fetch cost data
                    status_text.text("Fetching cost data...")
                    costs_data = fetch_costs_data(
                        api_key,
                        st.session_state.selected_project_id,
                        st.session_state.start_date,
                        st.session_state.end_date
                    )
                    st.session_state.costs_data = costs_data
                    progress_bar.progress(75)

                    # Step 4: Fetch API key usage data
                    status_text.text("Fetching API key usage data...")
                    if api_keys:
                        api_key_ids = [key.get('id') for key in api_keys if key.get('id')]
                        if api_key_ids:
                            api_key_usage = fetch_api_key_usage(
                                api_key,
                                st.session_state.selected_project_id,
                                api_key_ids,
                                st.session_state.start_date,
                                st.session_state.end_date
                            )
                            st.session_state.api_key_usage = api_key_usage

                    # Complete the progress
                    progress_bar.progress(100)
                    status_text.empty()

                    # Show success message with animation
                    st.success("✅ Dashboard data loaded successfully!")
                    st.balloons()  # Add a fun animation for successful load

    # Display enhanced dashboard if project is selected
    if st.session_state.get('selected_project_id'):
        # Get the selected project name
        selected_project_name = next((name for name, id in st.session_state.project_ids_map.items()
                                    if id == st.session_state.selected_project_id), "Selected Project")

        # Create dashboard header with project info
        st.markdown(f"""
        <div class="dashboard-card">
            <h2>Project Dashboard: {selected_project_name}</h2>
            <p>View and analyze usage metrics, costs, and API keys for this project</p>
            <div class="help-text">Date range: {st.session_state.start_date} to {st.session_state.end_date}</div>
        </div>
        """, unsafe_allow_html=True)

        # Create tabs with better styling and organization
        tab1, tab2, tab3 = st.tabs(["📊 Usage Overview", "💰 Cost Analysis", "🔑 API Key Management"])

        with tab1:
            # Quick metrics in cards with improved styling
            st.markdown("### Dashboard Overview")

            # Calculate metrics
            api_keys = st.session_state.get('api_keys', [])
            active_keys = len([k for k in api_keys if k.get('id') not in st.session_state.get('deleted_keys', set())])
            date_range = (datetime.strptime(st.session_state.end_date, '%Y-%m-%d') -
                          datetime.strptime(st.session_state.start_date, '%Y-%m-%d')).days + 1

            # Get actual costs if available
            costs_data = st.session_state.get('costs_data', {})
            if costs_data:
                processed_costs = process_costs_data(costs_data)
                actual_total_cost = processed_costs.get('total', 0)
            else:
                processed_costs = {'daily': {}, 'total': 0, 'line_items': {}}
                actual_total_cost = 0

            # Get usage data if available
            usage_data = st.session_state.get('usage_data', {})
            total_requests = 0

            if usage_data and 'data' in usage_data:
                for bucket in usage_data.get('data', []):
                    for result in bucket.get('results', []):
                        total_requests += result.get('num_model_requests', 0)

            # Display metrics in a nice grid
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h4>Active API Keys</h4>
                    <h2 style="color: #1e88e5;">{}</h2>
                    <div class="help-text">Total keys in project</div>
                </div>
                """.format(active_keys), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h4>Total Cost</h4>
                    <h2 style="color: #4caf50;">${:.2f}</h2>
                    <div class="help-text">For selected period</div>
                </div>
                """.format(actual_total_cost), unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h4>API Requests</h4>
                    <h2 style="color: #ff9800;">{:,}</h2>
                    <div class="help-text">Total API calls</div>
                </div>
                """.format(total_requests), unsafe_allow_html=True)

            with col4:
                st.markdown("""
                <div class="metric-card">
                    <h4>Date Range</h4>
                    <h2 style="color: #9c27b0;">{}</h2>
                    <div class="help-text">Days of data</div>
                </div>
                """.format(date_range), unsafe_allow_html=True)

            # Usage trends
            st.markdown("### Usage Trends")

            if usage_data and 'data' in usage_data:
                # Process usage data
                usage_by_date = {}
                usage_by_model = {}

                for bucket in usage_data.get('data', []):
                    date = bucket.get('start_time', 0)
                    date_str = datetime.fromtimestamp(date).strftime('%Y-%m-%d')

                    if date_str not in usage_by_date:
                        usage_by_date[date_str] = 0

                    for result in bucket.get('results', []):
                        model = result.get('model', 'Unknown')
                        requests = result.get('num_model_requests', 0)

                        if model not in usage_by_model:
                            usage_by_model[model] = 0

                        usage_by_date[date_str] += requests
                        usage_by_model[model] += requests

                # Create usage trend chart
                if usage_by_date:
                    usage_trend_data = []
                    for date, requests in sorted(usage_by_date.items()):
                        usage_trend_data.append({
                            'Date': date,
                            'Requests': requests
                        })

                    df_usage_trend = pd.DataFrame(usage_trend_data)

                    # Check if there's any actual usage data
                    has_usage_data = any(item['Requests'] > 0 for item in usage_trend_data)

                    if has_usage_data:
                        # Create chart with custom styling
                        fig_usage = px.line(
                            df_usage_trend,
                            x='Date',
                            y='Requests',
                            title='Daily API Requests',
                            markers=True
                        )

                        # Enhance the chart styling
                        fig_usage.update_traces(
                            line=dict(width=3, color='#1e88e5'),
                            marker=dict(size=8, color='#1e88e5')
                        )
                        fig_usage.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            margin=dict(t=50, b=50, l=20, r=20),
                            xaxis=dict(
                                title_font=dict(size=14),
                                tickfont=dict(size=12),
                                gridcolor='#f5f5f5'
                            ),
                            yaxis=dict(
                                title='Number of Requests',
                                title_font=dict(size=14),
                                tickfont=dict(size=12),
                                gridcolor='#f5f5f5'
                            ),
                            hoverlabel=dict(
                                bgcolor="white",
                                font_size=14,
                                font_family="Arial"
                            )
                        )

                        st.plotly_chart(fig_usage, use_container_width=True)

                        # Model distribution chart
                        if usage_by_model:
                            st.markdown("### Model Distribution")

                            model_data = []
                            for model, requests in usage_by_model.items():
                                if requests > 0:  # Only include models with usage
                                    model_data.append({
                                        'Model': model,
                                        'Requests': requests
                                    })

                            if model_data:
                                df_models = pd.DataFrame(model_data)

                                # Create donut chart
                                fig_models = px.pie(
                                    df_models,
                                    values='Requests',
                                    names='Model',
                                    title='API Requests by Model',
                                    hole=0.5,
                                    color_discrete_sequence=px.colors.qualitative.Set2
                                )

                                # Customize chart
                                fig_models.update_layout(
                                    legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=-0.2,
                                        xanchor="center",
                                        x=0.5
                                    ),
                                    margin=dict(t=60, b=100, l=20, r=20)
                                )

                                # Add text in center of donut
                                fig_models.add_annotation(
                                    text=f"{sum(df_models['Requests']):,}",
                                    x=0.5, y=0.5,
                                    font_size=20,
                                    showarrow=False
                                )
                                fig_models.add_annotation(
                                    text="Total Requests",
                                    x=0.5, y=0.42,
                                    font_size=12,
                                    showarrow=False
                                )

                                st.plotly_chart(fig_models, use_container_width=True)
                    else:
                        st.info("📊 No usage data available for the selected date range.")
                else:
                    st.info("📊 No usage data available for the selected date range.")
            else:
                st.info("📈 Usage data not loaded yet. Click 'Load Dashboard Data' to fetch usage information.")

        with tab2:
            # Cost Analysis section with enhanced visualizations
            st.markdown("### Cost Analysis")

            if costs_data:
                # Process cost data
                processed_costs = process_costs_data(costs_data)

                # Quick cost metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    daily_avg = processed_costs['total'] / max(len(processed_costs['daily']), 1)
                    st.markdown("""
                    <div class="metric-card">
                        <h4>Total Cost</h4>
                        <h2 style="color: #4caf50;">${:.2f}</h2>
                    </div>
                    """.format(processed_costs['total']), unsafe_allow_html=True)

                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <h4>Daily Average</h4>
                        <h2 style="color: #1e88e5;">${:.2f}</h2>
                    </div>
                    """.format(daily_avg), unsafe_allow_html=True)

                with col3:
                    # Find the most expensive day
                    if processed_costs['daily']:
                        max_day = max(processed_costs['daily'].items(), key=lambda x: x[1])
                        st.markdown("""
                        <div class="metric-card">
                            <h4>Peak Day</h4>
                            <h2 style="color: #ff9800;">${:.2f}</h2>
                            <div class="help-text">{}</div>
                        </div>
                        """.format(max_day[1], max_day[0]), unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="metric-card">
                            <h4>Peak Day</h4>
                            <h2 style="color: #ff9800;">$0.00</h2>
                            <div class="help-text">No data</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Daily cost chart
                daily_cost_data = []
                for date, cost in processed_costs['daily'].items():
                    daily_cost_data.append({
                        'Date': date,
                        'Cost': cost
                    })

                # Sort by date
                daily_cost_data = sorted(daily_cost_data, key=lambda x: x['Date'])

                # Create DataFrame
                df_daily_cost = pd.DataFrame(daily_cost_data)

                # Check if there's any actual cost data
                has_cost_data = any(cost > 0 for cost in processed_costs['daily'].values())

                if has_cost_data:
                    # Create combination chart - bar and line
                    fig = go.Figure()

                    # Add bar chart
                    fig.add_trace(go.Bar(
                        x=df_daily_cost['Date'],
                        y=df_daily_cost['Cost'],
                        name='Daily Cost',
                        marker_color='#1e88e5',
                        opacity=0.7
                    ))

                    # Add line for moving average
                    df_daily_cost['MA7'] = df_daily_cost['Cost'].rolling(7, min_periods=1).mean()
                    fig.add_trace(go.Scatter(
                        x=df_daily_cost['Date'],
                        y=df_daily_cost['MA7'],
                        name='7-Day Average',
                        line=dict(color='#ff5252', width=3)
                    ))

                    # Customize layout
                    fig.update_layout(
                        title='Daily Cost with 7-Day Moving Average',
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        margin=dict(t=60, b=50, l=20, r=20),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        xaxis=dict(
                            title='Date',
                            title_font=dict(size=14),
                            tickfont=dict(size=12),
                            gridcolor='#f5f5f5'
                        ),
                        yaxis=dict(
                            title='Cost (USD)',
                            title_font=dict(size=14),
                            tickfont=dict(size=12),
                            gridcolor='#f5f5f5',
                            tickprefix='$'
                        ),
                        hovermode='x unified',
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=14,
                            font_family="Arial"
                        )
                    )

                    # Add custom hover template
                    fig.update_traces(
                        hovertemplate='<b>%{x}</b><br>$%{y:.2f}<extra></extra>'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Line item breakdown
                    if processed_costs.get('line_items'):
                        st.markdown("### Cost Breakdown by Model/Type")

                        line_item_data = []
                        for item, cost in processed_costs['line_items'].items():
                            if cost > 0:  # Only include items with cost
                                line_item_data.append({
                                    'Model/Type': item,
                                    'Cost': cost
                                })

                        if line_item_data:
                            # Create DataFrame
                            df_line_items = pd.DataFrame(line_item_data)
                            df_line_items = df_line_items.sort_values(by='Cost', ascending=False)

                            # Create horizontal bar chart
                            fig_items = px.bar(
                                df_line_items,
                                x='Cost',
                                y='Model/Type',
                                title='Cost by Model/Type',
                                orientation='h',
                                color='Cost',
                                color_continuous_scale='Blues'
                            )

                            # Enhance chart
                            fig_items.update_layout(
                                plot_bgcolor='white',
                                paper_bgcolor='white',
                                margin=dict(t=60, b=50, l=20, r=20),
                                xaxis=dict(
                                    title='Cost (USD)',
                                    title_font=dict(size=14),
                                    tickfont=dict(size=12),
                                    gridcolor='#f5f5f5',
                                    tickprefix='$'
                                ),
                                yaxis=dict(
                                    title='',
                                    title_font=dict(size=14),
                                    tickfont=dict(size=12)
                                ),
                                coloraxis_showscale=False
                            )

                            # Add value labels
                            fig_items.update_traces(
                                texttemplate='$%{x:.2f}',
                                textposition='outside',
                                hovertemplate='<b>%{y}</b><br>$%{x:.2f}<extra></extra>'
                            )

                            st.plotly_chart(fig_items, use_container_width=True)

                            # Create pie chart for distribution
                            fig_pie = px.pie(
                                df_line_items,
                                values='Cost',
                                names='Model/Type',
                                title='Cost Distribution',
                                hole=0.4,
                                color_discrete_sequence=px.colors.qualitative.Set2
                            )

                            fig_pie.update_layout(
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.2,
                                    xanchor="center",
                                    x=0.5
                                ),
                                margin=dict(t=60, b=100, l=20, r=20)
                            )

                            # Add total in center
                            fig_pie.add_annotation(
                                text=f"${processed_costs['total']:.2f}",
                                x=0.5, y=0.5,
                                font_size=20,
                                showarrow=False
                            )
                            fig_pie.add_annotation(
                                text="Total Cost",
                                x=0.5, y=0.42,
                                font_size=12,
                                showarrow=False
                            )

                            # Create two-column layout
                            col1, col2 = st.columns(2)

                            with col1:
                                # Table for detailed breakdown
                                st.subheader("Detailed Breakdown")

                                # Format the table data
                                df_display = df_line_items.copy()
                                df_display['Cost'] = df_display['Cost'].apply(lambda x: f"${x:.2f}")
                                df_display['Percentage'] = df_line_items['Cost'] / processed_costs['total'] * 100
                                df_display['Percentage'] = df_display['Percentage'].apply(lambda x: f"{x:.1f}%")

                                # Display the styled table
                                st.dataframe(
                                    df_display,
                                    column_config={
                                        "Model/Type": st.column_config.TextColumn("Model/Type"),
                                        "Cost": st.column_config.TextColumn("Cost (USD)"),
                                        "Percentage": st.column_config.TextColumn("% of Total")
                                    },
                                    hide_index=True,
                                    use_container_width=True
                                )

                            with col2:
                                st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("💰 No cost data available for the selected date range.")
            else:
                st.info("💰 Cost data not loaded yet. Click 'Load Dashboard Data' to fetch cost information.")

        with tab3:
            # API Keys management with improved UI
            st.markdown("### API Keys Management")

            # Get API key usage data if available
            api_key_usage = st.session_state.get('api_key_usage', {})
            api_keys = st.session_state.get('api_keys', [])

            if api_key_usage and api_keys:
                # Process key usage
                processed_key_usage = process_api_key_usage(api_key_usage, api_keys)

                if processed_key_usage['keys']:
                    # Create API key usage summary
                    st.markdown("#### API Key Usage Summary")

                    # Prepare data for comparison
                    key_totals = []
                    for key_name, key_data in processed_key_usage['keys'].items():
                        key_totals.append({
                            'API Key': key_name,
                            'Total Requests': key_data['total']
                        })

                    # Create DataFrame
                    if key_totals:
                        df_key_totals = pd.DataFrame(key_totals)
                        df_key_totals = df_key_totals.sort_values(by='Total Requests', ascending=False)

                        # Create horizontal bar chart
                        fig_key_usage = px.bar(
                            df_key_totals,
                            x='Total Requests',
                            y='API Key',
                            title='Total Requests by API Key',
                            orientation='h',
                            color='Total Requests',
                            color_continuous_scale='Viridis'
                        )

                        # Enhance chart
                        fig_key_usage.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            margin=dict(t=60, b=50, l=20, r=20),
                            xaxis=dict(
                                title='Number of Requests',
                                title_font=dict(size=14),
                                tickfont=dict(size=12),
                                gridcolor='#f5f5f5'
                            ),
                            yaxis=dict(
                                title='',
                                title_font=dict(size=14),
                                tickfont=dict(size=12)
                            ),
                            coloraxis_showscale=False
                        )

                        # Add value labels
                        fig_key_usage.update_traces(
                            texttemplate='%{x:,}',
                            textposition='outside',
                            hovertemplate='<b>%{y}</b><br>%{x:,} requests<extra></extra>'
                        )

                        st.plotly_chart(fig_key_usage, use_container_width=True)

                    # Prepare data for daily usage line chart
                    line_data = []
                    for key_name, key_data in processed_key_usage['keys'].items():
                        for date, requests in sorted(key_data['daily'].items()):
                            line_data.append({
                                'Date': date,
                                'API Key': key_name,
                                'Requests': requests
                            })

                    if line_data:
                        # Create DataFrame
                        df_line = pd.DataFrame(line_data)

                        # Check if there's any actual usage data
                        has_usage_data = any(item['Requests'] > 0 for item in line_data)

                        if has_usage_data:
                            # Create interactive line chart
                            fig_line = px.line(
                                df_line,
                                x='Date',
                                y='Requests',
                                color='API Key',
                                title='Daily API Key Usage',
                                markers=True
                            )

                            # Enhance chart
                            fig_line.update_layout(
                                plot_bgcolor='white',
                                paper_bgcolor='white',
                                margin=dict(t=60, b=50, l=20, r=20),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                ),
                                xaxis=dict(
                                    title='Date',
                                    title_font=dict(size=14),
                                    tickfont=dict(size=12),
                                    gridcolor='#f5f5f5'
                                ),
                                yaxis=dict(
                                    title='Number of Requests',
                                    title_font=dict(size=14),
                                    tickfont=dict(size=12),
                                    gridcolor='#f5f5f5'
                                ),
                                hovermode='x unified',
                                hoverlabel=dict(
                                    bgcolor="white",
                                    font_size=14,
                                    font_family="Arial"
                                )
                            )

                            st.plotly_chart(fig_line, use_container_width=True)

            # API Keys List with enhanced UI
            st.markdown("### API Keys")

            # Get API keys (if available)
            api_keys = st.session_state.get('api_keys', [])

            if api_keys:
                # Track deleted keys
                deleted_keys = st.session_state.get('deleted_keys', set())

                # Create a filter for active/revoked keys
                key_filter = st.radio(
                    "Filter keys:",
                    ["All Keys", "Active Keys", "Revoked Keys"],
                    horizontal=True
                )

                # Count active and revoked keys
                active_count = len([k for k in api_keys if k.get('id') not in deleted_keys])
                revoked_count = len([k for k in api_keys if k.get('id') in deleted_keys])

                # Display counts
                st.markdown(f"""
                <div style="display: flex; gap: 20px; margin-bottom: 10px;">
                    <div class="status-badge status-active">Active: {active_count}</div>
                    <div class="status-badge status-revoked">Revoked: {revoked_count}</div>
                </div>
                """, unsafe_allow_html=True)

                # Filter keys based on selection
                filtered_keys = []
                if key_filter == "All Keys":
                    filtered_keys = api_keys
                elif key_filter == "Active Keys":
                    filtered_keys = [k for k in api_keys if k.get('id') not in deleted_keys]
                else:  # Revoked Keys
                    filtered_keys = [k for k in api_keys if k.get('id') in deleted_keys]

                # Display keys in enhanced cards
                for key in filtered_keys:
                    key_id = key.get('id', 'Unknown')
                    key_name = key.get('name', 'Unnamed Key')
                    key_object = key.get('object', 'Unknown')
                    key_owner = key.get('owner', 'Unknown')
                    created_at = key.get('created_at', 'Unknown')
                    last_used = key.get('last_used_at', 'Never')

                    # Check if this key has been deleted
                    is_deleted = key_id in deleted_keys

                    # Format dates if available
                    for date_field_name in ['created_at', 'last_used_at']:
                        date_value = key.get(date_field_name)

                        if date_value is None:
                            # Keep as None
                            continue

                        if date_field_name == 'created_at':
                            formatted_date = created_at
                        else:
                            formatted_date = last_used

                        # Check if it's a timestamp (integer)
                        if isinstance(date_value, int) or (isinstance(date_value, str) and date_value.isdigit()):
                            try:
                                # Convert to integer if it's a string
                                if isinstance(date_value, str):
                                    date_value = int(date_value)

                                # Convert timestamp to datetime and format
                                date_dt = datetime.fromtimestamp(date_value)
                                formatted_date = date_dt.strftime('%Y-%m-%d %H:%M:%S')

                                # Update the appropriate variable
                                if date_field_name == 'created_at':
                                    created_at = formatted_date
                                else:
                                    last_used = formatted_date
                            except:
                                # Keep original value if conversion fails
                                pass
                        # Check if it's an ISO format date string
                        elif isinstance(date_value, str) and date_value not in ['Unknown', 'Never']:
                            try:
                                date_dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                                formatted_date = date_dt.strftime('%Y-%m-%d %H:%M:%S')

                                # Update the appropriate variable
                                if date_field_name == 'created_at':
                                    created_at = formatted_date
                                else:
                                    last_used = formatted_date
                            except:
                                # Keep original value if conversion fails
                                pass

                    # Calculate days since last used
                    last_used_days = ""
                    if last_used and last_used != 'Never' and last_used != 'Unknown':
                        try:
                            last_used_date = datetime.strptime(last_used, '%Y-%m-%d %H:%M:%S')
                            days_since = (datetime.now() - last_used_date).days
                            last_used_days = f" ({days_since} days ago)"
                        except:
                            pass

                    # Create API key card with native Streamlit components
                    status = "REVOKED" if is_deleted else "ACTIVE"
                    status_color = "red" if is_deleted else "green"

                    # Create an expander for each key
                    with st.expander(f"{key_name} - {status}", expanded=False):
                        # Display key information in columns
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**ID:** {key_id}")
                            st.markdown(f"**Type:** {key_object}")
                            st.markdown(f"**Owner:** {key_owner}")

                        with col2:
                            st.markdown(f"**Created:** {created_at}")
                            st.markdown(f"**Last Used:** {last_used}{last_used_days}")

                        # Display redacted API key
                        st.text_input("Redacted API Key",
                                     value=key.get('redacted_value', 'Not available'),
                                     disabled=True)

                        # Add action buttons
                        if not is_deleted:
                            if st.button(f"Revoke {key_name}", key=f"revoke_{key_id}"):
                                with st.spinner(f"Revoking key {key_name}..."):
                                    success = revoke_api_key(api_key, st.session_state.selected_project_id, key_id)
                                    if success:
                                        # Add to deleted keys set
                                        if 'deleted_keys' not in st.session_state:
                                            st.session_state.deleted_keys = set()
                                        st.session_state.deleted_keys.add(key_id)
                                        st.success(f"✅ Key '{key_name}' revoked successfully!")
                                        st.rerun()
            else:
                # Enhanced empty state with native Streamlit components
                st.info("No API Keys Found")
                st.write("There are no API keys available for this project.")
                st.write("Click 'Load API Keys' to fetch API keys.")

                # Add a button to load data if it hasn't been loaded yet
                if not st.session_state.get('api_keys'):
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🔑 Load API Keys", use_container_width=True):
                            with st.spinner("Loading API keys..."):
                                api_keys = fetch_project_api_keys(api_key, st.session_state.selected_project_id)
                                st.session_state.api_keys = api_keys
                                st.success(f"✅ Found {len(api_keys)} API keys")
                                st.rerun()
else:
    # Enhanced welcome screen with better onboarding using native Streamlit components
    st.title("Welcome to OpenAI Guardian")
    st.write("Your comprehensive dashboard for monitoring and managing OpenAI API usage")

    # Getting Started section
    st.markdown("## Getting Started")

    # Create a blue info box
    st.info("""
    Follow these steps to get started:
    1. Enter your **OpenAI Admin API Key** in the sidebar
    2. Click **Fetch Projects** to load your projects
    3. Select a project and click **Load Dashboard Data**
    4. View your usage dashboard and manage API keys
    """)

    # Feature highlights using columns
    st.markdown("## Key Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📊 Track Usage")
        st.markdown("Monitor API requests across models")

    with col2:
        st.markdown("### 💰 Control Costs")
        st.markdown("Analyze spending and trends")

    with col3:
        st.markdown("### 🔑 Manage Keys")
        st.markdown("Secure and track API keys")

    # Add helpful tips
    st.markdown("### 💡 Tips for Getting the Most Out of OpenAI Guardian")

    with st.expander("Understanding Your Dashboard", expanded=False):
        st.markdown("""
        - **Usage Overview**: Track API requests by day and model
        - **Cost Analysis**: Monitor spending and identify trends
        - **API Key Management**: Manage and revoke keys as needed
        """)

    with st.expander("Optimizing Your OpenAI Costs", expanded=False):
        st.markdown("""
        - Monitor peak usage days to identify potential optimizations
        - Compare model usage to find cost-saving opportunities
        - Track API key activity to identify unused or overused keys
        """)

    with st.expander("Security Best Practices", expanded=False):
        st.markdown("""
        - Regularly audit API keys and revoke unused ones
        - Create separate keys for different applications or services
        - Monitor for unusual activity patterns in your usage data
        """)

# Enhanced footer
st.markdown("""
<div class="footer">
    <div>OpenAI Guardian</div>
    <div style="margin-top: 5px; font-size: 0.8rem;">v1.2.0 • Last updated: April 2025</div>
</div>
""", unsafe_allow_html=True)
