app_id = "cli_a83fafd0aa14d013"
app_secret = "dy637jNB8N4v7bBbeHNA0eZveXizuZxH"

import requests
import logging
import time
import json
from feishu_api import FeishuAPI

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



# 示例用法
if __name__ == "__main__":
    try:
        # 创建飞书API客户端
        feishu_api = FeishuAPI(app_id=app_id, app_secret=app_secret)

        # 示例1: 获取部门信息（替换为实际的部门ID）
        # department_id = "od-64242a18099d3a31acd24d8fce8dxxxx"
        # department_info = feishu_api.get_department_info(department_id=department_id)
        # print("部门信息:", department_info)

        # 示例2: 批量获取用户ID
        emails = []
        mobiles = ["15810260321"]

        # 调用批量获取用户ID的方法
        user_ids_info = feishu_api.batch_get_user_id(
            emails=emails,
            mobiles=mobiles,
            include_resigned=True,
            user_id_type="open_id",
        )
        print("批量获取的用户ID信息:", user_ids_info)

    except Exception as e:
        print(f"执行出错: {str(e)}")

    # 定义示例卡片数据
    demo_dict = {
        "schema": "2.0",
        "config": {"update_multi": True},
        "body": {
            "direction": "vertical",
            "elements": [
                {
                    "tag": "markdown",
                    "content": "**请选择邮件类型查看详情**",
                    "text_align": "left",
                    "margin": "0px 0px 0px 0px",
                },
                {
                    "tag": "column_set",
                    "flex_mode": "stretch",
                    "horizontal_align": "left",
                    "columns": [],
                    "margin": "0px 0px 0px 0px",
                },
                {
                    "tag": "column_set",
                    "flex_mode": "stretch",
                    "horizontal_spacing": "8px",
                    "horizontal_align": "left",
                    "columns": [
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "审批 (1)",
                                    },
                                    "type": "primary_filled",
                                    "width": "default",
                                    "behaviors": [
                                        {
                                            "type": "callback",
                                            "value": {"action": "view_approval"},
                                        }
                                    ],
                                    "margin": "4px 0px 4px 0px",
                                }
                            ],
                            "vertical_spacing": "8px",
                            "horizontal_align": "left",
                            "vertical_align": "top",
                        },
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "关注 (3)",
                                    },
                                    "type": "default",
                                    "width": "default",
                                    "behaviors": [
                                        {
                                            "type": "callback",
                                            "value": {"action": "view_follow"},
                                        }
                                    ],
                                    "margin": "4px 0px 4px 0px",
                                }
                            ],
                            "vertical_spacing": "8px",
                            "horizontal_align": "left",
                            "vertical_align": "top",
                        },
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "不处理 (1)",
                                    },
                                    "type": "default",
                                    "width": "default",
                                    "behaviors": [
                                        {
                                            "type": "callback",
                                            "value": {"action": "view_ignore"},
                                        }
                                    ],
                                    "margin": "4px 0px 4px 0px",
                                }
                            ],
                            "vertical_spacing": "8px",
                            "horizontal_align": "left",
                            "vertical_align": "top",
                        },
                    ],
                    "margin": "0px 0px 0px 0px",
                },
                {"tag": "hr", "margin": "0px 0px 0px 0px"},
                {
                    "tag": "form",
                    "elements": [
                        {
                            "tag": "column_set",
                            "horizontal_align": "left",
                            "columns": [
                                {
                                    "tag": "column",
                                    "width": "auto",
                                    "elements": [
                                        {
                                            "tag": "column_set",
                                            "flex_mode": "stretch",
                                            "background_style": "blue-50",
                                            "horizontal_align": "left",
                                            "columns": [
                                                {
                                                    "tag": "column",
                                                    "width": "weighted",
                                                    "elements": [
                                                        {
                                                            "tag": "markdown",
                                                            "content": "**<font color='blue'>📋 邮件详情</font>**",
                                                            "text_align": "left",
                                                        },
                                                        {
                                                            "tag": "markdown",
                                                            "content": "• **发件人** ：张三 (zhang.san@example.com)\n• **主题** ：关于XX项目预算审批的申请\n• **日期** ：2023-10-27 09:30\n• **摘要** ：申请XX项目第三季度预算，金额15万元，用于采购新设备\n• **审批建议** ：建议批准，符合本季度预算规划",
                                                            "text_align": "left",
                                                            "text_size": "notation",
                                                        },
                                                        {
                                                            "tag": "column_set",
                                                            "horizontal_align": "left",
                                                            "columns": [
                                                                {
                                                                    "tag": "column",
                                                                    "width": "weighted",
                                                                    "elements": [
                                                                        {
                                                                            "tag": "input",
                                                                            "placeholder": {
                                                                                "tag": "plain_text",
                                                                                "content": "处理情况说明，选填",
                                                                                "i18n_content": {
                                                                                    "en_us": "Action taken (if any)"
                                                                                },
                                                                            },
                                                                            "label": {
                                                                                "tag": "plain_text",
                                                                                "content": "审批意见",
                                                                            },
                                                                            "default_value": "",
                                                                            "width": "fill",
                                                                            "name": "notes_input",
                                                                            "margin": "0px 0px 0px 0px",
                                                                        },
                                                                        # {
                                                                        #     "tag": "input",
                                                                        #     "name": "approval_comment",
                                                                        #     "placeholder": {
                                                                        #         "tag": "plain_text",
                                                                        #         "content": "请输入您的审批意见...",
                                                                        #     },
                                                                        #     "default_value": "",
                                                                        #     "width": "default",
                                                                        #     "label": {
                                                                        #         "tag": "plain_text",
                                                                        #         "content": "审批意见",
                                                                        #     },
                                                                        #     "label_position": "top",
                                                                        #     "disabled": False,
                                                                        #     "behaviors": [
                                                                        #         {
                                                                        #             "type": "callback",
                                                                        #             "value": "",
                                                                        #         }
                                                                        #     ],
                                                                        #     "margin": "8px 0px 8px 0px",
                                                                        #     "element_id": "custom_id",
                                                                        # },
                                                                        {
                                                                            "tag": "button",
                                                                            "text": {
                                                                                "tag": "plain_text",
                                                                                "content": "处理完成",
                                                                                "i18n_content": {
                                                                                    "en_us": "Mark as Resolved"
                                                                                },
                                                                            },
                                                                            "type": "primary_filled",
                                                                            "width": "fill",
                                                                            "behaviors": [
                                                                                {
                                                                                    "type": "callback",
                                                                                    "value": {
                                                                                        "action": "complete_alarm",
                                                                                        "time": "${alarm_time}",
                                                                                    },
                                                                                }
                                                                            ],
                                                                            "form_action_type": "submit",
                                                                            "name": "email_submit_approval",
                                                                        },
                                                                        # {
                                                                        #     "tag": "button",
                                                                        #     "text": {
                                                                        #         "tag": "plain_text",
                                                                        #         "content": "处理选中邮件",
                                                                        #     },
                                                                        #     "type": "primary_filled",
                                                                        #     "width": "fill",
                                                                        #     "disabled": False,
                                                                        #     "behaviors": [
                                                                        #         {
                                                                        #             "type": "callback",
                                                                        #             "value": {
                                                                        #                 "action": "process_email"
                                                                        #             },
                                                                        #         }
                                                                        #     ],
                                                                        #     "margin": "4px 0px 4px 0px",
                                                                        # },
                                                                    ],
                                                                    "vertical_spacing": "8px",
                                                                    "horizontal_align": "left",
                                                                    "vertical_align": "top",
                                                                    "weight": 1,
                                                                }
                                                            ],
                                                        },
                                                    ],
                                                    "vertical_spacing": "8px",
                                                    "horizontal_align": "left",
                                                    "vertical_align": "top",
                                                    "weight": 1,
                                                }
                                            ],
                                            "margin": "0px 0px 0px 0px",
                                        },
                                    ],
                                    "vertical_spacing": "8px",
                                    "horizontal_align": "left",
                                    "vertical_align": "top",
                                }
                            ],
                            "margin": "0px 0px 0px 0px",
                        }
                    ],
                    "direction": "vertical",
                    "padding": "4px 0px 4px 0px",
                    "margin": "0px 0px 0px 0px",
                    "name": "Form_m6vy7xol",
                },
            ],
        },
        "header": {
            "title": {"tag": "plain_text", "content": "邮件分类处理中心"},
            "subtitle": {"tag": "plain_text", "content": ""},
            "template": "blue",
            "padding": "12px 12px 12px 12px",
        },
    }

    try:
        # 创建飞书API客户端
        feishu_api = FeishuAPI(app_id=app_id, app_secret=app_secret)

        # 示例3: 创建card_json类型卡片
        print("\n=== 示例3: 创建card_json类型卡片 ===")

        # 使用已有的demo_dict作为card_json数据
        card_json_data = json.dumps(demo_dict)

        # 调用创建卡片方法
        card_id = None
        try:
            card_result = feishu_api.create_card(
                card_type="card_json", card_data=card_json_data
            )
            print("创建card_json类型卡片结果:", card_result)
            # 获取创建的卡片ID
            card_id = card_result.get("card_id")
            if card_id:
                print(f"成功获取卡片ID: {card_id}")
            else:
                print("创建卡片成功，但未返回card_id")
        except Exception as e:
            print(f"创建card_json类型卡片失败: {str(e)}")

        # 示例4: 创建template类型卡片（需要替换为实际的模板ID和版本）
        print("\n=== 示例4: 创建template类型卡片 ===")

        # # 模板数据（实际使用时需要替换为真实的模板ID和变量）
        # template_data = json.dumps({
        #     "template_id": "AAqIi1B8abcef",
        #     "template_version_name": "1.0.0",
        #     "template_variable": {
        #         "open_id": "ou_5c6d1637498e704f541095bba3dabcef"
        #     }
        # })

        # # 调用创建卡片方法
        # # 注意：由于这是示例模板ID，实际执行可能会失败
        # try:
        #     card_result = feishu_api.create_card(
        #         card_type="template",
        #         card_data=template_data
        #     )
        #     print("创建template类型卡片结果:", card_result)
        # except Exception as e:
        #     print(f"创建template类型卡片失败（预期行为，因为模板ID是示例）: {str(e)}")

        # 示例5: 发送卡片消息
        print("\n=== 示例5: 发送卡片消息 ===")
        if card_id:
            try:
                # 先使用手机号获取用户open_id
                print("\n=== 获取用户open_id ===")
                mobiles = ["15810260321"]
                user_ids_info = feishu_api.batch_get_user_id(
                    mobiles=mobiles,
                    include_resigned=True,
                    user_id_type="open_id",
                )
                print("批量获取的用户ID信息:", user_ids_info)

                # 获取open_id
                open_id = None
                if user_ids_info.get("user_list"):
                    open_id = user_ids_info["user_list"][0].get("user_id")
                    if open_id:
                        print(f"成功获取用户open_id: {open_id}")
                    else:
                        print("未获取到用户open_id")

                # 使用真实创建的卡片ID和获取到的open_id发送消息
                if open_id:
                    send_result = feishu_api.send_card_message(
                        receive_id_type="open_id", receive_id=open_id, card_id=card_id
                    )
                    print("发送卡片消息结果:", send_result)
            except Exception as e:
                print(f"发送卡片消息失败: {str(e)}")
        else:
            print("未获取到卡片ID，跳过发送卡片消息")

    except Exception as e:
        print(f"执行出错: {str(e)}")
