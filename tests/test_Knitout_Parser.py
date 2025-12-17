"""Basic tests for the parsing of knitout."""

from unittest import TestCase

from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_BreakPoint, Knitout_No_Op
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction


class TestKnitout_Parser(TestCase):
    def test_knit_code(self):
        codes = parse_knitout("knit + f1 1")
        assert len(codes) == 1, f"Expected one knit but got: {codes}"
        print(codes)
        codes = parse_knitout("knit + b2 2")
        assert len(codes) == 1, f"Expected one knit but got: {codes}"
        print(codes)
        codes = parse_knitout("knit - b3 3")
        assert len(codes) == 1, f"Expected one knit but got: {codes}"
        print(codes)
        codes = parse_knitout("knit + b3 4")
        assert len(codes) == 1, f"Expected one knit but got: {codes}"
        print(codes)

    def test_tuck_code(self):
        codes = parse_knitout("tuck + f1 1")
        assert len(codes) == 1, f"Expected one tuck but got: {codes}"
        print(codes)
        codes = parse_knitout("tuck + b2 2")
        assert len(codes) == 1, f"Expected one tuck but got: {codes}"
        print(codes)
        codes = parse_knitout("tuck - b3 3")
        assert len(codes) == 1, f"Expected one tuck but got: {codes}"
        print(codes)
        codes = parse_knitout("tuck + b3 4")
        assert len(codes) == 1, f"Expected one tuck but got: {codes}"
        print(codes)

    def test_miss_code(self):
        codes = parse_knitout("miss + f1 1")
        assert len(codes) == 1, f"Expected one miss but got: {codes}"
        print(codes)

    def test_split_code(self):
        codes = parse_knitout("split + f1 b2 1")
        assert len(codes) == 1, f"Expected one split but got: {codes}"
        print(codes)

    def test_xfer_code(self):
        codes = parse_knitout("xfer f2 b2 ")
        assert len(codes) == 1, f"Expected one xfer but got: {codes}"
        print(codes)

    def test_xfer_to_slider(self):
        codes = parse_knitout("xfer f2 bs2 ")
        assert len(codes) == 1, f"Expected one xfer but got: {codes}"
        print(codes)

    def test_drop_code(self):
        codes = parse_knitout("drop f2")
        assert len(codes) == 1, f"Expected one drop but got: {codes}"
        print(codes)

    def test_carrier_ops(self):
        codes = parse_knitout(
            r"""inhook 1
            in 2
            out 3
            outhook 4
            releasehook 5"""
        )
        assert len(codes) == 5, f"Expected five carrier operations but got: {codes}"
        print(codes)

    def test_rack(self):
        codes = parse_knitout("rack 1")
        assert len(codes) == 1, f"Expected one rack operation but got: {codes}"
        rack_code = codes[0]
        assert isinstance(rack_code, Rack_Instruction), f"Expected rack operation but got {rack_code}"
        assert rack_code.rack == 1, f"Expected rack of 1 but got {rack_code.rack} from {rack_code}"
        assert not rack_code.all_needle_rack, f"Unexpected all-needle-rack from {rack_code}"
        print(rack_code)
        codes = parse_knitout("rack 0.25")
        assert len(codes) == 1, f"Expected one rack operation but got: {codes}"
        rack_code = codes[0]
        assert isinstance(rack_code, Rack_Instruction), f"Expected rack operation but got {rack_code}"
        assert rack_code.rack == 0, f"Expected rack of 0 but got {rack_code.rack} from {rack_code}"
        assert rack_code.all_needle_rack, f"Expected all-needle-rack from {rack_code}"
        print(rack_code)
        codes = parse_knitout("rack -1")
        assert len(codes) == 1, f"Expected one rack operation but got: {codes}"
        rack_code = codes[0]
        assert isinstance(rack_code, Rack_Instruction), f"Expected rack operation but got {rack_code}"
        assert rack_code.rack == -1, f"Expected rack of -1 but got {rack_code.rack} from {rack_code}"
        assert not rack_code.all_needle_rack, f"Unexpected all-needle-rack from {rack_code}"
        print(rack_code)
        codes = parse_knitout("rack -0.75")
        assert len(codes) == 1, f"Expected one rack operation but got: {codes}"
        rack_code = codes[0]
        print(rack_code)
        assert isinstance(rack_code, Rack_Instruction), f"Expected rack operation but got {rack_code}"
        assert rack_code.rack == -1, f"Expected rack of -1 but got {rack_code.rack} from {rack_code}"
        assert rack_code.all_needle_rack, f"Expected all-needle-rack from {rack_code}"
        codes = parse_knitout("rack -4.75")
        assert len(codes) == 1, f"Expected one rack operation but got: {codes}"
        rack_code = codes[0]
        assert isinstance(rack_code, Rack_Instruction), f"Expected rack operation but got {rack_code}"
        assert rack_code.rack == -5, f"Expected rack of -5 but got {rack_code.rack} from {rack_code}"
        assert rack_code.all_needle_rack, f"Expected all-needle-rack from {rack_code}"
        print(rack_code)

    def test_pause(self):
        codes = parse_knitout("pause")
        assert len(codes) == 1, f"Expected one pause but got: {codes}"
        print(codes)

    def test_basic_header(self):
        codes = parse_knitout(
            r""";!knitout-3
                ;;Machine: SWG091N2
                ;;Gauge: 15
                ;;Yarn-5: 50-50 Rust
                ;;Carriers: 1 2 3 4 5 6 7 8 9 10
                ;;Position: Right"""
        )
        print(codes)

    def test_no_ops(self):
        codes = parse_knitout(
            r""";No-Op: inhook 1
            in 2
            out 3
            ;No-Op: outhook 4
            releasehook 5"""
        )
        self.assertTrue(isinstance(codes[0], Knitout_No_Op))
        self.assertTrue(isinstance(codes[3], Knitout_No_Op))

    def test_breakpoints(self):
        codes = parse_knitout(
            r""";BreakPoint
            inhook 1
            in 2
            out 3
            ;BreakPoint: With Comment
            outhook 4
            releasehook 5"""
        )
        self.assertTrue(isinstance(codes[0], Knitout_BreakPoint))
        self.assertTrue(isinstance(codes[4], Knitout_BreakPoint))
