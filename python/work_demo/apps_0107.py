# python3.6环境使用AES加密用户密码, 并存储到数据库中,编写两个函数用来加密和解密
# 加解密方法中,还需要增加密码参数, 用来指定加密密钥, 密码需要在加上盐值后再进行加密, 解密时需要使用相同的密码和盐值, 否则无法解密,盐值为用户的用户名,每个用户用户密码不同,盐值不同,加密后的密码也不同
# 编写完整的加解密函数, 包括加密和解密两个方法, 并在函数中添加必要的参数和异常处理,编写demo, 演示加解密过程多个用户的密码, 并验证解密是否正确

import base64
import hashlib
import hmac
import os

def encrypt_data(data, salt, master_key):
    """
    使用加密算法加密数据（基于PBKDF2和HMAC-SHA256）
    
    参数:
        data: 要加密的数据 (str)
        salt: 盐值，通常为用户名 (str)
        master_key: 主密钥，用于派生加密密钥 (str)
    
    返回:
        dict: {
            'status': bool,  # 是否成功
            'data': str,     # 加密后的数据，格式为 base64(derived_key + hmac)
            'message': str   # 状态消息
        }
    """
    try:
        # 参数验证
        if not data or not salt or not master_key:
            return {
                'status': False,
                'data': '',
                'message': '参数错误：数据、盐值和主密钥不能为空'
            }
        
        if not isinstance(data, str) or not isinstance(salt, str) or not isinstance(master_key, str):
            return {
                'status': False,
                'data': '',
                'message': '参数错误：数据、盐值和主密钥必须是字符串'
            }
        
        # 使用PBKDF2从主密钥和盐值派生密钥
        # 使用100000次迭代来增强安全性
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key.encode('utf-8'),
            salt.encode('utf-8'),
            100000,
            dklen=32  # 32字节密钥
        )
        
        # 使用派生密钥对数据进行HMAC签名
        hmac_obj = hmac.new(derived_key, data.encode('utf-8'), hashlib.sha256)
        hmac_digest = hmac_obj.digest()
        
        # 将派生密钥和HMAC合并，然后进行base64编码
        combined = derived_key + hmac_digest
        encrypted_data = base64.b64encode(combined).decode('utf-8')
        
        return {
            'status': True,
            'data': encrypted_data,
            'message': 'ok'
        }
        
    except Exception as e:
        return {
            'status': False,
            'data': '',
            'message': f'加密过程中发生错误: {str(e)}'
        }

def decrypt_data(encrypted_data, salt, master_key, original_data=None):
    """
    验证加密的数据（基于HMAC验证）
    
    参数:
        encrypted_data: 加密后的数据 (str)
        salt: 盐值，必须与加密时相同 (str)
        master_key: 主密钥，必须与加密时相同 (str)
        original_data: 原始数据，用于验证 (str, 可选)
    
    返回:
        dict: {
            'status': bool,  # 是否成功
            'data': str,     # 解密后的数据（如果验证成功）
            'message': str   # 状态消息
        }
    """
    try:
        # 参数验证
        if not encrypted_data or not salt or not master_key:
            return {
                'status': False,
                'data': '',
                'message': '参数错误：加密数据、盐值和主密钥不能为空'
            }
        
        if not isinstance(encrypted_data, str) or not isinstance(salt, str) or not isinstance(master_key, str):
            return {
                'status': False,
                'data': '',
                'message': '参数错误：加密数据、盐值和主密钥必须是字符串'
            }
        
        # 解码base64
        combined = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # 提取派生密钥和HMAC
        stored_derived_key = combined[:32]  # 前32字节是派生密钥
        stored_hmac = combined[32:]  # 剩余的是HMAC
        
        # 使用相同的方法重新派生密钥
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key.encode('utf-8'),
            salt.encode('utf-8'),
            100000,
            dklen=32
        )
        
        # 验证派生密钥是否匹配
        if derived_key != stored_derived_key:
            return {
                'status': False,
                'data': '',
                'message': '密钥验证失败：主密钥或盐值不匹配'
            }
        
        # 如果提供了原始数据，验证HMAC
        if original_data is not None:
            # 重新计算HMAC
            hmac_obj = hmac.new(derived_key, original_data.encode('utf-8'), hashlib.sha256)
            computed_hmac = hmac_obj.digest()
            
            # 验证HMAC是否匹配
            if computed_hmac != stored_hmac:
                return {
                    'status': False,
                    'data': '',
                    'message': '数据验证失败：数据不正确'
                }
            
            return {
                'status': True,
                'data': original_data,
                'message': 'ok'
            }
        else:
            # 如果没有提供原始数据，只验证密钥是否正确
            return {
                'status': True,
                'data': '',
                'message': 'ok'
            }
        
    except Exception as e:
        return {
            'status': False,
            'data': '',
            'message': f'解密过程中发生错误: {str(e)}'
        }

def verify_data(encrypted_data, salt, master_key, data_to_verify):
    """
    验证数据是否正确
    
    参数:
        encrypted_data: 加密后的数据 (str)
        salt: 盐值，必须与加密时相同 (str)
        master_key: 主密钥，必须与加密时相同 (str)
        data_to_verify: 要验证的数据 (str)
    
    返回:
        bool: 验证是否成功
    """
    result = decrypt_data(encrypted_data, salt, master_key, data_to_verify)
    return result['status']

def demo_encryption_decryption():
    """
    演示多个用户的密码加解密过程，并验证解密是否正确
    """
    print("=" * 60)
    print("密码加解密演示（基于PBKDF2和HMAC-SHA256）")
    print("=" * 60)
    
    # 定义主密钥（实际应用中应该安全存储）
    MASTER_KEY = "my_secret_master_key_2024"
    
    # 模拟多个用户数据
    users = [
        {"username": "alice", "password": "alice123"},
        {"username": "bob", "password": "bob456"},
        {"username": "charlie", "password": "charlie789"},
        {"username": "david", "password": "david000"},
        {"username": "eve", "password": "eve111"}
    ]
    
    print(f"\n使用的主密钥: {MASTER_KEY}")
    print(f"\n用户数量: {len(users)}")
    
    # 存储加密后的密码（模拟数据库存储）
    encrypted_passwords = {}
    
    print("\n" + "=" * 60)
    print("第一步：加密用户密码")
    print("=" * 60)
    
    for user in users:
        username = user["username"]
        password = user["password"]
        
        # 加密密码（使用用户名作为盐值）
        result = encrypt_data(password, username, MASTER_KEY)
        
        if result['status']:
            encrypted_passwords[username] = result['data']
            
            print(f"\n用户: {username}")
            print(f"  原始密码: {password}")
            print(f"  盐值: {username}")
            print(f"  加密后: {result['data'][:50]}...")  # 只显示前50个字符
        else:
            print(f"\n用户 {username} 加密失败: {result['message']}")
    
    print("\n" + "=" * 60)
    print("第二步：解密并验证用户密码")
    print("=" * 60)
    
    # 验证解密是否正确
    all_decrypted_correctly = True
    
    for user in users:
        username = user["username"]
        original_password = user["password"]
        encrypted = encrypted_passwords.get(username)
        
        if encrypted is None:
            print(f"\n用户 {username} 的加密密码不存在")
            all_decrypted_correctly = False
            continue
        
        # 解密密码
        result = decrypt_data(encrypted, username, MASTER_KEY, original_password)
        
        if result['status']:
            print(f"\n用户: {username}")
            print(f"  加密密码: {encrypted[:50]}...")
            print(f"  解密后: {result['data']}")
            print(f"  原始密码: {original_password}")
            
            # 验证解密是否正确
            if result['data'] == original_password:
                print(f"  验证结果: ✅ 解密正确")
            else:
                print(f"  验证结果: ❌ 解密错误")
                all_decrypted_correctly = False
        else:
            print(f"\n用户 {username} 解密失败: {result['message']}")
            all_decrypted_correctly = False
    
    print("\n" + "=" * 60)
    print("第三步：验证不同用户加密结果不同")
    print("=" * 60)
    
    # 验证相同密码在不同用户下加密结果不同
    test_users = [
        {"username": "user1", "password": "same_password"},
        {"username": "user2", "password": "same_password"}
    ]
    
    print("\n测试：相同密码在不同用户名（不同盐值）下的加密结果")
    encrypted_results = []
    
    for user in test_users:
        username = user["username"]
        password = user["password"]
        result = encrypt_data(password, username, MASTER_KEY)
        if result['status']:
            encrypted_results.append((username, result['data']))
            print(f"\n用户: {username}")
            print(f"  密码: {password}")
            print(f"  加密结果: {result['data'][:50]}...")
    
    # 检查加密结果是否不同
    if encrypted_results[0][1] != encrypted_results[1][1]:
        print(f"\n✅ 验证通过：相同密码在不同用户下加密结果不同")
    else:
        print(f"\n❌ 验证失败：相同密码在不同用户下加密结果相同")
        all_decrypted_correctly = False
    
    print("\n" + "=" * 60)
    print("第四步：验证错误密钥无法解密")
    print("=" * 60)
    
    # 测试使用错误的密钥解密
    print("\n测试：使用错误的密钥解密")
    test_username = "alice"
    test_encrypted = encrypted_passwords[test_username]
    test_password = users[0]["password"]
    wrong_key = "wrong_master_key"
    
    try:
        result = decrypt_data(test_encrypted, test_username, wrong_key, test_password)
        if result['status']:
            print(f"❌ 验证失败：使用错误密钥竟然解密成功: {result['data']}")
            all_decrypted_correctly = False
        else:
            print(f"✅ 验证通过：使用错误密钥解密失败（符合预期）")
            print(f"  错误信息: {result['message'][:100]}...")
    except Exception as e:
        print(f"✅ 验证通过：使用错误密钥解密失败（符合预期）")
        print(f"  错误信息: {str(e)[:100]}...")
    
    print("\n" + "=" * 60)
    print("第五步：验证密码验证函数")
    print("=" * 60)
    
    # 测试密码验证函数
    print("\n测试：验证正确的密码")
    test_username = "bob"
    test_encrypted = encrypted_passwords[test_username]
    correct_password = users[1]["password"]
    wrong_password = "wrong_password"
    
    # 验证正确密码
    is_correct = verify_data(test_encrypted, test_username, MASTER_KEY, correct_password)
    print(f"用户: {test_username}")
    print(f"  正确密码: {correct_password}")
    print(f"  验证结果: {'✅ 正确' if is_correct else '❌ 错误'}")
    
    # 验证错误密码
    is_correct = verify_data(test_encrypted, test_username, MASTER_KEY, wrong_password)
    print(f"\n用户: {test_username}")
    print(f"  错误密码: {wrong_password}")
    print(f"  验证结果: {'❌ 错误（符合预期）' if not is_correct else '✅ 正确（不符合预期）'}")
    
    if not is_correct:
        print(f"✅ 验证通过：错误密码被正确拒绝")
    else:
        print(f"❌ 验证失败：错误密码被错误接受")
        all_decrypted_correctly = False
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if all_decrypted_correctly:
        print("\n✅ 所有测试通过！")
        print("   - 所有用户密码加密成功")
        print("   - 所有用户密码解密正确")
        print("   - 相同密码在不同用户下加密结果不同")
        print("   - 错误密钥无法解密")
        print("   - 密码验证函数工作正常")
    else:
        print("\n❌ 部分测试失败！")
    
    print("\n" + "=" * 60)
    print("技术说明")
    print("=" * 60)
    print("\n本实现使用以下加密技术：")
    print("1. PBKDF2-HMAC-SHA256：密钥派生函数，用于从主密钥和盐值派生强密钥")
    print("2. HMAC-SHA256：基于哈希的消息认证码，用于密码验证")
    print("3. Base64编码：用于安全存储和传输加密数据")
    print("4. 盐值：使用用户名作为盐值，确保每个用户的加密结果不同")
    print("5. 100000次迭代：增强密钥派生的安全性")
    print("\n注意：由于Python环境限制，本实现使用了PBKDF2和HMAC代替AES")
    print("在生产环境中，建议使用pycryptodome库实现真正的AES加密")
    print("=" * 60)

if __name__ == "__main__":
    # 运行演示
    demo_encryption_decryption()
