"""
Message Handler Interface - A standard interface wrapper to eliminate duplicated logic
in Discord bot message processing.
"""

import discord
import random
import asyncio
from typing import List, Union, Callable, Optional
from enum import Enum


class MatchType(Enum):
    """Defines different types of message matching strategies"""
    EXACT = "exact"           # Exact string match
    CONTAINS = "contains"     # String contains keyword
    ANY_IN = "any_in"         # Any of the keywords in message
    CUSTOM = "custom"         # Custom matching function


class ResponseType(Enum):
    """Defines different types of responses"""
    FILE = "file"             # Send a file (image/gif)
    TEXT = "text"             # Send text message
    RANDOM_FILE = "random_file"   # Send random file from list
    CUSTOM = "custom"         # Custom response function
    ANIMATION = "animation"   # Special text animation


class MessageRule:
    """Represents a single message handling rule"""
    
    def __init__(
        self,
        name: str,
        match_type: MatchType,
        keywords: Union[str, List[str], Callable],
        response_type: ResponseType,
        response_data: Union[str, List[str], Callable],
        priority: int = 0,
        condition: Optional[Callable] = None
    ):
        self.name = name
        self.match_type = match_type
        self.keywords = keywords
        self.response_type = response_type
        self.response_data = response_data
        self.priority = priority
        self.condition = condition  # Additional condition function
    
    def matches(self, content: str, message: discord.Message) -> bool:
        """Check if this rule matches the message content"""
        
        # Check additional condition if provided
        if self.condition and not self.condition(message):
            return False
        
        match self.match_type:
            case MatchType.EXACT:
                if isinstance(self.keywords, list):
                    return content in self.keywords
                else:
                    return content == self.keywords
            case MatchType.CONTAINS:
                if isinstance(self.keywords, list):
                    return any(keyword in content for keyword in self.keywords)
                else:
                    return self.keywords in content
            case MatchType.ANY_IN:
                if isinstance(self.keywords, list):
                    return any(word in content for word in self.keywords)
                else:
                    return self.keywords in content
            case MatchType.CUSTOM:
                if callable(self.keywords):
                    return self.keywords(content, message)
                else:
                    raise ValueError("Custom match type requires callable function")
        
        return False
    
    async def execute_response(self, message: discord.Message, **kwargs) -> bool:
        """Execute the response for this rule. Returns True if message was handled."""
        
        match self.response_type:
            case ResponseType.FILE:
                file_path = kwargs.get('img_path', '') + self.response_data
                await message.channel.send(file=discord.File(file_path))
                return True
            case ResponseType.TEXT:
                await message.channel.send(self.response_data)
                return True
            case ResponseType.RANDOM_FILE:
                if isinstance(self.response_data, list):
                    chosen_file = random.choice(self.response_data)
                    file_path = kwargs.get('img_path', '') + chosen_file
                    await message.channel.send(file=discord.File(file_path))
                    return True
                else:
                    raise ValueError("Random file response requires list of files")
            case ResponseType.CUSTOM:
                if callable(self.response_data):
                    return await self.response_data(message, **kwargs)
                else:
                    raise ValueError("Custom response type requires callable function")
            case ResponseType.ANIMATION:
                if callable(self.response_data):
                    await self.response_data(message)
                    return True
                else:
                    raise ValueError("Animation response type requires callable function")
        
        return False


class MessageHandler:
    """Main message handler that processes rules and manages responses"""
    
    def __init__(self, img_path_func: Callable = None):
        self.rules: List[MessageRule] = []
        self.img_path_func = img_path_func or (lambda: "")
    
    def add_rule(self, rule: MessageRule):
        """Add a rule to the handler"""
        self.rules.append(rule)
        # Sort by priority (higher priority first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def add_simple_file_rule(
        self, 
        name: str, 
        keywords: Union[str, List[str]], 
        filename: str, 
        match_type: MatchType = MatchType.CONTAINS,
        priority: int = 0
    ):
        """Convenience method to add a simple file response rule"""
        rule = MessageRule(
            name=name,
            match_type=match_type,
            keywords=keywords,
            response_type=ResponseType.FILE,
            response_data=filename,
            priority=priority
        )
        self.add_rule(rule)
    
    def add_random_file_rule(
        self, 
        name: str, 
        keywords: Union[str, List[str]], 
        filenames: List[str], 
        match_type: MatchType = MatchType.EXACT,
        priority: int = 0
    ):
        """Convenience method to add a random file response rule"""
        rule = MessageRule(
            name=name,
            match_type=match_type,
            keywords=keywords,
            response_type=ResponseType.RANDOM_FILE,
            response_data=filenames,
            priority=priority
        )
        self.add_rule(rule)
    
    def add_text_rule(
        self, 
        name: str, 
        keywords: Union[str, List[str]], 
        text: str, 
        match_type: MatchType = MatchType.EXACT,
        priority: int = 0
    ):
        """Convenience method to add a text response rule"""
        rule = MessageRule(
            name=name,
            match_type=match_type,
            keywords=keywords,
            response_type=ResponseType.TEXT,
            response_data=text,
            priority=priority
        )
        self.add_rule(rule)
    
    async def handle_message(self, message: discord.Message) -> bool:
        """Process a message through all rules. Returns True if message was handled."""
        
        if message.author.bot:  # Ignore bot messages
            return False
        
        content = message.content
        
        for rule in self.rules:
            if rule.matches(content, message):
                handled = await rule.execute_response(
                    message, 
                    img_path=self.img_path_func()
                )
                if handled:
                    return True
        
        return False
    
    def remove_rule(self, name: str):
        """Remove a rule by name"""
        self.rules = [rule for rule in self.rules if rule.name != name]
    
    def list_rules(self) -> List[str]:
        """Get list of all rule names"""
        return [rule.name for rule in self.rules]


# Custom response functions for complex behaviors
async def deepseek_animation(message: discord.Message):
    """Custom animation for deepseek mode"""
    sent = await message.channel.send("思")
    await asyncio.sleep(0.02)
    sent = await sent.edit(content="思考")
    await asyncio.sleep(0.02)
    sent = await sent.edit(content="思考中")
    await asyncio.sleep(0.02)
    sent = await sent.edit(content="思考中.")
    await asyncio.sleep(0.02)
    sent = await sent.edit(content="思考中..")
    await asyncio.sleep(0.02)
    sent = await sent.edit(content="思考中...")
    await asyncio.sleep(5)
    await message.channel.send("服务器繁忙，请稍后再试")


async def go_response(message: discord.Message, **kwargs):
    """Custom response for 'go' messages"""
    # Access to global isGo variable would be passed through kwargs
    is_go = kwargs.get('is_go', True)
    if is_go:
        await message.channel.send("還在Go 還在Go")
        img_path = kwargs.get('img_path', '')
        await message.channel.send(file=discord.File(img_path + "我也一樣.jpg"))
    return True


def mention_condition(message: discord.Message) -> bool:
    """Condition function to check if bot is mentioned"""
    # This would need access to the client instance
    # Can be passed through kwargs or set up differently
    return True  # Placeholder


def create_mention_matcher(client, nicknames: List[str]) -> Callable:
    """Factory function to create mention matcher"""
    def matcher(content: str, message: discord.Message) -> bool:
        return (client.user in message.mentions or 
                any(word in content for word in nicknames))
    return matcher
