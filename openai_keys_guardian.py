import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List

# Set page configuration
st.set_page_config(
    page_title="OpenAI Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simplified CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #0f52ba;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1e88e5;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }
    .card {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
    }
    .warning { color: #ff5252; font-weight: bold; }
    .success { color: #4caf50; font-weight: bold; }
    .info { color: #2196f3; font-weight: bold; }
    .api-key-card {
        background-color: #e8f4fd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        color: #9e9e9e;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Simplified sidebar
st.sidebar.markdown("## OpenAI Guardian 🛡️")
st.sidebar.markdown("---")

# OpenAI Admin API Key input with toggle for visibility
api_key = st.sidebar.text_input("Enter OpenAI Admin API Key", type="password")
show_key = st.sidebar.checkbox("Show API Key")
if show_key:
    st.sidebar.code(api_key if api_key else "No API key entered")

# Initialize session state for storing project data
if 'projects' not in st.session_state:
    st.session_state.projects = []
    st.session_state.project_ids_map = {}
    st.session_state.selected_project_id = None
    st.session_state.api_keys = []
    st.session_state.usage_data = {}
    # Set default date range to one month
    st.session_state.start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    st.session_state.end_date = datetime.now().strftime('%Y-%m-%d')

# Simplified date range selection
st.sidebar.markdown("## Date Range")

# Quick date range selector
date_range_options = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "Last 180 days": 180,
    "Last 365 days": 365
}

selected_range = st.sidebar.selectbox(
    "Quick select",
    options=list(date_range_options.keys()),
    index=1  # Default to 30 days
)

# Apply the selected range when the user changes it
if st.sidebar.button("Apply Range", use_container_width=True):
    days = date_range_options[selected_range]
    st.session_state.start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    st.session_state.end_date = datetime.now().strftime('%Y-%m-%d')
    st.rerun()

# Custom date range input
st.sidebar.markdown("### Custom Range")
col1, col2 = st.sidebar.columns(2)
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

# Refresh button
if st.sidebar.button("Refresh Data", use_container_width=True):
    st.session_state.refresh_counter = st.session_state.get('refresh_counter', 0) + 1

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("""
OpenAI Guardian helps you:
- Monitor API usage and costs
- Track usage trends
- Manage API keys
""")

# Simplified API interaction functions
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
        st.error(f"API Error: {e}")
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
    """Revoke an API key."""
    url = f"https://api.openai.com/v1/organization/projects/{project_id}/api_keys/{key_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True
    except:
        st.warning("Could not revoke key. Please revoke it manually in the OpenAI dashboard.")
        return False

def estimate_cost(usage_data: Dict) -> Dict:
    """Estimate cost based on usage data and model pricing."""
    # Simplified pricing model
    pricing = {
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4o': {'input': 0.005, 'output': 0.015},
        'default': {'input': 0.01, 'output': 0.02}
    }

    costs = {'daily': {}, 'total': 0, 'models': {}}

    # Check if we have the new data structure
    if 'data' in usage_data and isinstance(usage_data['data'], list):
        # New structure: data is a list of buckets
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

    # If no usage data was found or processed, ensure we have at least empty structures
    if not costs['daily']:
        # Add dates from the date range to show empty bars in chart
        start_date = datetime.strptime(st.session_state.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(st.session_state.end_date, '%Y-%m-%d')
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            costs['daily'][date_str] = 0
            current_date += timedelta(days=1)

    return costs

def process_costs_data(costs_data: Dict) -> Dict:
    """Process the cost data from the API."""
    processed_costs = {'daily': {}, 'total': 0, 'line_items': {}}

    # Check if we have the data structure
    if 'data' in costs_data and isinstance(costs_data['data'], list):
        # Data is a list of buckets
        buckets = costs_data.get('data', [])

        for bucket in buckets:
            date = bucket.get('start_time', 0)
            date_str = datetime.fromtimestamp(date).strftime('%Y-%m-%d')

            # Initialize daily cost for this date if not exists
            if date_str not in processed_costs['daily']:
                processed_costs['daily'][date_str] = 0

            # Process results in this bucket
            for result in bucket.get('results', []):
                # Handle different possible structures in the API response
                if isinstance(result, dict):
                    # Get line item (could be under different keys depending on API version)
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
                            # If we can't find a numeric value, use 0
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

    # If no cost data was found, ensure we have at least empty structures
    if not processed_costs['daily']:
        # Add dates from the date range to show empty bars in chart
        start_date = datetime.strptime(st.session_state.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(st.session_state.end_date, '%Y-%m-%d')
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            processed_costs['daily'][date_str] = 0
            current_date += timedelta(days=1)

    # Sort the daily costs by date
    processed_costs['daily'] = dict(sorted(processed_costs['daily'].items()))

    return processed_costs

def process_api_key_usage(api_key_usage: Dict, api_keys: List[Dict]) -> Dict:
    """Process the API key usage data."""
    # Create a mapping of API key IDs to names
    key_id_to_name = {key.get('id'): key.get('name', 'Unnamed Key') for key in api_keys if key.get('id')}

    # Initialize the processed data structure
    processed_data = {'daily': {}, 'keys': {}}

    # Check if we have the data structure
    if 'data' in api_key_usage and isinstance(api_key_usage['data'], list):
        # Data is a list of buckets
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

    # Ensure all keys have data for all dates
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

# Add the missing rate limits function
@st.cache_data(ttl=300)
def fetch_project_rate_limits(api_key: str, project_id: str) -> List[Dict]:
    """Fetch rate limits for a specific project."""
    url = f"https://api.openai.com/v1/organization/projects/{project_id}/rate_limits"
    response = make_api_request(url, api_key, {"limit": 100})
    return response.get('data', [])

# Main dashboard UI
st.markdown("<h1 class='main-header'>OpenAI Guardian</h1>", unsafe_allow_html=True)

# Display Project Management section only if API key is provided
if api_key:
    # Fetch projects button and project selection in the same row
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("Fetch Projects", use_container_width=True):
            with st.spinner("Fetching projects..."):
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
                    st.success(f"Found {len(projects)} projects")
                else:
                    st.error("No projects found")

    # Project selection dropdown
    with col2:
        if st.session_state.projects:
            selected_project_name = st.selectbox(
                "Select a project",
                options=st.session_state.projects
            )

            if selected_project_name in st.session_state.project_ids_map:
                st.session_state.selected_project_id = st.session_state.project_ids_map[selected_project_name]

                # Load button
                if st.button("Load Data", use_container_width=True):
                    with st.spinner(f"Loading data for {selected_project_name}..."):
                        # Fetch API keys
                        api_keys = fetch_project_api_keys(api_key, st.session_state.selected_project_id)
                        st.session_state.api_keys = api_keys

                        # Fetch usage data
                        usage_data = fetch_usage_data(
                            api_key,
                            st.session_state.selected_project_id,
                            st.session_state.start_date,
                            st.session_state.end_date
                        )
                        st.session_state.usage_data = usage_data

                        # Fetch cost data
                        costs_data = fetch_costs_data(
                            api_key,
                            st.session_state.selected_project_id,
                            st.session_state.start_date,
                            st.session_state.end_date
                        )
                        st.session_state.costs_data = costs_data

                        # Fetch API key usage data if we have API keys
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

                        st.success("Data loaded successfully")

    # Display dashboard if project is selected
    if st.session_state.get('selected_project_id'):
        # Get the selected project name
        selected_project_name = next((name for name, id in st.session_state.project_ids_map.items()
                                    if id == st.session_state.selected_project_id), "Selected Project")

        # Display project header
        st.markdown(f"## Project: {selected_project_name}")
        st.markdown(f"ID: `{st.session_state.selected_project_id}`")
        st.markdown("---")

        # Create tabs for different views
        tab1, tab2 = st.tabs(["Usage & Cost Analysis", "API Keys"])

        with tab1:
            # Quick metrics
            col1, col2, col3 = st.columns(3)

            # Calculate metrics
            api_keys = st.session_state.get('api_keys', [])
            num_api_keys = len(api_keys)
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

            with col1:
                st.metric("API Keys", num_api_keys)

            with col2:
                st.metric("Total Cost", f"${actual_total_cost:.2f}")

            with col3:
                st.metric("Date Range", f"{date_range} days")

            # Cost Analysis
            st.subheader("Cost Analysis")

            if costs_data:
                # Daily cost chart
                daily_cost_data = []
                for date, cost in processed_costs['daily'].items():
                    daily_cost_data.append({
                        'Date': date,
                        'Cost (USD)': cost
                    })

                # Sort by date
                daily_cost_data = sorted(daily_cost_data, key=lambda x: x['Date'])

                # Create DataFrame
                df_daily_cost = pd.DataFrame(daily_cost_data)

                # Check if there's any actual cost data
                has_cost_data = any(cost > 0 for cost in processed_costs['daily'].values())

                if has_cost_data:
                    # Create daily cost chart
                    fig_daily_cost = px.line(
                        df_daily_cost,
                        x='Date',
                        y='Cost (USD)',
                        title='Daily Cost',
                        markers=True
                    )

                    st.plotly_chart(fig_daily_cost, use_container_width=True)

                    # Line item breakdown
                    if processed_costs.get('line_items'):
                        st.subheader("Model Usage Breakdown")

                        line_item_data = []
                        for item, cost in processed_costs['line_items'].items():
                            if cost > 0:  # Only include items with cost
                                line_item_data.append({
                                    'Model, I\\O': item,
                                    'Cost (USD)': cost
                                })

                        if line_item_data:
                            # Create DataFrame
                            df_line_items = pd.DataFrame(line_item_data)

                            # Create pie chart
                            fig_line_items = px.pie(
                                df_line_items,
                                values='Cost (USD)',
                                names='Model, I\\O',
                                title='Models i\\o Cost Distribution',
                                hole=0.4
                            )

                            st.plotly_chart(fig_line_items, use_container_width=True)

                            # Display line item table
                            st.dataframe(
                                df_line_items.sort_values(by='Cost (USD)', ascending=False),
                                use_container_width=True
                            )
                else:
                    st.info("No cost data available for the selected date range.")
            else:
                st.info("No cost data available. Click 'Load Data' to fetch cost information.")



        with tab2:
            # API Keys management
            st.subheader("API Keys")

            # API Key Usage Chart
            st.markdown("### API Key Usage")

            # Get API key usage data if available
            api_key_usage = st.session_state.get('api_key_usage', {})
            api_keys = st.session_state.get('api_keys', [])

            if api_key_usage and api_keys:
                processed_key_usage = process_api_key_usage(api_key_usage, api_keys)

                if processed_key_usage['keys']:
                    # Prepare data for line chart
                    line_data = []

                    for key_name, key_data in processed_key_usage['keys'].items():
                        for date, requests in key_data['daily'].items():
                            line_data.append({
                                'Date': date,
                                'API Key': key_name,
                                'Requests': requests
                            })

                    # Sort by date
                    line_data = sorted(line_data, key=lambda x: x['Date'])

                    # Create DataFrame
                    df_line = pd.DataFrame(line_data)

                    # Check if there's any actual usage data
                    has_usage_data = any(item['Requests'] > 0 for item in line_data)

                    if has_usage_data:
                        # Create line chart
                        fig_line = px.line(
                            df_line,
                            x='Date',
                            y='Requests',
                            color='API Key',
                            title='API Key Usage (Requests per Day)',
                            markers=True
                        )

                        st.plotly_chart(fig_line, use_container_width=True)

                        # Display total requests by key
                        st.markdown("### Total Requests by API Key")

                        key_totals = []
                        for key_name, key_data in processed_key_usage['keys'].items():
                            key_totals.append({
                                'API Key': key_name,
                                'Total Requests': key_data['total']
                            })

                        # Create DataFrame
                        df_key_totals = pd.DataFrame(key_totals)

                        # Display as bar chart
                        fig_key_totals = px.bar(
                            df_key_totals.sort_values(by='Total Requests', ascending=False),
                            x='API Key',
                            y='Total Requests',
                            title='Total Requests by API Key',
                            color='API Key'
                        )

                        st.plotly_chart(fig_key_totals, use_container_width=True)
                    else:
                        st.info("No API key usage data available for the selected date range.")
                else:
                    st.info("No API key usage data available.")
            else:
                st.info("No API key usage data available. Click 'Load Data' to fetch API key usage information.")

            # API Keys List
            st.markdown("### API Keys List")

            # Get API keys (if available)
            api_keys = st.session_state.get('api_keys', [])

            if api_keys:
                # Track deleted keys
                deleted_keys = st.session_state.get('deleted_keys', set())

                for key in api_keys:
                    key_id = key.get('id', 'Unknown')
                    key_name = key.get('name', 'Unnamed Key')
                    key_object = key.get('object', 'Unknown')
                    key_owner = key.get('owner', 'Unknown')
                    created_at = key.get('created_at', 'Unknown')
                    last_used = key.get('last_used_at', 'Never')

                    # Check if this key has been deleted
                    is_deleted = key_id in deleted_keys

                    # Format dates if available
                    # Handle timestamps (integers) or ISO format dates
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

                    # Display key information in an expandable card with status indicator
                    expander_title = f"{key_name}" if not is_deleted else f"{key_name} (REVOKED)"
                    expander_color = "" if not is_deleted else "color: #ff5252;"

                    with st.expander(expander_title, expanded=False):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**ID:** {key_id}")
                            st.markdown(f"**Type:** {key_object}")
                            st.markdown(f"**Owner:** {key_owner}")
                            if is_deleted:
                                st.markdown("**Status:** <span style='color: #ff5252;'>REVOKED</span>", unsafe_allow_html=True)

                        with col2:
                            st.markdown(f"**Created:** {created_at}")
                            st.markdown(f"**Last Used:** {last_used}")

                        # Display redacted key value if available
                        redacted_value = key.get('redacted_value')
                        if redacted_value:
                            st.text_input("Redacted API Key", value=redacted_value, disabled=True)

                        # Add revoke button (only if not already deleted)
                        if not is_deleted:
                            if st.button(f"Revoke Key", key=f"revoke_{key_id}"):
                                with st.spinner("Revoking key..."):
                                    success = revoke_api_key(api_key, st.session_state.selected_project_id, key_id)
                                    if success:
                                        # Add to deleted keys set
                                        if 'deleted_keys' not in st.session_state:
                                            st.session_state.deleted_keys = set()
                                        st.session_state.deleted_keys.add(key_id)
                                        st.success(f"Key revoked successfully")
                                        st.rerun()
            else:
                # Display message when no API keys are available
                st.info("No API keys found for this project. Click 'Load Data' to fetch API keys.")

                # Add a button to load data if it hasn't been loaded yet
                if not st.session_state.get('api_keys'):
                    if st.button("Load API Keys"):
                        with st.spinner("Loading API keys..."):
                            api_keys = fetch_project_api_keys(api_key, st.session_state.selected_project_id)
                            st.session_state.api_keys = api_keys
                            st.success(f"Found {len(api_keys)} API keys")
                            st.rerun()
else:
    # Display instructions when no API key is provided
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Getting Started")
    st.markdown("""
    1. Enter your OpenAI Admin API Key in the sidebar
    2. Click "Fetch Projects" to load your projects
    3. Select a project and click "Load Data"
    4. View your usage dashboard and manage API keys
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown("OpenAI Guardian")
st.markdown("</div>", unsafe_allow_html=True)

