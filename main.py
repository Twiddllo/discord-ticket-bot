import discord
from discord.ext import commands
import os
from discord import File
from datetime import datetime, timedelta
import config

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

COOLDOWN_DURATION = timedelta(minutes=config.COOLDOWN_MINUTES)
user_cooldowns = {}
BUY_TICKET_CATEGORY_ID = config.BUY_TICKET_CATEGORY_ID
SUPPORT_TICKET_CATEGORY_ID = config.SUPPORT_TICKET_CATEGORY_ID
INITIAL_MESSAGE_CHANNEL_ID = config.INITIAL_MESSAGE_CHANNEL_ID
LOG_CHANNEL_ID = config.LOG_CHANNEL_ID
roles = config.ROLES
crypto_addresses = config.CRYPTO_ADDRESSES
active_tickets = {}
HELPER_ROLE_NAME = config.HELPER_ROLE_NAME

class SupportModal(discord.ui.Modal, title="Support Request"):
    subject = discord.ui.TextInput(label="Subject", required=True, placeholder="Enter the subject of your request")
    details = discord.ui.TextInput(label="Details", style=discord.TextStyle.paragraph, required=True, placeholder="Enter detailed information about your request")

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=SUPPORT_TICKET_CATEGORY_ID)
        channel_name = f'support-{interaction.user.name}'
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
        }
        helper_role = discord.utils.get(guild.roles, name=HELPER_ROLE_NAME)
        if helper_role:
            overwrites[helper_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await channel.send(
            embed=discord.Embed(
                title="Support Ticket Created",
                description=f"{interaction.user.mention} has opened a support ticket.\n\n\n"
                            f"## {self.subject.value}\n"
                            f"**Details**: {self.details.value}",
                color=discord.Color.blue()
            ).set_footer(text="Support Ticket"),
            view=TicketControlView(interaction.user)
        )
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Support Ticket Created",
                description=f"Support ticket created in {channel.mention}",
                color=discord.Color.green()
            ),
            ephemeral=True
        )
        if channel:
            active_tickets[interaction.user.id] = interaction.message.id

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=opt["label"], value=opt["value"], description=opt.get("description")) for opt in config.TICKET_SELECT_OPTIONS]
        super().__init__(placeholder="Choose an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in active_tickets:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Active Ticket",
                    description="You already have an active ticket.",
                    color=discord.Color.orange()
                ),
                ephemeral=True
            )
            return
        if self.values[0] == "Support":
            await interaction.response.send_modal(SupportModal())
        elif self.values[0] == "Buy":
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Buy Selection",
                    description="Choose a plan to buy:",
                    color=discord.Color.blue()
                ),
                view=BuyRoleView(),
                ephemeral=True
            )
        self.disabled = True
        await interaction.message.edit(view=self.view)

class SelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class SupportModalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SupportModal())

class BuyRoleSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=opt["label"], value=opt["value"], description=opt.get("description")) for opt in config.BUY_ROLE_SELECT_OPTIONS]
        super().__init__(placeholder="Select a role", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_roles = ', '.join([role.capitalize() for role in self.values])
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Payment Method",
                description=f"You selected: {selected_roles}. Choose a payment method:",
                color=discord.Color.blue()
            ),
            view=PaymentMethodView(roles=self.values),
            ephemeral=True
        )
        self.disabled = True
        await interaction.message.edit(view=self.view)

class BuyRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BuyRoleSelect())

class PaymentMethodSelect(discord.ui.Select):
    def __init__(self, role):
        self.role = role
        options = [discord.SelectOption(label=opt["label"], value=opt["value"], description=opt.get("description")) for opt in config.PAYMENT_METHOD_SELECT_OPTIONS]
        super().__init__(placeholder="Select a payment method", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "PayPal":
            price = roles[self.role] * 1.2
            guild = interaction.guild
            category = discord.utils.get(guild.categories, id=BUY_TICKET_CATEGORY_ID)
            channel_name = f'buy-paypal-{interaction.user.name}'
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
            }
            helper_role = discord.utils.get(guild.roles, name=HELPER_ROLE_NAME)
            if helper_role:
                overwrites[helper_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
            await channel.send(
                embed=discord.Embed(
                    title="PayPal Payment Instructions",
                    description=(
                        f"{interaction.user.mention},\n\n"
                        f"You are purchasing the **{self.role.capitalize()}**  "
                        f"for **{price:.2f} EUR** (including fees).\n\n"
                        f"**Instructions:**\n"
                        f"1. Wait for @twiddllo to send you the PayPal email.\n"
                        f"2. Once you receive the email, complete the payment.\n\n"
                        f"**Important:**\n"
                        f"Please make sure to read our [PayPal payment rules]"
                        "(https://discord.com/channels/1277575605617168487/1277785393063788654/1279282967000387598). "
                        "Failure to comply with these rules will result in no refund and no service."
                    ),
                    color=discord.Color.green()
                )
            )
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Payment Channel Created",
                    description=f"Your payment channel is {channel.mention}. Please check it for further instructions.",
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        elif self.values[0] == "Crypto":
            price = roles[self.role]
            guild = interaction.guild
            category = discord.utils.get(guild.categories, id=BUY_TICKET_CATEGORY_ID)
            channel_name = f'buy-crypto-{interaction.user.name}'
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
            }
            helper_role = discord.utils.get(guild.roles, name=HELPER_ROLE_NAME)
            if helper_role:
                overwrites[helper_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
            crypto_options = "\n".join([f"{crypto}: {address}" for crypto, address in crypto_addresses.items()])
            await channel.send(
                embed=discord.Embed(
                    title="Crypto Payment Instructions",
                    description=(
                        f"{interaction.user.mention},\n\n"
                        f"You are purchasing the **{self.role.capitalize()}** for **{roles[self.role]} EUR**.\n\n"
                        f"**Please pay to the following crypto addresses:**\n\n"
                        f"{crypto_options}\n\n"
                        f"Once the payment is completed, please provide the transaction hash(TXID) in proof seloution"
                    ),
                    color=discord.Color.green()
                )
            )
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Payment Channel Created",
                    description=f"A payment channel has been created: {channel.mention}. Please follow the instructions there.",
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        active_tickets[interaction.user.id] = interaction.message.id
        self.disabled = True
        await interaction.message.edit(view=self.view)

class PaymentMethodView(discord.ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        self.add_item(PaymentMethodSelect(role=roles[0]))

class CryptoSelect(discord.ui.Select):
    def __init__(self, role):
        self.role = role
        options = [discord.SelectOption(label=opt["label"], value=opt["value"]) for opt in config.CRYPTO_SELECT_OPTIONS]
        super().__init__(placeholder="Select a cryptocurrency", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        crypto = self.values[0]
        address = crypto_addresses.get(crypto, "Address not available")
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=BUY_TICKET_CATEGORY_ID)
        channel_name = f'buy-{crypto.lower()}-{interaction.user.name}'
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
        }
        helper_role = discord.utils.get(guild.roles, name=HELPER_ROLE_NAME)
        if helper_role:
            overwrites[helper_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        await channel.send(
            embed=discord.Embed(
                title="Payment Instructions",
                description=(
                    f"{interaction.user.mention}, please send the payment for the **{self.role.capitalize()}** "
                    f"(€{roles[self.role]:.2f}) to the following address:\n"
                    f"**{crypto} Address**: {address}\n"
                    "After sending the payment, please provide proof of payment here. Our staff will verify your payment shortly."
                ),
                color=discord.Color.green()
            ).set_footer(text="Payment Instructions"),
            view=TicketControlView(interaction.user)
        )
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Payment Channel Created",
                description=f"A payment channel has been created: {channel.mention}. Please follow the instructions there.",
                color=discord.Color.green()
            ),
            ephemeral=True
        )
        active_tickets[interaction.user.id] = interaction.message.id
        self.disabled = True
        await interaction.message.edit(view=self.view)

class CryptoView(discord.ui.View):
    def __init__(self, *, role):
        super().__init__()
        self.add_item(CryptoSelect(role))

class TicketControlView(discord.ui.View):
    def __init__(self, ticket_owner):
        super().__init__()
        self.ticket_owner = ticket_owner
        self.add_item(PingSupportButton())
        self.add_item(NotifyButton(ticket_owner))
        self.add_item(CloseTicketButton(ticket_owner))

class PingSupportButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label=config.PING_SUPPORT_LABEL, style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = datetime.utcnow()
        if user_id in user_cooldowns:
            last_used_time = user_cooldowns[user_id]
            if current_time - last_used_time < COOLDOWN_DURATION:
                remaining_time = COOLDOWN_DURATION - (current_time - last_used_time)
                await interaction.response.send_message(
                    f"Please wait {remaining_time.seconds // 60} minute(s) and {remaining_time.seconds % 60} second(s) before using this button again.",
                    ephemeral=True
                )
                return
        user_cooldowns[user_id] = current_time
        staff_role = discord.utils.get(interaction.guild.roles, name=HELPER_ROLE_NAME)
        if staff_role:
            await interaction.channel.send(f"{staff_role.mention}, {interaction.user.mention} needs assistance.")
        else:
            await interaction.response.send_message("The staff role does not exist.", ephemeral=True)

class NotifyButton(discord.ui.Button):
    def __init__(self, ticket_owner):
        super().__init__(label=config.NOTIFY_LABEL, style=discord.ButtonStyle.secondary)
        self.ticket_owner = ticket_owner

    async def callback(self, interaction: discord.Interaction):
        helper_role = discord.utils.get(interaction.guild.roles, name=HELPER_ROLE_NAME)
        if helper_role not in interaction.user.roles:
            await interaction.response.send_message("You do not have the required role to use this button.", ephemeral=True)
            return
        ticket_url = interaction.message.jump_url
        try:
            await self.ticket_owner.send(f"Please check your ticket: {ticket_url}")
            await interaction.response.send_message(f"Notification sent to {self.ticket_owner.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Failed to send DM. The user might have DMs disabled.", ephemeral=True)

    async def callback(self, interaction: discord.Interaction):
        ticket_url = interaction.message.jump_url
        try:
            await self.ticket_owner.send(f"Please check your ticket: {ticket_url}")
            await interaction.response.send_message(f"Notification sent to {self.ticket_owner.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Failed to send DM. The user might have DMs disabled.", ephemeral=True)

class CloseTicketButton(discord.ui.Button):
    def __init__(self, ticket_owner):
        super().__init__(label=config.CLOSE_LABEL, style=discord.ButtonStyle.danger)
        self.ticket_owner = ticket_owner

    async def callback(self, interaction: discord.Interaction):
        messages = []
        async for message in interaction.channel.history(limit=None):
            messages.append(message)
        html_content = generate_html_log(messages, interaction.channel.name)
        file_name = f"{interaction.channel.name}_log.html"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(html_content)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await self.ticket_owner.send("Here is the log of your ticket:", file=File(file_name))
        await log_channel.send(f"Log for ticket {interaction.channel.name}:", file=File(file_name))
        await interaction.channel.delete()
        os.remove(file_name)
        active_tickets.pop(self.ticket_owner.id, None)

def generate_html_log(messages, channel_name):
    html_content = """
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>{channel_name} - Discord Chat Log</title>
        <style>
            body {{
                background-color: #36393f;
                font-family: 'Arial', sans-serif;
                color: #dcddde;
                margin: 0;
                padding: 20px;
            }}
            .chat-log {{
                max-width: 800px;
                margin: 0 auto;
                border-radius: 5px;
                padding: 10px;
                background-color: #2f3136;
            }}
            .message {{
                display: flex;
                margin-bottom: 10px;
            }}
            .avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                margin-right: 10px;
                background-color: #40444b;
            }}
            .message-content {{
                background-color: #40444b;
                padding: 10px;
                border-radius: 5px;
                max-width: 600px;
                position: relative;
                display: flex;
                flex-direction: column;
            }}
            .message-content::before {{
                content: '';
                position: absolute;
                top: 10px;
                left: -8px;
                width: 0;
                height: 0;
                border-top: 6px solid transparent;
                border-bottom: 6px solid transparent;
                border-right: 8px solid #40444b;
            }}
            .username {{
                font-weight: bold;
                color: #ffffff;
            }}
            .timestamp {{
                margin-left: 10px;
                color: #72767d;
                font-size: 12px;
            }}
            .message-text {{
                margin-top: 5px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            .message-text code {{
                background-color: #2e2f32;
                color: #c3c5c7;
                padding: 2px 4px;
                border-radius: 3px;
            }}
            .message-text strong {{
                color: #ffffff;
            }}
            .message-text em {{
                color: #c3c5c7;
            }}
        </style>
    </head>
    <body>
        <div class="chat-log">
    """.format(channel_name=channel_name)
    for message in reversed(messages):
        html_content += """
        <div class="message">
            <img class="avatar" src="{avatar_url}" alt="User Avatar">
            <div class="message-content">
                <span class="username">{username}</span>
                <span class="timestamp">{timestamp}</span>
                <div class="message-text">{content}</div>
            </div>
        </div>
        """.format(
            avatar_url=message.author.avatar.url if message.author.avatar else 'https://cdn.discordapp.com/embed/avatars/0.png',
            username=message.author.name,
            timestamp=message.created_at.strftime('%b %d, %Y at %I:%M %p'),
            content=message.content
                .replace('\n', '<br>')
                .replace('**', '<strong>').replace('__', '<em>').replace('', '<code>').replace('</code>', '</code>').replace('</strong>', '</strong>').replace('</em>', '</em>')
        )
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name="refresh")
@commands.has_role(HELPER_ROLE_NAME)
async def refresh(ctx):
    await ctx.message.delete()
    if ctx.channel.id == INITIAL_MESSAGE_CHANNEL_ID:
        view = SelectView()
        await ctx.channel.send(
            embed=discord.Embed(
                title="Create a Ticket",
                description="Please choose one of the following options:",
                color=discord.Color.blue()
            ),
            view=view
        )

@bot.event
async def on_ready():
    channel = bot.get_channel(INITIAL_MESSAGE_CHANNEL_ID)
    if channel is None:
        print("Channel not found")
        return
    async for message in channel.history(limit=100):
        try:
            await message.delete()
        except discord.Forbidden:
            print("Bot does not have permission to delete messages.")
        except discord.HTTPException as e:
            print(f"Failed to delete message: {e}")
    embed = discord.Embed(title="Ticket System", description="Click the button below to create a ticket.")
    button = discord.ui.Button(label="Create Ticket", style=discord.ButtonStyle.primary)
    async def button_callback(interaction: discord.Interaction):
        if interaction.user.id in active_tickets:
            await interaction.response.send_message("You already have an active ticket.", ephemeral=True)
            return
        await interaction.response.send_message("Please select an option:", view=SelectView(), ephemeral=True)
    button.callback = button_callback
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    message = await channel.send(embed=embed, view=view)

@bot.command(name="prules")
async def prules(ctx):
    embed = discord.Embed(
        title="PayPal Payment Rules",
        description="""- **Send in EUR**: All payments should be made in Euros (€).\n
- **No Payment Notes**: Do not write anything in the 'Notes' section when sending a payment.\n
- **Use Balance**: Ensure payments are made from your PayPal balance, not from a linked card or bank account.\n
- **Send as F&F**: Payments should be sent as 'Friends & Family' to avoid fees and delays.\n
***By making a payment, you agree to these rules. Failure to adhere to them means no refunds and no service will be provided.***""",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name="notify")
@commands.has_role(HELPER_ROLE_NAME)
async def notify(ctx, ticket_owner: discord.User):
    ticket_url = ctx.message.jump_url
    try:
        await ticket_owner.send(f"Please check your ticket: {ticket_url}")
        await ctx.send(f"Notification sent to {ticket_owner.mention}.", delete_after=10)
    except discord.Forbidden:
        await ctx.send("Failed to send DM. The user might have DMs disabled.", delete_after=10)

@bot.command(name="close")
@commands.has_role(HELPER_ROLE_NAME)
async def close_ticket(ctx, ticket_owner: discord.User = None):
    if not (ctx.channel.name.startswith("buy") or ctx.channel.name.startswith("support")):
        await ctx.send("This command can only be used in channels that start with 'buy' or 'support'.")
        return
    if ticket_owner is None:
        try:
            user_id = int(ctx.channel.name.split('-')[1])
            ticket_owner = await bot.fetch_user(user_id)
        except (IndexError, ValueError):
            await ctx.send("Could not find the ticket owner. Please specify a user.")
            return
    messages = []
    async for message in ctx.channel.history(limit=None):
        messages.append(message)
    html_content = generate_html_log(messages, ctx.channel.name)
    file_name = f"{ctx.channel.name}_log.html"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(html_content)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if ticket_owner:
        try:
            await ticket_owner.send("Here is the log of your ticket:", file=discord.File(file_name))
        except discord.HTTPException:
            await ctx.send(f"Could not send a DM to {ticket_owner.name}. They might have DMs disabled.")
    await log_channel.send(f"Log for ticket {ctx.channel.name}:", file=discord.File(file_name))
    await ctx.channel.delete()
    os.remove(file_name)
    if ticket_owner:
        active_tickets.pop(ticket_owner.id, None)

bot.run(config.BOT_TOKEN)