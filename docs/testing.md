# Testing

Testing this dynamic service follows the normal general pattern for KBase SDK services:

- clone the repo
- ensure that a copy of `kb_sdk` is in your terminal path
- run `kb-sdk test` once to generate the `test_local` directory
- update `test_local/test.cfg` with the appropriate auth tokens
- run tests with `kb-sdk test`
- inspect results in the terminal
- inspect the results for coverage in a browser

## Clone Repo

```bash
git clone https://github.com/kbaseapps/kbase-sdk-module-job-browser-bff
```

## Set up `kb_sdk`

The KBase service `sdk` needs to be available locally, built, and in the path. You will need to have a JDK version 8 installed and available in the system path.

- clone `kb_sdk` somewhere in your system; it is recommended to install it in the same directory in which you cloned this repo.
  
  ```bash
  git clone https://github.com/kbase/kb_sdk
  ```

- build it

  ```bash
  cd kb_sdk
  make
  ```

- Add it to the current shell path

  ```bash
  export PATH=$PATH:`pwd`/../kb_sdk/bin
  ```

## run `kb-sdk test` once to generate the `test_local` directory

One of the reasons we love `kb_sdk` is that in order to set up tests, you just need to run the test task once. This won't actually run any tests, since they are not yet set up, but it will create the `test_local` directory and populate it with scrips and `test.cfg`.

`test.cfg` is a supplementary config file used just for testing.

Note that this must be run in the same terminal in which you altered the PATH.

## complete the test config file `test.cfg`

By default `kb_sdk` creates the following configuration fields:

```text
test_token=
kbase_endpoint=https://appdev.kbase.us/services
auth_service_url=https://appdev.kbase.us/services/auth/api/legacy/KBase/Sessions/Login
auth_service_url_allow_insecure=false
```

This is designed so that you can simply enter a token for an `appdev` user, and create tests which work against `appdev` services.

However, for dynamic services, we work against CI, and also in this case we are going to add additional test configuration.

- First, replace `appdev` with `ci`. 
- Next, append the contents of `test/test-extra.cfg` to `test_local/test.cfg`.
- this requires two additional fields to be populated
  
  ```text
  test_token_ci_user=
  test_token_ci_admin=
  ```

  The `test_token_ci_user` field currently must be a token for the CI user `kbaseuitest`. This is a dedicated UI testing user, for which sample jobs have been run, and against which test expectations have been set up.

  The `test_token_ci_admin` field must be a token for the user `eapearson`. We will be establishing a CI account for admin testing.


## run the tests

The run the final tests, simply issue, in the same terminal window:

```bash
kb-sdk test
```

This will build an image for the service, and then invoke the test scripts within a running container, display the results, place the coverage report in `test_local/work/workdir/test_coverage`, and exit.

You may inspect the coverage reports by opening `test_local/workdir/test_coverage/index.html` in your favorite browser.

## TODO

Two types of tests were developed which are not currently run:

- mock tests using `mongodb`
- mock tests using mock endpoints

These tests are especially useful for simulating conditions which cannot be done either with actual services (e.g. testing against CI), or with normal mocks.

The `mongodb` tests utilize a snapshot of actual data which is imported into a local `mongodb` container. This allows a large amount of stable test data. Usage of `mongodb` is simply for convenience -- it is much easier to implement tests against a local database than files.

The network mocks work by running a local mock http server, which can simulate various network or service conditions. E.g. failures, timeouts.
