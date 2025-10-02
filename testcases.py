from proj1 import SICXEDecoder

def test():
    decoder = SICXEDecoder()

    print("ppt 테스트케이스들")

    testCases = [
        {
            'hex': '032600',
            'pc': 0x003000,
        },
        {
            'hex': '03C300',
            'pc': 0x003000,
        },
        {
            'hex': '022030',
            'pc': 0x003000,
        },
        {
            'hex': '010030',
            'pc': 0x003000,
        },
        {
            'hex': '003600',
            'pc': 0x003000,
        },
        {
            'hex': '0310C303',
            'pc': 0x003000,
        }
    ]

    for i, test in enumerate(testCases, 1):
        print(f"\n---- {i}번째 hex: {[test['hex']]}")
        decoder.decodeInstruction(test['hex'], test['pc'])

if __name__ == "__main__":
    test()