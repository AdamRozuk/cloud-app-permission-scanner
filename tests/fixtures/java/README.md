# Java test fixtures

Small Java sources that the test suite compiles with `javac` into real
`.class` files, so the scanner runs against genuine bytecode.

- `stubs/` holds minimal stand-ins for AWS SDK v2 client interfaces. They only
  need the right package, class and method names, because the scanner reads
  method references from the constant pool and never links against the SDK.
- `app/` holds the "application" classes that call those clients. Tests scan
  only the compiled `app/` output.
