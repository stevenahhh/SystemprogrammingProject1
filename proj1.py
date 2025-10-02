class SICXEDecoder:
    def __init__(self):
        # opcode -> mnemonic table
        self.OPCODES = {
            0x00: 'LDA'  # Load Accumulator
        }

        # 레지스터 테이블
        self.registers = {
            0: 'A',
            1: 'X',
            2: 'L',
            3: 'B',
            4: 'S',
            5: 'T',
            6: 'F',
            8: 'PC',
            9: 'SW'
        }
        self.memoryMap = {     # 메모리 맵
            0x3030: 0x003600,  # 주소 3030에 값 003600
            0x3600: 0x103000,  # 주소 3600에 값 103000
            0x6390: 0x00C303,  # 주소 6390에 값 00C303
            0xC303: 0x003030,  # 주소 C303에 값 003030
        }

        self.defaultRegisters = { # 레지스터 값
            'B': 0x006000,        # Base
            'PC': 0x003000,       # Program
            'X': 0x000090         # Index
        }

    def getAddressingMode(self, n, i, x, b, p, e, isFormat4=False):
        # 주소 지정 모드
        if n == 0 and i == 0:
            addrMode = "SIC format"
        elif n == 1 and i == 1:
            addrMode = "Simple addressing"
        elif n == 1 and i == 0:
            addrMode = "Indirect addressing"
        elif n == 0 and i == 1:
            addrMode = "Immediate addressing"

        if isFormat4: # 4형식인지 3형식인지
            addrMode += ", Extended" if e == 1 else "" # - 4형식(e=1)
        else:
            addrMode += ", PC-relative" if p == 1 else "" # 3형식 p=1이면 Program-counter relative
            addrMode += ", Base-relative" if b == 1 else "" # 3형식 b=1이면 Base-relative

        addrMode += ", Indexed" if x == 1 else "" # 인덱스 레지스터

        return addrMode

    def printMemoryValue(self, address): # 레지스터 A에 로드된 값 출력하는함수
        memoryValue = self.memoryMap.get(address, None)
        if memoryValue is not None:
            print(f"register A: {memoryValue:06X}")

    def decodeInstruction(self, hexInput, pcValue=None, baseValue=None, xValue=None):
        hexCode = hexInput
        instruction = int(hexCode, 16) # hex를 정수로 변환

        if pcValue is None:
            pcValue = self.defaultRegisters['PC']  # 값 비어있으면 PC = 0x003000
        if baseValue is None:
            baseValue = self.defaultRegisters['B']  # Base = 0x006000
        if xValue is None:
            xValue = self.defaultRegisters['X']    # Index = 0x000090

        if len(hexCode) == 6:        # 6자리면 3바이트
            self.decodeFormat3(instruction, hexCode, pcValue, baseValue, xValue) # 3형식 디코딩하러 감
        elif len(hexCode) == 8:		# 8자리면 4바이트
            self.decodeFormat4(instruction, hexCode) # 4형식 디코딩하러 감

    def decodeFormat3(self, instruction, hexCode, pcValue, baseValue, xValue):
        # 3형식
        # 비트 추출
        opCode = (instruction >> 16) & 0xFC  # 상위 6비트
        ni = (instruction >> 16) & 0x03     # n, i 비트
        x = (instruction >> 15) & 0x01      # x 비트
        b = (instruction >> 14) & 0x01      # b 비트
        p = (instruction >> 13) & 0x01      # p 비트
        e = (instruction >> 12) & 0x01      # e 비트
        disp = instruction & 0xFFF          # 12비트 displacement

        # disp가 음수일 수 있으니 2의보수 처리
        if disp & 0x800:  # 12번째 비트가 1이면 음수
            dispSigned = disp - 0x1000  # 2의 보수 변환
        else:
            dispSigned = disp

        # opcode에서 명령어 찾기
        mnemonic = self.OPCODES.get(opCode, 'UNKNOWN')

        # 이진수 변환 ----- 24비트
        binary = format(instruction, '024b')
        binary_formatted = ' '.join([binary[i:i+4] for i in range(0, len(binary), 4)]) # 4비트씩 끊어서 표시. Claude code가 도와줬어요.
        print(f"Binary: {binary_formatted}")
        print(f"Opcode: {opCode:06X}")

        # nixbpe 비트
        n = (ni >> 1) & 1 # 두 번째 최하위 비트
        i = ni & 1 # 최하위 비트
        print(f"nixbpe: {n}{i}{x}{b}{p}{e}")

        # disp
        dispBinary = format(disp, '012b') # 12비트
        disp_formatted = ' '.join([dispBinary[i:i+4] for i in range(0, len(dispBinary), 4)]) # 4비트씩 끊어서 표시. Claude code가 또 도와줬어요.
        print(f"disp: {disp_formatted}")
        print(f"disp hex: {disp:X}")

        # TA 계산
        TA = None
        addressingCalc = ""

        # 주소 지정 모드에 따른 계산
        if n == 0 and i == 0:  # SIC 호환 모드 (15비트 주소) b, p, e 비트 주소의 일부로 사용 참고
            SICAddress = ((b << 14) + (p << 13) + (e << 12) + disp) & 0x7FFF  # 15비트 마스크
            TA = SICAddress
            addressingCalc = f"SIC format (15bit address) = 0x{TA:04X}" # 15비트 주소
        elif n == 1 and i == 1:  # Simple addressing
            if p == 1 and b == 0:  # PC relative
                TA = pcValue + dispSigned # PC + disp = TA
                addressingCalc = f"PC-relative: PC(0x{pcValue:04X}) + disp({dispSigned:+d}) = 0x{TA:04X}" # dispSigned가 음수일 수도 있어서 {dispSigned:+d}로 표시
            elif p == 0 and b == 1:  # Base relative
                TA = baseValue + dispSigned
                addressingCalc = f"Base-relative: Base(0x{baseValue:04X}) + disp({dispSigned:+d}) = 0x{TA:04X}"
            elif p == 0 and b == 0:  # Direct addressing 12b
                TA = disp
                addressingCalc = f"Direct addressing (12bit) = 0x{TA:04X}"
        elif n == 1 and i == 0:  # Indirect addressing
            if p == 1:  # PC relative indirect
                indirectAddr = pcValue + dispSigned
                TA = self.memoryMap.get(indirectAddr, 0x000000) # PC + disp = indirect주소에 실제 TA 들어있다고 가정
                addressingCalc = f"Indirect PC-relative: [PC(0x{pcValue:04X}) + disp({dispSigned:+d})] = [0x{indirectAddr:04X}] = 0x{TA:06X}"
        elif n == 0 and i == 1:  # Immediate addressing
            TA = dispSigned if dispSigned >= 0 else disp # 양수면 dispSigned, 음수면 disp
            addressingCalc = f"Immediate addressing = 0x{TA:04X}"

        # 인덱스 레지스터 적용
        if x == 1 and TA is not None:
            originalAddr = TA
            TA += xValue # 실제 참조 주소 만들기
            addressingCalc += f" + X(0x{xValue:04X}) = 0x{TA:04X}"

        if TA is not None:
            print(f"Target Address: {TA:04X}")
            print(f"계산: {addressingCalc}")

            # 메모리 값 표시
            self.printMemoryValue(TA)

        # getAddressingMode 호출해서 주소 지정 모드 확인
        addrMode = self.getAddressingMode(n, i, x, b, p, e, isFormat4=False)

        print(f"Addressing mode: {addrMode}")
        print(f"Format: 3")

        # n, i비트로 SIC인지 SIC/XE인지
        if n == 0 and i == 0:
            print(f"SIC/SICXE: SIC")
        else:
            print(f"SIC/SICXE: SIC/XE")

        print(f"Mnemonic: {mnemonic}")

    def decodeFormat4(self, instruction, hexCode):
        # 4형식
        # 비트 추출
        opCode = (instruction >> 24) & 0xFC  # 상위 6비트
        ni = (instruction >> 24) & 0x03     # n, i 비트
        x = (instruction >> 23) & 0x01      # x 비트
        b = (instruction >> 22) & 0x01      # b 비트
        p = (instruction >> 21) & 0x01      # p 비트
        e = (instruction >> 20) & 0x01      # e 비트
        address = instruction & 0xFFFFF     # 20비트 주소

        # opcode에서 명령어 찾기
        mnemonic = self.OPCODES.get(opCode, 'UNKNOWN')

        # 이진수 변환 (32비트)
        binary = format(instruction, '032b')
        binary_formatted = ' '.join([binary[i:i+4] for i in range(0, len(binary), 4)])
        print(f"Binary: {binary_formatted}")
        print(f"Opcode: {opCode:06X}")

        # nixbpe 비트들
        n = (ni >> 1) & 1
        i = ni & 1
        nixbpe = f"{n}{i}{x}{b}{p}{e}"
        print(f"nixbpe: {nixbpe}")

        # 주소 정보
        addrBinary = format(address, '020b')
        addr_formatted = ' '.join([addrBinary[i:i+4] for i in range(0, len(addrBinary), 4)])
        print(f"addr: {addr_formatted}")
        print(f"addr hex: {address:X}")
        print(f"Target Address: 0x{address:05X}")

        # 메모리 값 표시
        self.printMemoryValue(address)

        # 주소 지정 모드
        addrMode = self.getAddressingMode(n, i, x, b, p, e, isFormat4=True)

        print(f"Addressing mode: {addrMode}")
        print(f"Format: 4")
        print(f"SIC/SICXE: SIC/XE")
        print(f"Mnemonic: {mnemonic}")

if __name__ == "__main__":
    decoder = SICXEDecoder()
    hexInput = input("Hex 코드: ").strip()
    print()
    decoder.decodeInstruction(hexInput)