#!/bin/bash

# Beendet Streamlit sauber bei SIGTERM/SIGINT
cleanup() {
    echo "Stopping Streamlit..."
    kill -s SIGTERM $PID
    wait $PID
    echo "Streamlit stopped."
}

trap cleanup SIGINT SIGTERM

# Starte Streamlit
streamlit run app.py --server.port=8501 --server.enableCORS=false &
PID=$!

# Warten, bis Streamlit beendet wird
wait $PID
