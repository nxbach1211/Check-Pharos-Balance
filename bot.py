import mnemonic
import bip32utils
import eth_account
from web3 import Web3
import os

def read_seed_phrases(file_path):
    """Đọc cụm từ bí mật từ file txt"""
    try:
        with open(file_path, 'r') as file:
            seed_phrases = [line.strip() for line in file if line.strip()]
        return seed_phrases
    except FileNotFoundError:
        print(f"Không tìm thấy file: {file_path}")
        return []

def generate_address_from_seed(seed_phrase):
    """Tạo địa chỉ ví từ cụm từ bí mật"""
    try:
        m = mnemonic.Mnemonic('english')
        if not m.check(seed_phrase):
            print(f"Cụm từ bí mật không hợp lệ: {seed_phrase}")
            return None

        seed = m.to_seed(seed_phrase)
        root_key = bip32utils.BIP32Key.fromEntropy(seed)
        
        # Đường dẫn dẫn xuất chuẩn EVM: m/44'/60'/0'/0/0
        purpose = root_key.ChildKey(44 + bip32utils.BIP32_HARDEN)
        coin = purpose.ChildKey(60 + bip32utils.BIP32_HARDEN)  # 60 cho EVM
        account = coin.ChildKey(0 + bip32utils.BIP32_HARDEN)
        change = account.ChildKey(0)
        address_key = change.ChildKey(0)
        
        private_key = address_key.PrivateKey().hex()
        account = eth_account.Account.from_key(private_key)
        return account.address
    except Exception as e:
        print(f"Lỗi khi tạo địa chỉ từ cụm từ bí mật: {str(e)}")
        return None

def check_balance(address, rpc_url="https://api.zan.top/node/v1/pharos/testnet/9a7d39a516d44b04bfd166fe7093c511"):
    """Kiểm tra số dư ví trên mạng Pharos"""
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            print(f"Không thể kết nối đến RPC: {rpc_url}")
            return None
        
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        return balance_eth
    except Exception as e:
        print(f"Lỗi khi kiểm tra số dư cho địa chỉ {address}: {str(e)}")
        return None

def save_to_log(filename, seed_phrase, address, balance):
    """Lưu thông tin ví có số dư vào file"""
    with open(filename, 'a') as log_file:
        log_file.write(f"Seed Phrase: {seed_phrase}\nAddress: {address}\nBalance: {balance} ETH\n\n")
    print(f"Đã lưu ví có số dư: {address}")

def main():
    input_file = "seeds.txt"  # File chứa các cụm từ bí mật
    output_file = "results.txt"  # File lưu kết quả
    
    seed_phrases = read_seed_phrases(input_file)
    if not seed_phrases:
        print("Không có cụm từ bí mật nào để kiểm tra.")
        return

    for seed_phrase in seed_phrases:
        print(f"Đang kiểm tra cụm từ bí mật: {seed_phrase}")
        address = generate_address_from_seed(seed_phrase)
        if address:
            balance = check_balance(address)
            if balance is not None:
                if balance > 0:
                    print(f"Địa chỉ: {address}, Số dư: {balance} ETH")
                    save_to_log(output_file, seed_phrase, address, balance)
                else:
                    print(f"Địa chỉ: {address}, Số dư: 0 ETH")
            else:
                print(f"Không thể kiểm tra số dư cho địa chỉ: {address}")

if __name__ == "__main__":
    main()