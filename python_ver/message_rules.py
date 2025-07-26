"""
Message rules configuration for Discord bot
"""

import asyncio
import os
from config import ALLOW_GO_SERVER
from message_handler import (
    MessageHandler,
    MessageRule,
    MatchType,
    ResponseType,
)
import random
import discord


def setup_message_handler(client, img_path_func):
    """Set up the message handler with all the rules"""

    handler = MessageHandler(img_path_func)

    # Rule for "一輩子" or "一世" - random between two images
    handler.add_random_file_rule(
        name="lifetime",
        keywords=["一輩子", "一世"],
        filenames=["畢竟這是一輩子的事.jpg", "是一輩子喔_一輩子.jpg"],
        match_type=MatchType.CONTAINS,
        priority=10,
    )

    # Rule for negative keywords - random between two images
    negative_keywords = ["不行", "不能", "不可以", "不要", "不想", "dame", "だめ"]
    negative_exact = ["No", "no", "NO", "Not", "not", "NOT"]

    # Custom function for negative responses
    async def negative_response(message: discord.Message, **kwargs):
        imgs = ["不行.jpg", "不可以-BiaRmwz4.webp"]
        chosen_img = random.choice(imgs)
        img_path = kwargs.get("img_path", "")
        await message.channel.send(file=discord.File(os.path.join(img_path, chosen_img)))
        return True

    # Add rule for negative words in content
    handler.add_rule(
        MessageRule(
            name="negative_contains",
            match_type=MatchType.ANY_IN,
            keywords=negative_keywords,
            response_type=ResponseType.CUSTOM,
            response_data=negative_response,
            priority=9,
        )
    )

    # Add rule for exact negative matches
    handler.add_rule(
        MessageRule(
            name="negative_exact",
            match_type=MatchType.EXACT,
            keywords=negative_exact,
            response_type=ResponseType.CUSTOM,
            response_data=negative_response,
            priority=9,
        )
    )

    # Rule for "春日影"
    async def kasuga_response(message: discord.Message, **kwargs):
        img_path = kwargs.get("img_path", "")
        await message.channel.send(
            file=discord.File(os.path.join(img_path, "為什麼要演奏春日影.jpg"))
        )
        # Process commands if message starts with "!"
        if message.content.startswith("!"):
            await client.process_commands(message)
        return True

    handler.add_rule(
        MessageRule(
            name="kasuga",
            match_type=MatchType.CONTAINS,
            keywords="春日影",
            response_type=ResponseType.CUSTOM,
            response_data=kasuga_response,
            priority=8,
        )
    )

    # Rule for "go" variants - custom response with condition
    async def go_custom_response(message: discord.Message, **kwargs):
        if message.guild in ALLOW_GO_SERVER:
            await message.channel.send("還在Go 還在Go")
            img_path = kwargs.get("img_path", "")
            await message.channel.send(file=discord.File(os.path.join(img_path + "我也一樣.jpg")))
        return True

    handler.add_rule(
        MessageRule(
            name="go",
            match_type=MatchType.EXACT,
            keywords=["go", "Go", "GO", "gO", "去"],
            response_type=ResponseType.CUSTOM,
            response_data=go_custom_response,
            priority=7,
        )
    )

    # Rule for "Me too" variants
    handler.add_simple_file_rule(
        name="me_too",
        keywords=[
            "Me too",
            "me too",
            "我也是",
            "我也是啊",
            "我也一樣",
            "我也是呀",
            "me2",
        ],
        filename="我也一樣.jpg",
        match_type=MatchType.ANY_IN,
        priority=6,
    )

    # Rule for "Mujica" variants
    handler.add_simple_file_rule(
        name="mujica",
        keywords=["Mujica", "mujica", "ムヒカ", "穆希卡", "ミュヒカ", "母鷄卡"],
        filename="現在正是復權的時刻.jpg",
        match_type=MatchType.ANY_IN,
        priority=5,
    )

    # Rule for health-related messages
    health_keywords = [
        "對健康不好",
        "不健康",
        "不健康的",
        "對健康不好啊",
        "對健康不好嗎",
        "不健康嗎",
        "不健康的嗎",
        "對健康不好喔",
        "對健康不好啊喔",
        "對健康不好啊喔嗎",
    ]
    health_images = [
        "對健康不好喔_2-Cmch--Fa.webp",
        "對健康不好喔_3-Cpm4dn3P.webp",
        "對健康不好喔-D9lhW0Ao.webp",
    ]

    handler.add_random_file_rule(
        name="health",
        keywords=health_keywords,
        filenames=health_images,
        match_type=MatchType.EXACT,
        priority=4,
    )

    # Rule for Togawa Group
    togawa_keywords = [
        "豐川集團",
        "TGW",
        "Togawa Group",
        "TGWG",
        "Togawa",
        "豐川集團TGW",
        "豐川集團TGWG",
        "豐川集團Togawa Group",
    ]

    handler.add_simple_file_rule(
        name="togawa",
        keywords=togawa_keywords,
        filename="豐川集團.gif",
        match_type=MatchType.EXACT,
        priority=3,
    )

    # Rule for bot mentions and nicknames
    soyo_nicknames = [
        "Soyo",
        "soyo",
        "そよ",
        "長崎そよ",
        "長崎爽世",
        "そよちゃん",
        "爽世",
        "素世",
        "長崎素世",
    ]

    def mention_matcher(content: str, message: discord.Message) -> bool:
        return client.user in message.mentions or any(
            word in content for word in soyo_nicknames
        )

    handler.add_rule(
        MessageRule(
            name="mentions",
            match_type=MatchType.CUSTOM,
            keywords=mention_matcher,
            response_type=ResponseType.IMAGE,
            response_data="幹嘛-CStDUUrz.webp",
            priority=2,
        )
    )

    async def deepseek_animation(message: discord.Message):
        """Custom animation for deepseek mode"""
        frames = [
            ("思", 0.02),
            ("思考", 0.02),
            ("思考中", 0.02),
            ("思考中.", 0.02),
            ("思考中..", 0.02),
            ("思考中...", 0.02)
        ]
        
        sent = await message.channel.send(frames[0][0])
        for content, delay in frames[1:]:
            sent = await sent.edit(content=content)
            await asyncio.sleep(delay)
        
        await asyncio.sleep(5)
        await message.channel.send("服务器繁忙，请稍后再试")

    # Rule for deepseek mode - special animation
    handler.add_rule(
        MessageRule(
            name="deepseek",
            match_type=MatchType.EXACT,
            keywords="!deepseek_mode",
            response_type=ResponseType.ANIMATION,
            response_data=deepseek_animation,
            priority=1,
        )
    )

    return handler
