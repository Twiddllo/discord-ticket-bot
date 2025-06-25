# Discord Bot Configuration

# Bot Token (DO NOT SHARE THIS PUBLICLY)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Channel and Category IDs
BUY_TICKET_CATEGORY_ID = 1329051188339146843
SUPPORT_TICKET_CATEGORY_ID = 1329051180692803658
INITIAL_MESSAGE_CHANNEL_ID = 1329051149038260275
LOG_CHANNEL_ID = 1329051230487580778

# Role prices (in EUR)
ROLES = {
    "Silver": 5,
    "Gold": 10,
    "Champion": 20,
    "View Access": 30,
    "Private Bot (MONTHLY)": 30,
    "Private Bot (LIFETIME)": 70,
    "View Access (PRO)": 70,
    " V I P ": 150
}

# Crypto addresses
CRYPTO_ADDRESSES = {
    "USDT": "TLop2zYyN5euprRLhxZj4MDtRx87VdifwR",
    "LTC": "LWK8XimA8AyVAghdXV2rVU4ziAyveCiZ5t",
    "BTC": "36yS3NUt4rcSNg6ySLATHRhsSKHCpScZkN",
    "Others": "Please specify the cryptocurrency and an address will be provided by twiddllo."
}

# Cooldown duration (in minutes)
COOLDOWN_MINUTES = 5

# Admin/Helper role name
HELPER_ROLE_NAME = "Helper"

# UI Labels and Select Options
TICKET_SELECT_OPTIONS = [
    {"label": "Support", "value": "Support", "description": "Get help with an issue"},
    {"label": "Buy", "value": "Buy", "description": "Purchase a role"}
]

BUY_ROLE_SELECT_OPTIONS = [
    {"label": "Silver", "value": "Silver", "description": "€5"},
    {"label": "Gold", "value": "Gold", "description": "€10"},
    {"label": "Champion", "value": "Champion", "description": "€20"},
    {"label": "View Access", "value": "View Access", "description": "€30"},
    {"label": "Private Bot (MONTHLY)", "value": "Private Bot (MONTHLY)", "description": "€30"},
    {"label": "View Access (PRO)", "value": "View Access (PRO)", "description": "€70"},
    {"label": "Private Bot (LIFETIME)", "value": "Private Bot (LIFETIME)", "description": "€70"},
    {"label": " V I P ", "value": " V I P ", "description": "€150"}
]

PAYMENT_METHOD_SELECT_OPTIONS = [
    {"label": "PayPal", "value": "PayPal", "description": "Add 20% fees"},
    {"label": "Crypto", "value": "Crypto", "description": "Choose from various cryptocurrencies"}
]

CRYPTO_SELECT_OPTIONS = [
    {"label": "USDT", "value": "USDT"},
    {"label": "LTC", "value": "LTC"},
    {"label": "BTC", "value": "BTC"},
    {"label": "Others", "value": "Others"}
]

# Button Labels
PING_SUPPORT_LABEL = "Ping Support"
NOTIFY_LABEL = "Notify"
CLOSE_LABEL = "Close"
CREATE_TICKET_LABEL = "Create Ticket" 