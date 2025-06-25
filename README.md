# 🎟️ Discord Ticket Bot

A powerful, fully-configurable Discord bot for managing support and purchase tickets in your server. Users can create tickets, select payment methods, and receive logs. Staff can manage, notify, and close tickets with logs sent to both the user and a log channel.

---

## ✨ Features
- 📝 **Create support or purchase tickets** via interactive buttons and dropdowns
- 💸 **Role-based pricing** and crypto address selection
- 🛡️ **Staff notification** and ticket management
- 📄 **HTML log generation** and delivery on ticket close
- ⚙️ **Everything configurable** via a single `config.py` file (no code edits needed!)
- ⏳ **Cooldown system** to prevent spam
- 🔒 **Security best practices**

---

## 🛠️ Requirements
- Python 3.8+
- [`discord.py`](https://pypi.org/project/discord.py/) (v2.x)

---

## 🚀 Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/discord-ticket-bot.git
   cd discord-ticket-bot
   ```
2. **Install dependencies:**
   ```bash
   pip install -U discord.py
   ```

---

## ⚙️ Configuration
All settings are in `config.py`. **You never need to edit the main code!**

### 🔑 Essentials
- `BOT_TOKEN`: Your Discord bot token
- Channel/Category IDs: `BUY_TICKET_CATEGORY_ID`, `SUPPORT_TICKET_CATEGORY_ID`, `INITIAL_MESSAGE_CHANNEL_ID`, `LOG_CHANNEL_ID`
- `ROLES`: Role names and prices (EUR)
- `CRYPTO_ADDRESSES`: Crypto addresses for payments
- `COOLDOWN_MINUTES`: Cooldown for pinging support
- `HELPER_ROLE_NAME`: Name of your staff/helper role

### 🎨 UI Customization
- `TICKET_SELECT_OPTIONS`: Options for the main ticket type select (label, value, description)
- `BUY_ROLE_SELECT_OPTIONS`: Options for the buy role select (label, value, description)
- `PAYMENT_METHOD_SELECT_OPTIONS`: Payment method select options
- `CRYPTO_SELECT_OPTIONS`: Crypto select options
- `PING_SUPPORT_LABEL`, `NOTIFY_LABEL`, `CLOSE_LABEL`, `CREATE_TICKET_LABEL`: Button labels

#### Example:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
BUY_TICKET_CATEGORY_ID = 123456789012345678
SUPPORT_TICKET_CATEGORY_ID = 123456789012345679
INITIAL_MESSAGE_CHANNEL_ID = 123456789012345680
LOG_CHANNEL_ID = 123456789012345681
ROLES = {"Silver": 5, "Gold": 10}
CRYPTO_ADDRESSES = {"USDT": "...", "BTC": "..."}
COOLDOWN_MINUTES = 5
HELPER_ROLE_NAME = "Helper"
TICKET_SELECT_OPTIONS = [
    {"label": "Support", "value": "Support", "description": "Get help with an issue"},
    {"label": "Buy", "value": "Buy", "description": "Purchase a role"}
]
# ...and so on for other options
```

> **Tip:** Use emojis in your labels for extra flair! Example: `{ "label": "🛒 Buy", ... }`

---

## ▶️ Running the Bot
```bash
python ticket.py
```

---

## 💡 Usage
- On startup, the bot posts a ticket creation message in your configured channel.
- Users click the button to create a support or purchase ticket.
- Staff can use these commands:
  - `!refresh` (Helper only): Reposts the ticket creation message
  - `!prules`: Posts PayPal payment rules
  - `!notify @user` (Helper only): Notifies a ticket owner via DM
  - `!close [@user]` (Helper only): Closes the ticket, sends the log to the user and log channel, and deletes the channel

---

## 🔒 Security Tips
- **Never commit your real bot token to GitHub!**
- `.gitignore` already excludes `config.py` for you
- Limit bot permissions to only what is necessary

---

## 🧩 Customization
- Change role prices, crypto addresses, cooldowns, UI text, and select options in `config.py`
- For advanced changes, edit `ticket.py` (not needed for most users)

---

## 🙋 FAQ
**Q: Can I use this bot in any language?**
> Yes! Just change the labels and descriptions in `config.py`.

**Q: Can I add more roles or payment methods?**
> Absolutely! Add more entries to the relevant lists in `config.py`.

**Q: How do I update the UI with emojis?**
> Add emojis to the `label` fields in your select/button options.

---

## 📄 License
MIT

---

> Made with ❤️ for the Discord community! 