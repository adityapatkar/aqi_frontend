mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
[theme]
primaryColor = '#55DB98'
backgroundColor = '#EAEFFB'
secondaryBackgroundColor = '#FFFFFF'
textColor = '#000000'
font = 'sans-serif'
" > ~/.streamlit/config.toml