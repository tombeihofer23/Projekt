from src.hanoi_dashboard.app import app


def main():
    app.run(debug=True, host="0.0.0.0", port=8050)
