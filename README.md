<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="./.docs/NoneBotPlugin.svg" width="300" alt="logo"></a>
</div>

<div align="center">

# nonebot-plugin-emojilike-automonkey

_✨ NoneBot onebotV11 贴猴插件，Fork form fllesser/nonebot-plugin-emojilike，Powered by Deepseek-R1 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/fllesser/nonebot-plugin-emojilike.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-emojilike">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-emojilike.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>


## 📖 介绍

NoneBot onebotV11 贴猴插件，Fork form fllesser/nonebot-plugin-emojilike，Powered by Deepseek-R1  
配置好.env文件中的配置项后可以实现对特定QQ用户的包含特定关键词的信息进行贴猴，妈妈再也不用担心我的腱鞘炎了

## 💿 安装

<details open>
<summary>pip</summary>

    pip install --upgrade nonebot-plugin-emojilike-automonkey
</details>

<details close>

<summary>若你有大量插件依赖于 Pydantic V1 </summary>

    pip install --upgrade nonebot-plugin-emojilike-automonkey==12.0.0
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_emojilike_automonkey"]

</details>


## 🎉 使用
### .env中的配置项
| 配置项 | 注释 |
|:------------------------:|:-------------------------:|
| automonkey_users | 被贴猴的用户 |
示例:
automonkey_users=["12345678", "12345679"]

### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 赞我 | 群员 | 否 | 群聊 | 顾名思义 |
| 天天赞我 | 群员 | 否 | 群聊 | 顾名思义 |
| 给我贴猴 | 群员 | 否 | 群聊 | 顾名思义 |
| 开启/关闭自动贴猴 | SUPERUSER | 否 | 群聊 | 顾名思义 |
| 开启/关闭用户检测 | 群员 | 否 | 群聊 | 顾名思义 |
| 开启/关闭贴猴关键词检测 | 群员 | 否 | 群聊 | 顾名思义 |
| 增加/删除贴猴关键词+空格+关键词 | 群员 | 否 | 群聊 | 顾名思义 |
| 列出当前贴猴关键词 | 群员 | 否 | 群聊 | 顾名思义 |
| 贴猴菜单 | 群员 | 否 | 群聊 | 顾名思义 |

## 效果图
<img src=".docs/1.png">
<img src=".docs/2.png">
<img src=".docs/3.png">
