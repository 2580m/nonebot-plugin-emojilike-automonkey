import json
import emoji
import re

from nonebot import logger, require, get_driver, get_bots
from nonebot import get_plugin_config
from .config import Config
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import (
    on_command,
    on_message,
)
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP

require("nonebot_plugin_localstore")
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa: E402
import nonebot_plugin_localstore as store  # noqa: E402
from typing import Set, List
from .config import Config

automonkey_keys_file = "automonkey_keys.json"

#driver = get_driver()

#plugin_config = get_plugin_config(Config)

try:
    plugin_config = get_plugin_config(Config)
except ImportError:
    plugin_config = Config.parse_obj(get_driver().config)

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-emojilike-automonkey",
    description="nonebot2 贴猴插件",
    usage="""
    在.env文件中添加以下配置项:
    automonkey_users:List[str]监测的用户
    automonkey_groups:List[str]监测的群聊
    输入"<COMMANDSTART>贴猴菜单"查看具体使用方式
    """,
    config=Config,
    type="application",
    homepage="https://github.com/2580m/nonebot-plugin-emojilike-automonkey",
    supported_adapters={"~onebot.v11"},
)

automonkey_users: List[str] = plugin_config.automonkey_users
#automonkey_users = set(automonkey_users)
automonkey_groups: List[str] = plugin_config.automonkey_groups  

#automonkey_keys: List[str] = driver.config.automonkey_keys


class AutoMonkeyState:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.enabled = True           # 总开关
            cls._instance.key_check_enabled = False # 关键词检测开关
            cls._instance.user_check_enabled = True # 新增用户检测开关
            cls._instance.group_check_enabled = True  # 新增群聊检测开关
        return cls._instance
    
    def enable(self):
        self.enabled = True
    
    def disable(self):
        self.enabled = False

# 全局访问点
state = AutoMonkeyState()

groupcheck_cmd = on_command(
    "贴猴群聊检测", 
    aliases={"开启贴猴群聊检测", "关闭贴猴群聊检测"}, 
    permission=GROUP,
)

@groupcheck_cmd.handle()
async def handle_groupcheck_toggle(bot: Bot, event: GroupMessageEvent):
    cmd = event.get_plaintext().strip()
    
    if "开启" in cmd:
        state.group_check_enabled = True
        msg = "👥 已启用群聊检测（仅监控指定群组）"
    elif "关闭" in cmd:
        state.group_check_enabled = False
        msg = "🌐 已禁用群聊检测（监控所有群组）"
    
    await bot.send(event, msg)
    logger.info(f"群聊检测状态变更为：{state.group_check_enabled}")

toggle_monkey = on_command(
    cmd="自动贴猴", 
    aliases={"开启自动贴猴", "关闭自动贴猴"}, 
    permission=SUPERUSER, 
    #rule=to_me()
)

@toggle_monkey.handle()
async def handle_toggle(bot: Bot, event: GroupMessageEvent):
    cmd = event.get_plaintext().strip()
    if "开启" in cmd:
        state.enable()
        msg = "✅ 自动贴猴功能已启用"
    elif "关闭" in cmd:
        state.disable()
        msg = "⛔ 自动贴猴功能已禁用"
    
    await bot.send(event, msg)
    logger.info(f"管理员 {event.user_id} 修改自动贴猴状态为：{'启用' if state.enabled else '禁用'}")

keycheck_cmd = on_command(
    "贴猴关键词检测", 
    aliases={"开启贴猴关键词检测", "关闭贴猴关键词检测"}, 
    permission=GROUP,
    #rule=to_me()
)

@keycheck_cmd.handle()
async def handle_keycheck_toggle(bot: Bot, event: GroupMessageEvent):
    cmd = event.get_plaintext().strip()
    
    if "开启" in cmd:
        state.key_check_enabled = True
        msg = "✅ 已启用关键词检测（仅当消息含关键词时贴猴）"
    elif "关闭" in cmd:
        state.key_check_enabled = False
        msg = "🛑 已禁用关键词检测（所有消息均贴猴）"
    
    await bot.send(event, msg)
    logger.info(f"关键词检测状态变更为：{state.key_check_enabled}")

usercheck_cmd = on_command(
    "贴猴用户检测", 
    aliases={"开启贴猴用户检测", "关闭贴猴用户检测"}, 
    permission=GROUP,
    #rule=to_me()
)

@usercheck_cmd.handle()
async def handle_usercheck_toggle(bot: Bot, event: GroupMessageEvent):
    cmd = event.get_plaintext().strip()
    
    if "开启" in cmd:
        state.user_check_enabled = True
        msg = "🔍 已启用用户检测（仅监控名单用户）"
    elif "关闭" in cmd:
        state.user_check_enabled = False
        msg = "👁️ 已禁用用户检测（监控所有用户）"
    
    await bot.send(event, msg)
    logger.info(f"用户检测状态：{state.user_check_enabled}")

def normalize_text(text: str) -> str:
    """标准化文本：将英文字母转为小写，保留中文及特殊符号"""
    return re.sub(
        r'[A-Za-z]+', 
        lambda x: x.group().lower(), 
        text
    )

def load_automonkey_keys() -> Set[str]:
    """从本地存储加载关键词"""
    data_file = store.get_plugin_data_file(automonkey_keys_file)
    if not data_file.exists():
        data_file.write_text(json.dumps([]))
    return set(json.loads(data_file.read_text()))

def save_automonkey_keys(keys: Set[str]):
    """保存关键词到本地存储"""
    #data_file = store.get_plugin_data_file(automonkey_keys_file)
    data_file.write_text(json.dumps(list(keys)))

# 预处理关键词（保留中文，英文转小写）
automonkey_keys = load_automonkey_keys()
processed_keys = {normalize_text(key) for key in automonkey_keys}

async def check_automonkey_condition(event: GroupMessageEvent) -> bool:
    # 全局开关检查
    if not state.enabled:
        return False
    
     # 新增群聊检测逻辑
    if state.group_check_enabled:
        if str(event.group_id) not in automonkey_groups:
            return False
    
    # 基础条件校验
    # 用户检测逻辑
#    if state.user_check_enabled:
#        # 当启用用户检测时检查白名单
#        if not (
#            str(event.user_id) in driver.config.automonkey_users
#            and event.user_id != event.self_id
#            and isinstance(event, GroupMessageEvent)
#        ):
#            return False

    # 用户检测逻辑
    if state.user_check_enabled:
        # 当启用用户检测时检查白名单
        if str(event.user_id) not in plugin_config.automonkey_users:
            return False
    
    # 机器人自身消息过滤（始终生效）
    if event.user_id == event.self_id:
        return False
    
# 关键词检测开关逻辑
    if state.key_check_enabled:
        try:
            raw_msg = event.get_plaintext().strip()
            normalized_msg = normalize_text(raw_msg)
            #processed_keys = {normalize_text(key) for key in driver.config.automonkey_keys}
            return any(k in normalized_msg for k in processed_keys)
        except Exception as e:
            logger.error(f"关键词检测失败：{str(e)}")
            return False
    else:
        # 关闭检测时直接通过
        return True

automonkey_matcher = on_message(
    rule=Rule(check_automonkey_condition),
    priority=10,
    block=False
)


@automonkey_matcher.handle()
async def handle_automonkey(bot: Bot, event: GroupMessageEvent):
    try:
        await bot.call_api(
            "set_msg_emoji_like",
            message_id=event.message_id,
            emoji_id="128053"
        )
        logger.info(f"已为 {event.user_id} 的合规消息添加贴猴表情")
    except Exception as e:
        logger.error(f"自动贴猴失败 | 用户：{event.user_id} | 错误：{str(e)}")


def contain_face(event: GroupMessageEvent) -> bool:
    msg = event.get_message()
    return any(seg.type == "face" for seg in msg) or any(
        char in emoji.EMOJI_DATA for char in msg.extract_plain_text().strip()
    )


#@on_message(
#    rule=Rule(contain_face), permission=GROUP, block=False, priority=999
#).handle()
#async def _(bot: Bot, event: GroupMessageEvent):
#    msg = event.get_message()
#    msg_emoji_id_set: set[int] = {
#        int(seg.data["id"]) for seg in msg if seg.type == "face"
#    } | {
#        ord(char)
#        for char in msg.extract_plain_text().strip()
#        if char in emoji.EMOJI_DATA
#    }
#    for id in msg_emoji_id_set:
#        if id in emoji_like_id_set:
#            await bot.call_api(
#                "set_msg_emoji_like", message_id=event.message_id, emoji_id=id
#            )


#like_monkey = on_message(
#    rule= keyword('贴猴') & Rule(is_reply),
#    priority=1,
#    permission=permission.GROUP
#)

#@like_monkey.handle()

# 定义触发规则：纯文本消息为"贴猴"且存在被回复消息
async def check_reply_taohou(event: MessageEvent) -> bool:
    return (
        event.get_plaintext().strip() == "贴猴"  # 消息内容校验
        and event.reply is not None  # 存在回复对象
    )

# 创建消息处理器
taohou_matcher = on_message(
    rule=Rule(check_reply_taohou),
    priority=10,
    block=True
)

@taohou_matcher.handle()
async def handle_taohou(bot: Bot, event: GroupMessageEvent):
    try:
        # 获取被回复消息的ID
        replied_msg_id = event.reply.message_id
        
        # 调用API添加表情
        await bot.call_api(
            "set_msg_emoji_like",  # OneBot协议标准API
            message_id=replied_msg_id,
            emoji_id="128053"      # 目标表情ID
        )
        
        # 可选：发送操作反馈
        #await bot.send(event, "表情贴附成功 🐵")
        
    except Exception as e:
        # 异常处理（日志记录+用户提示）
        await bot.send(event, f"操作失败: {str(e)}")



@on_command(cmd="赞我", aliases={"草我"}, permission=GROUP).handle()
async def _(bot: Bot, event: GroupMessageEvent):    
    id_set = {"76", "66", "63", "201", "10024"}
    try:
        for _ in range(1):
            await bot.send_like(user_id=event.user_id, times=10)
            await bot.call_api(
                "set_msg_emoji_like", message_id=event.message_id, emoji_id=id_set.pop()
            )
    except Exception as _:
        await bot.call_api(
            "set_msg_emoji_like", message_id=event.message_id, emoji_id="39"
        )


@on_command(cmd="给我贴猴", permission=GROUP).handle()
async def _(bot: Bot, event: GroupMessageEvent):    
    id_set = {"128053"}
    try:
        for _ in range(1):
            await bot.send_like(user_id=event.user_id, times=10)
            await bot.call_api(
                "set_msg_emoji_like", message_id=event.message_id, emoji_id=id_set.pop()
            )
    except Exception as _:
        await bot.call_api(
            "set_msg_emoji_like", message_id=event.message_id, emoji_id="128053"
        )


sub_like_set: set[int] = {1}
sub_list_file = "sub_list.json"


@get_driver().on_startup
async def _():
    data_file = store.get_plugin_data_file(sub_list_file)
    if not data_file.exists():
        data_file.write_text(json.dumps([]))
    global sub_like_set
    sub_like_set = set(json.loads(data_file.read_text()))
    logger.info(f"每日赞列表: [{','.join(map(str, sub_like_set))}]")


@on_command(cmd="天天赞我", aliases={"天天草我"}, permission=GROUP).handle()
async def _(bot: Bot, event: MessageEvent):
    sub_like_set.add(event.user_id)
    #data_file = store.get_plugin_data_file(sub_list_file)
    data_file.write_text(json.dumps(list(sub_like_set)))
    await bot.call_api(
        "set_msg_emoji_like", message_id=event.message_id, emoji_id="424"
    )

manage_key_cmd = on_command(
    "贴猴关键词", 
    aliases={"添加贴猴关键词", "删除贴猴关键词"}, 
    permission=GROUP,
    #rule=to_me()
)

@manage_key_cmd.handle()
async def handle_manage_key(bot: Bot, event: MessageEvent):
    cmd = event.get_plaintext().split()
    if len(cmd) < 2:
        await bot.send(event, "格式错误，请使用：添加贴猴关键词/删除贴猴关键词 [关键词]")
        return

    action = cmd[0]
    key = " ".join(cmd[1:])
    
    global automonkey_keys, processed_keys
    
    if action == "添加贴猴关键词":
        if key in automonkey_keys:
            await bot.send(event, f"⚠️ 关键词 [{key}] 已存在")
            return
        automonkey_keys.add(key)
        processed_keys.add(normalize_text(key))
        save_automonkey_keys(automonkey_keys)
        await bot.send(event, f"✅ 已添加关键词 [{key}]")
        logger.info(f"管理员添加贴猴关键词: {key}")

    elif action == "删除贴猴关键词":
        if key not in automonkey_keys:
            await bot.send(event, f"⚠️ 关键词 [{key}] 不存在")
            return
        automonkey_keys.remove(key)
        processed_keys = {normalize_text(k) for k in automonkey_keys}
        save_automonkey_keys(automonkey_keys)
        await bot.send(event, f"🗑️ 已删除关键词 [{key}]")
        logger.info(f"管理员删除贴猴关键词: {key}")

    else:
        await bot.send(event, "❌ 未知操作，支持命令：添加贴猴关键词/删除贴猴关键词")

list_automonkey_keys_cmd = on_command(
    cmd = "列出当前贴猴关键词",
    permission=GROUP,
)

@list_automonkey_keys_cmd.handle()
async def handle_list_automonkey_keys(bot: Bot, event: GroupMessageEvent):
    
    # 构建菜单消息
    list_automonkey_keys_msg = f"""
当前监控关键词：{', '.join(automonkey_keys) or "无"}
    """.strip()

    await bot.send(event, list_automonkey_keys_msg)

menu_cmd = on_command(
    cmd="贴猴菜单", 
    permission=GROUP,
    #rule=to_me()
)

@menu_cmd.handle()
async def handle_menu(bot: Bot, event: GroupMessageEvent):
    # 获取当前状态
    status_total = "✅ 开启" if state.enabled else "⛔ 关闭"
    status_user = "🔍 开启" if state.user_check_enabled else "👁️ 关闭"
    status_key = "📖 开启" if state.key_check_enabled else "📭 关闭"
    status_group = "👥 开启" if state.group_check_enabled else "🌐 关闭"
    
    # 构建菜单消息
    menu_msg = f"""
【自动贴猴系统菜单】
━━━━━━━━━━━━━━
{status_total} - 总开关
  权限：SUPERUSER
  开启命令：开启自动贴猴
  关闭命令：关闭自动贴猴

{status_user} - 用户检测
  权限：群聊
  开启命令：开启贴猴用户检测
  关闭命令：关闭贴猴用户检测
  → 当前模式：{"仅监控名单用户" if state.user_check_enabled else "监控所有用户"}

{status_key} - 关键词检测
  权限：群聊
  开启命令：开启贴猴关键词检测
  关闭命令：关闭贴猴关键词检测
  → 当前模式：{"需触发关键词" if state.key_check_enabled else "任意消息均触发"}

{status_group} - 群聊检测
  权限：群聊
  开启命令：开启贴猴群聊检测
  关闭命令：关闭贴猴群聊检测
  → 当前模式：{"仅监控指定群组" if state.group_check_enabled else "监控所有群组"}

🐵🐵 - 调整贴猴关键词
  权限：群聊
  增加命令：增加贴猴关键词+空格+关键词
  删除命令：删除贴猴关键词+空格+关键词
  查看命令：列出当前贴猴关键词
━━━━━━━━━━━━━━
当前贴猴名单用户：{', '.join(plugin_config.automonkey_users) or "无"}
当前贴猴群组：{', '.join(plugin_config.automonkey_groups) or "无"}
    """.strip()

    await bot.send(event, menu_msg)
    #logger.info(f"管理员 {event.user_id} 查看了系统菜单")

@scheduler.scheduled_job("cron", hour=8, minute=0, id="sub_card_like")
async def _():
    # 取 instance Bot
    bots = [bot for bot in get_bots().values() if isinstance(bot, Bot)]
    if not bots:
        return
    for bot in bots:
        for user_id in sub_like_set:
            try:
                for _ in range(5):
                    await bot.send_like(user_id=user_id, times=10)
            except Exception:
                continue

