def hex_encode(text: str) -> str:
    return text.encode().hex()

def hex_decode(hex_text: str) -> str:
    return bytes.fromhex(hex_text).decode()

if __name__ == "__main__":
    action = input("Choose action (encode/decode): ").strip().lower()

    if action == "encode":
        text = input("Enter normal text to encode: ")
        print("Hex Encoded:", hex_encode(text))
    elif action == "decode":
        text = input("Enter hex string to decode: ")
        try:
            print("Decoded Text:", hex_decode(text))
        except ValueError:
            print("❌ Invalid hex string! Make sure you enter only hex characters (0-9, a-f).")
    else:
        print("Invalid action! Use encode or decode.")
