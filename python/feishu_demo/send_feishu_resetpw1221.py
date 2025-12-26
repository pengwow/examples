import requests
import json
from feishu_api import FeishuAPI
card_json = {
    "schema": "2.0",
    "config": {
        "update_multi": True
    },
    "body": {
        "direction": "vertical",
        "elements": [
            {
                "tag": "form",
                "elements": [
                    {
                        "tag": "markdown",
                        "content": "邮箱邮件获取失败,修改密码后重试",
                        "element_id": "t1"
                    },
                    {
                        "tag": "markdown",
                        "content": "<font color='grey'>当前邮箱地址：</font><br><font color='blue'>example@company.com</font>",
                        "element_id": "custom_id"
                    },
                    {
                        "tag": "input",
                        "placeholder": {
                            "tag": "plain_text",
                            "content": "请输入新密码"
                        },
                        "default_value": "",
                        "width": "default",
                        "label": {
                            "tag": "plain_text",
                            "content": "确认新密码"
                        },
                        "label_position": "top",
                        "required": True,
                        "name": "confirm_password",
                        "margin": "8px 0px 0px 0px",
                        "element_id": "xP3HyIrXUOpAVyzE0w1L"
                    },
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "提交修改"
                        },
                        "type": "primary_filled",
                        "width": "fill",
                        "behaviors": [
                            {
                                "type": "callback",
                                "value": {
                                    "action": "change_password"
                                }
                            }
                        ],
                        "form_action_type": "submit",
                        "name": "email_reset_pwd_submit_button",
                        "margin": "4px 0px 4px 0px",
                        "element_id": "uyiQaXJbgaIOHbO_faEE"
                    }
                ],
                "direction": "vertical",
                "horizontal_align": "left",
                "vertical_align": "top",
                "padding": "12px 12px 12px 12px",
                "margin": "0px 0px 0px 0px",
                "name": "password_change_form"
            }
        ]
    },
    "header": {
        "title": {
            "tag": "plain_text",
            "content": "邮箱密码修改"
        },
        "subtitle": {
            "tag": "plain_text",
            "content": ""
        },
        "template": "blue",
        "icon": {
            "tag": "standard_icon",
            "token": "password_outlined"
        },
        "padding": "12px 8px 12px 8px"
    }
}

if __name__ == '__main__':
    app_id = "cli_a83fafd0aa14d013"
    app_secret = "dy637jNB8N4v7bBbeHNA0eZveXizuZxH"
    feishu_api = FeishuAPI(app_id, app_secret)
    feishu_api = FeishuAPI(app_id=app_id, app_secret=app_secret)

    # 示例3: 创建card_json类型卡片
    print("\n=== 示例3: 创建card_json类型卡片 ===")

    # 使用已有的demo_dict作为card_json数据
    card_json_data = json.dumps(card_json)

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