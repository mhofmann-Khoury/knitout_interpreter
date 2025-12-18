"""Basic tests for the parsing of knitout."""

from typing import cast
from unittest import TestCase

from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_BreakPoint, Knitout_No_Op
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction


class TestKnitout_Parser(TestCase):
    def test_knit_code(self):
        codes = parse_knitout("knit + f1 1")
        self.assertEqual(len(codes), 1, f"Expected one knit but got: {codes}")
        codes = parse_knitout("knit + b2 2")
        self.assertEqual(len(codes), 1, f"Expected one knit but got: {codes}")
        codes = parse_knitout("knit - b3 3")
        self.assertEqual(len(codes), 1, f"Expected one knit but got: {codes}")
        codes = parse_knitout("knit + b3 4")
        self.assertEqual(len(codes), 1, f"Expected one knit but got: {codes}")

    def test_tuck_code(self):
        codes = parse_knitout("tuck + f1 1")
        self.assertEqual(len(codes), 1, f"Expected one tuck but got: {codes}")
        codes = parse_knitout("tuck + b2 2")
        self.assertEqual(len(codes), 1, f"Expected one tuck but got: {codes}")
        codes = parse_knitout("tuck - b3 3")
        self.assertEqual(len(codes), 1, f"Expected one tuck but got: {codes}")
        codes = parse_knitout("tuck + b3 4")
        self.assertEqual(len(codes), 1, f"Expected one tuck but got: {codes}")

    def test_miss_code(self):
        codes = parse_knitout("miss + f1 1")
        self.assertEqual(len(codes), 1, f"Expected one miss but got: {codes}")

    def test_split_code(self):
        codes = parse_knitout("split + f1 b2 1")
        self.assertEqual(len(codes), 1, f"Expected one split but got: {codes}")

    def test_xfer_code(self):
        codes = parse_knitout("xfer f2 b2 ")
        self.assertEqual(len(codes), 1, f"Expected one xfer but got: {codes}")

    def test_xfer_to_slider(self):
        codes = parse_knitout("xfer f2 bs2 ")
        self.assertEqual(len(codes), 1, f"Expected one xfer but got: {codes}")

    def test_drop_code(self):
        codes = parse_knitout("drop f2")
        self.assertEqual(len(codes), 1, f"Expected one drop but got: {codes}")

    def test_carrier_ops(self):
        codes = parse_knitout(
            r"""inhook 1
            in 2
            out 3
            outhook 4
            releasehook 5"""
        )
        self.assertEqual(len(codes), 5, f"Expected five carrier operations but got: {codes}")

    def test_rack(self):
        codes = parse_knitout("rack 1")
        self.assertEqual(len(codes), 1, f"Expected one rack operation but got: {codes}")
        rack_code: Rack_Instruction = cast(Rack_Instruction, codes[0])
        self.assertIsInstance(rack_code, Rack_Instruction, f"Expected rack operation but got {rack_code}")
        self.assertEqual(rack_code.rack, 1, f"Expected rack of 1 but got {rack_code.rack} from {rack_code}")
        self.assertFalse(rack_code.all_needle_rack, f"Unexpected all-needle-rack from {rack_code}")

        codes = parse_knitout("rack 0.25")
        self.assertEqual(len(codes), 1, f"Expected one rack operation but got: {codes}")
        rack_code: Rack_Instruction = cast(Rack_Instruction, codes[0])
        self.assertIsInstance(rack_code, Rack_Instruction, f"Expected rack operation but got {rack_code}")
        self.assertEqual(rack_code.rack, 0, f"Expected rack of 0 but got {rack_code.rack} from {rack_code}")
        self.assertTrue(rack_code.all_needle_rack, f"Expected all-needle-rack from {rack_code}")

        codes = parse_knitout("rack -1")
        self.assertEqual(len(codes), 1, f"Expected one rack operation but got: {codes}")
        rack_code: Rack_Instruction = cast(Rack_Instruction, codes[0])
        self.assertIsInstance(rack_code, Rack_Instruction, f"Expected rack operation but got {rack_code}")
        self.assertEqual(rack_code.rack, -1, f"Expected rack of -1 but got {rack_code.rack} from {rack_code}")
        self.assertFalse(rack_code.all_needle_rack, f"Unexpected all-needle-rack from {rack_code}")

        codes = parse_knitout("rack -0.75")
        self.assertEqual(len(codes), 1, f"Expected one rack operation but got: {codes}")
        rack_code: Rack_Instruction = cast(Rack_Instruction, codes[0])
        self.assertIsInstance(rack_code, Rack_Instruction, f"Expected rack operation but got {rack_code}")
        self.assertEqual(rack_code.rack, -1, f"Expected rack of -1 but got {rack_code.rack} from {rack_code}")
        self.assertTrue(rack_code.all_needle_rack, f"Expected all-needle-rack from {rack_code}")

        codes = parse_knitout("rack -4.75")
        self.assertEqual(len(codes), 1, f"Expected one rack operation but got: {codes}")
        rack_code: Rack_Instruction = cast(Rack_Instruction, codes[0])
        self.assertIsInstance(rack_code, Rack_Instruction, f"Expected rack operation but got {rack_code}")
        self.assertEqual(rack_code.rack, -5, f"Expected rack of -5 but got {rack_code.rack} from {rack_code}")
        self.assertTrue(rack_code.all_needle_rack, f"Expected all-needle-rack from {rack_code}")

    def test_pause(self):
        codes = parse_knitout("pause")
        self.assertEqual(len(codes), 1, f"Expected one pause but got: {codes}")

    def test_basic_header(self):
        codes = parse_knitout(
            r""";!knitout-3
                ;;Machine: SWG091N2
                ;;Gauge: 15
                ;;Yarn-5: 50-50 Rust
                ;;Carriers: 1 2 3 4 5 6 7 8 9 10
                ;;Position: Right"""
        )

    def test_no_ops(self):
        codes = parse_knitout(
            r""";No-Op: inhook 1
            in 2
            out 3
            ;No-Op: outhook 4
            releasehook 5"""
        )
        self.assertIsInstance(codes[0], Knitout_No_Op)
        self.assertIsInstance(codes[3], Knitout_No_Op)

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
        self.assertIsInstance(codes[0], Knitout_BreakPoint)
        self.assertIsInstance(codes[4], Knitout_BreakPoint)
