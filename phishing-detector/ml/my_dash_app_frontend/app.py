import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import requests

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder="assets"
)

API_URL = "http://127.0.0.1:8000"

app.layout = html.Div(className="container", children=[
    html.Div(className="card", children=[
        html.H1("🛡️ AI-Powered Phishing Detector"),
        html.P("Enter a URL to check if it's phishing or legitimate.",
               className="subtitle"),

        dbc.Row([
            dbc.Col([
                dbc.Input(
                    id="url-input",
                    type="text",
                    placeholder="Enter a URL (e.g. http://suspicious-login.com)",
                    size="lg",
                    className="mb-3"
                ),
            ], width=9),
            dbc.Col([
                dbc.Select(
                    id="model-select",
                    options=[
                        {"label": "ML Model (XGBoost)", "value": "predict"},
                        {"label": "Transformer (BERT)", "value": "predict/transformer"},
                        {"label": "Live Check (OpenPhish)", "value": "check-live"},
                    ],
                    value="predict",
                    className="mb-3"
                ),
            ], width=3),
        ]),

        dbc.Button(
            "Check for Phishing",
            id="check-button",
            color="primary",
            size="lg",
            className="w-100 mb-3"
        ),

        dcc.Loading(
            id="loading",
            type="circle",
            children=[html.Div(id="result-output")]
        ),
    ]),

    html.Div(className="card", children=[
        html.H4("📊 How it works"),
        html.P("This tool uses three detection methods:"),
        html.Ul([
            html.Li("🤖 ML Model (XGBoost) — trained on 111,754 URLs with 99.92% accuracy"),
            html.Li("🧠 Transformer (BERT) — fine-tuned DistilBERT with 99.98% accuracy"),
            html.Li("🌐 Live Check — queries OpenPhish live threat database"),
        ])
    ])
])

@callback(
    Output("result-output", "children"),
    Input("check-button", "n_clicks"),
    State("url-input", "value"),
    State("model-select", "value"),
    prevent_initial_call=True
)
def check_url(n_clicks, url, model):
    if not url:
        return dbc.Alert("Please enter a URL.", color="warning")

    try:
        response = requests.post(
            f"{API_URL}/{model}",
            json={"text": url},
            timeout=10
        )
        result = response.json()

        is_phishing = result.get("is_phishing", False)
        confidence = result.get("confidence", 0)
        confidence_pct = f"{confidence * 100:.2f}%"

        if is_phishing:
            return html.Div(className="phishing", children=[
                html.H3("⚠️ Phishing Detected!"),
                html.P(f"URL: {url}"),
                html.P(f"Confidence: {confidence_pct}"),
                html.P("This URL appears to be malicious. Do not visit it.")
            ])
        else:
            return html.Div(className="safe", children=[
                html.H3("✅ Safe"),
                html.P(f"URL: {url}"),
                html.P(f"Confidence: {confidence_pct}"),
                html.P("This URL appears to be legitimate.")
            ])

    except Exception as e:
        return dbc.Alert(f"Error connecting to API: {str(e)}", color="danger")

if __name__ == "__main__":
    app.run(debug=True, port=8050)