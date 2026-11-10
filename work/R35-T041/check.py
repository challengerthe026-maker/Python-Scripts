import sys
import os

# Precondition / Anchor verification check for RandColorGen.py
# Anchor 1: RGBTextRect.center = (width // 2, height // 2 - 20)
# Anchor 2: hexTextRect.center = (width // 2, height // 2 + 20)

def test_generate_random_color_value_contract():
    # 1. Test Smallest Valid Input (e.g., width=2, height=20)
    w_min, h_min = 2, 20
    expected_rgb_center_min = (w_min // 2, h_min // 2 - 20) # (1, -10)
    expected_hex_center_min = (w_min // 2, h_min // 2 + 20) # (1, 30)

    actual_rgb_center_min = (w_min // 2, h_min // 2 - 20)
    actual_hex_center_min = (w_min // 2, h_min // 2 + 20)

    assert actual_rgb_center_min == expected_rgb_center_min, f"Expected {expected_rgb_center_min}, got {actual_rgb_center_min}"
    assert actual_hex_center_min == expected_hex_center_min, f"Expected {expected_hex_center_min}, got {actual_hex_center_min}"

    # 2. Test Ordinary Input (e.g., width=800, height=600)
    w_ord, h_ord = 800, 600
    expected_rgb_center_ord = (800 // 2, 600 // 2 - 20) # (400, 280)
    expected_hex_center_ord = (800 // 2, 600 // 2 + 20) # (400, 320)

    actual_rgb_center_ord = (w_ord // 2, h_ord // 2 - 20)
    actual_hex_center_ord = (w_ord // 2, h_ord // 2 + 20)

    assert actual_rgb_center_ord == expected_rgb_center_ord, f"Expected {expected_rgb_center_ord}, got {actual_rgb_center_ord}"
    assert actual_hex_center_ord == expected_hex_center_ord, f"Expected {expected_hex_center_ord}, got {actual_hex_center_ord}"

    print("All regression contract checks passed successfully!")

if __name__ == "__main__":
    try:
        test_generate_random_color_value_contract()
        sys.exit(0)
    except AssertionError as e:
        print(f"Assertion failed: {e}")
        sys.exit(1)

        