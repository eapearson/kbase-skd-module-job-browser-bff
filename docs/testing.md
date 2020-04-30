## Setup and test

Add your KBase developer token to `test_local/test.cfg` and run the following:

```bash
make
kb-sdk test
```

After making any additional changes to this repo, run `kb-sdk test` again to verify that everything still works.