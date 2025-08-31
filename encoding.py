def hex_encode(text: str) -> str:
    """Encode normal text (like MAC address) into hex"""
    return text.encode().hex()


def hex_decode(hex_text: str) -> str:
    hex_text = hex_text.strip().replace(" ", "").replace("\n", "")

    # Check if valid hex
    if len(hex_text) % 2 != 0:
        raise ValueError("Hex string length must be even!")

    try:
        return bytes.fromhex(hex_text).decode()
    except Exception as e:
        raise ValueError(" Invalid hex string!") from e


if __name__ == "__main__":
    action = input("Choose action (encode/decode): ").strip().lower()

    if action == "encode":
        text = input("Enter normal text: ").strip()
        encoded = hex_encode(text)
        print("Hex Encoded:", encoded)

    elif action == "decode":
        text = input("Enter hex string to decode: ")
        try:
            decoded = hex_decode(text)
            print("Decoded Text:", decoded)
        except ValueError as e:
            print(e)

    else:
        print("Invalid action! Use encode or decode.")
