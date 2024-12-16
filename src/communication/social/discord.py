# social/discord.py
import discord
from discord.ext import commands
from typing import Dict, List, Any
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentDiscordBot(commands.Bot):
    def __init__(
        self,
        command_prefix: str,
        ai_service: Any,  # Your AI service
        wallet_service: Any,  # Your wallet service
        intents: discord.Intents = discord.Intents.default(),
    ):
        # Enable necessary intents
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        # Services
        self.ai_service = ai_service
        self.wallet_service = wallet_service

        # State management
        self.active_conversations: Dict[int, List[Dict]] = {}
        self.command_cooldowns: Dict[int, datetime] = {}

        # Register commands
        self.setup_commands()

    async def setup_hook(self):
        """Setup hook for bot initialization"""
        logger.info("Bot is initializing...")

    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="the blockchain 🔍"
            )
        )

    def setup_commands(self):
        """Setup bot commands"""

        @self.command(name="help")
        async def help_command(ctx):
            """Show help information"""
            embed = discord.Embed(
                title="AGI Agent Commands",
                description="Here are the available commands:",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="💬 General",
                value="`!help` - Show this help message\n"
                "`!about` - Learn about the agent",
                inline=False,
            )
            embed.add_field(
                name="🤖 AI Interaction",
                value="`!ask <question>` - Ask the agent something\n"
                "`!analyze <topic>` - Get market analysis",
                inline=False,
            )
            embed.add_field(
                name="💰 Wallet",
                value="`!balance` - Check wallet balance\n"
                "`!price <token>` - Get token price",
                inline=False,
            )
            await ctx.send(embed=embed)

        @self.command(name="ask")
        async def ask_command(ctx, *, question: str):
            """Ask the agent a question"""
            async with ctx.typing():
                try:
                    response = await self.ai_service.generate_response(
                        {
                            "content": question,
                            "author": str(ctx.author),
                            "channel": str(ctx.channel),
                        }
                    )
                    await ctx.reply(response)
                except Exception as e:
                    logger.error(f"Error processing question: {e}")
                    await ctx.reply(
                        "Sorry, I encountered an error processing your question."
                    )

        @self.command(name="analyze")
        async def analyze_command(ctx, *, topic: str):
            """Analyze market or topic"""
            async with ctx.typing():
                try:
                    analysis = await self.ai_service.analyze_market(
                        {"topic": topic, "timestamp": datetime.now().isoformat()}
                    )

                    embed = discord.Embed(
                        title=f"Analysis: {topic}",
                        description=analysis["summary"],
                        color=discord.Color.green(),
                    )

                    for key, value in analysis["metrics"].items():
                        embed.add_field(name=key, value=value)

                    await ctx.send(embed=embed)
                except Exception as e:
                    logger.error(f"Error during analysis: {e}")
                    await ctx.reply("Sorry, I encountered an error during analysis.")

        @self.command(name="balance")
        async def balance_command(ctx):
            """Check wallet balance"""
            try:
                balance = await self.wallet_service.get_balance()

                embed = discord.Embed(
                    title="Wallet Balance", color=discord.Color.gold()
                )

                for token, amount in balance.items():
                    embed.add_field(name=token, value=f"{amount:.4f}")

                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Error getting balance: {e}")
                await ctx.reply("Sorry, I couldn't retrieve the balance.")

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore messages from self
        if message.author == self.user:
            return

        # Process commands
        await self.process_commands(message)

        # Handle mentions
        if self.user in message.mentions:
            async with message.channel.typing():
                try:
                    response = await self.ai_service.generate_response(
                        {
                            "content": message.content,
                            "author": str(message.author),
                            "channel": str(message.channel),
                        }
                    )
                    await message.reply(response)
                except Exception as e:
                    logger.error(f"Error processing mention: {e}")
                    await message.reply("Sorry, I encountered an error.")

    async def on_member_join(self, member: discord.Member):
        """Welcome new members"""
        welcome_channel = member.guild.system_channel
        if welcome_channel:
            embed = discord.Embed(
                title="Welcome!",
                description=f"Welcome {member.mention} to the server! 👋\n"
                f"Use `!help` to see what I can do!",
                color=discord.Color.green(),
            )
            await welcome_channel.send(embed=embed)

    async def track_analytics(self):
        """Track bot analytics"""
        while True:
            try:
                for guild in self.guilds:
                    logger.info(f"Guild {guild.name}: {len(guild.members)} members")
                    # Add your analytics tracking here
            except Exception as e:
                logger.error(f"Error tracking analytics: {e}")
            await asyncio.sleep(3600)  # Track every hour

    def run_bot(self, token: str):
        """Run the bot"""
        self.loop.create_task(self.track_analytics())
        self.run(token)


class DiscordService:
    """Discord service wrapper"""

    def __init__(
        self, token: str, command_prefix: str, ai_service: Any, wallet_service: Any
    ):
        self.token = token
        self.bot = AgentDiscordBot(
            command_prefix=command_prefix,
            ai_service=ai_service,
            wallet_service=wallet_service,
        )

    def start(self):
        """Start the Discord bot"""
        self.bot.run_bot(self.token)

    async def send_message(self, channel_id: int, content: str):
        """Send message to specific channel"""
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(content)
