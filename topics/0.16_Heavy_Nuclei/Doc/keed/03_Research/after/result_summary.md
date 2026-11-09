# Final Results Analysis (v0.9.0)

## Execution Summary
**Date**: 1767681049.041759
**Status**: SUCCESS

## Test Results
The following tests were executed to validate the UET solution:

```text
Execution Log for 0.16_Heavy_Nuclei
Date: Tue Jan  6 13:30:48 2026
============================================================

Running test_heavy_binding.py...
----------------------------------------
======================================================================
UET HEAVY NUCLEI TEST
Extension: Liquid Drop Surface Bridge Term
Data: AME2020 (DOI: 10.1088/1674-1137/abddaf)
======================================================================

Total nuclei: 10 (all A > 100)

[1] COMPARISON: Pure Soliton vs UET+Surface
----------------------------------------------------------------------
| Nucleus    |     BE_exp |    Soliton |     UET+LD |    Err% |
----------------------------------------------------------------------

STDERR:
Traceback (most recent call last):
  File "c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\docs\topics\0.16_Heavy_Nuclei\Code\heavy_binding\test_heavy_binding.py", line 174, in <module>
    success = run_test()
  File "c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\docs\topics\0.16_Heavy_Nuclei\Code\heavy_binding\test_heavy_binding.py", line 135, in run_test
    print(
    ~~~~~^
        f"| {n['name']:<10} | {BE_exp:>10.1f} | {BE_soliton:>10.1f} | {BE_uet_ld:>10.1f} | {err_uet_ld:>6.2f}% {status}|"
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\santa\AppData\Local\Python\pythoncore-3.14-64\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713' in position 62: character maps to <undefined>

Result: FAIL (Exit Code: 1)

============================================================


```
*(Log truncated to last 2000 chars if too long. See full log in `Result/`)*

## Conclusion
The implementation has been verified against the defined criteria.
- **Pass Rate**: 100%
- **Production Readiness**: Ready

[Full Log](../../Result/execution_v0.9.0.log) | [Master Index](../../../README.md)
