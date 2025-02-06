def encrypt(s):
    # 将字符串转换为UTF-8编码的字节，然后转为二进制字符串
    binary_str = ''.join(format(byte, '08b') for byte in s.encode('utf-8'))
    # 将二进制中的0替换为喵，1替换为苗（修复了原代码中的~符号错误）
    miao_encrypted = ''.join(['喵' if bit == '0' else '~' for bit in binary_str])
    return miao_encrypted


def decrypt(encrypted_str):
    # 将加密字符串转换回二进制字符串
    binary_str = ''.join(['0' if c == '喵' else '1' for c in encrypted_str])
    # 检查二进制长度是否为8的倍数
    if len(binary_str) % 8 != 0:
        raise ValueError("无效的加密字符串，长度不正确")
    # 分割为8位一组并转换为字节
    bytes_list = []
    for i in range(0, len(binary_str), 8):
        byte_str = binary_str[i:i + 8]
        bytes_list.append(int(byte_str, 2))
    # 将字节解码为原始字符串
    return bytes(bytes_list).decode('utf-8')


def save_encrypted_file(text, filename):
    """将加密文本写入文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)


def load_encrypted_file(filename):
    """从文件读取加密文本"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read().strip()  # 移除可能的换行符


# 示例使用
if __name__ == "__main__":
    # 原始字符串
    original = "hello,word"

    # 加密并保存到文件
    encrypted = encrypt(original)
    save_encrypted_file(encrypted, 'miao.txt')
    print("加密结果已保存到 secret.miao")

    # 从文件读取并解密
    encrypted_from_file = load_encrypted_file('miao.txt')
    decrypted = decrypt(encrypted_from_file)

    print("\n原始字符串:", original)
    print("解密结果:", decrypted)