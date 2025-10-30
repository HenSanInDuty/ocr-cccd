# Test script cho QR parsing
import sys
sys.path.append('.')

from app import parse_qr_result, display_parsed_info

# Test data
test_qr = "096200014786|381902150|Trần Trọng Nhân|20122000|Nam|Cái Keo, Quách Phẩm, Cà Mau|18082025||||"

print("Testing QR parsing...")
print(f"Input: {test_qr}")
print()

result = parse_qr_result(test_qr)
print("Parsed result:")
for key, value in result.items():
    print(f"{key}: {value}")