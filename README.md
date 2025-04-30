# OpenAI Guardian

A comprehensive dashboard for monitoring and managing OpenAI API usage, costs, and API keys.\
112% Vibe coding


## Features

- **Track API Usage**: Monitor API requests across different models and time periods
- **Analyze Costs**: Visualize spending patterns and identify cost drivers
- **Manage API Keys**: View, monitor, and revoke API keys from a single interface
- **Interactive Dashboards**: Explore your data with interactive charts and filters

## Getting Started

### Prerequisites

- Python 3.7+
- OpenAI Admin API Key with organization-wide access

### Installation

1. Clone this repository


2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run openai_keys_guardian.py
   ```

## Usage

1. Enter your OpenAI Admin API Key in the sidebar
2. Click "Fetch Projects" to load your projects
3. Select a project and click "Load Dashboard Data"
4. Navigate through the tabs to explore usage, costs, and API keys

## Dashboard Sections

### Usage Overview
- Track daily API requests
- Analyze model distribution
- Monitor usage trends over time

### Cost Analysis
- View daily and total costs
- Break down costs by model/line item
- Identify cost optimization opportunities

### API Key Management
- View all API keys with detailed information
- Monitor API key usage
- Revoke API keys when needed

## Security Notes

- Your API key is never stored permanently and is only used for the current session
- All data is processed locally in your browser
- No data is sent to external servers beyond the OpenAI API

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses the [OpenAI API](https://platform.openai.com/)
- Visualizations powered by [Plotly](https://plotly.com/)
