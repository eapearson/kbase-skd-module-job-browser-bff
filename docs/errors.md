# Errors

This service may produce four types of errors.

1. Built-in (and JSONRPC 2.0 compliant) errors:

Several types of errors may be thrown by the SDK-provided code or the execution engine runtime itself. This includes -32700 (parse error), -32600 (invalid request), -32601 (method not found), -32602 (invalid parameters), -32603 (internal error).

> TODO: check where these are emitted, if at all.

E.g.

```json
EXAMPLE HERE
```

2. Uncaught exceptions

Runtime errors which are thrown as exceptions (in exception based languages) and are not caught by user code will be caught by the top level service method dispatcher. When caught, exceptions produce an error structure and issues a 500 response.  Note that some services intentionally "throw" runtime errors (in the sense of, e.g. in Python raising an exception) with the intention that they be caught by the sdk server layer (which will have the code -32700, which is incorrect). This codebase does not, rather either the standard code is returned or an application specific code defined in this document.

> TODO: it is actually more complex than this, in terms of how specific exception types are caught and handled.

E.g.

```json
EXAMPLE HERE
```

1. SDK Internal Errors

Certain runtime errors which are not caught by the message dispatcher, but are rather problems with the SDK server layer, may result in a plain text response body and a 500 response code. This should be considered a bug in the SDK.

The SDK execution engine may detect problems and issue an error response. Such errors include errors parsing the json request. [Are they returned as 500?]

E.g.

```json
EXAMPLE HERE
```

4. Service Errors

Finally, errors encountered in the service itself , such as providing an invalid parameter or an unexpected condition of fetched data, will result in either an error with a standard code or a code specific to the service itself. These errors do not result in a 500 response, but rather a 200.

> consider a 400 response?

E.g. an error structure may look like:

```json
{
  "code": 40000,
  "message": "No job found for the provided job id '5d769018aa5a4d298c5dc97a'",
  "data": {
       "source": "JobBrowserBFF.get_job",
       "trace": [
            "some",
            "stack",
            "trace"
       ]
  }
}
```

Important features of this error structure:

- an error code is emitted. This allows the client code to handle this error explicitly.
- a display message is provided
- the JSONRPC standard field `data` is used to provide some useful context:
  - the source provides a more human-grokkable context than the stack trace. It is intentionally simple, so that layered errors may be more easily understood. (Layered or wrapped errors are not proposed yet.)
  - a standard stack trace as provided by the language runtime, if available

A service method may populate the data field with arbitrary data which is meaningful to the specific error.

## Custom Error Catalog

| Code   | Description                               |
| ------ | ----------------------------------------- |
| 01     | Unknown error |
| 10     | The requested job could not be found                     |
| 20     | Job could not be canceled because it is not active      |
| 21     | Job could not be canceled due to insufficient privileges |
| 30     | The requested job log could not be found |
| 40     | User does not have access to this job |
| 50     | Non-admin user attempt to use admin method |
| 60     | Job is not cancelable |
| 100    | Request timeout |



40xxx job query related
41xxx job action related
