# Risk Rules (Banking Rewrite)

This document captures the current rule-based risk checks for the banking
rewrite endpoint. These rules are v1 and intended for rapid, deterministic
screening.

## Risky phrases (exact match, case-insensitive)
- guaranteed returns
- will give you excellent returns
- risk-free
- no risk
- you should buy
- i recommend you invest

## Examples
- "guaranteed returns" -> high
- "will give you excellent returns" -> medium
- "you should invest now" -> medium/high (add to list if used)
