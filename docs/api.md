# Job Browser BFF API

## cancel_job

Cancel processing of the specified job. This method does not return anything, and may return an error if the user does not have permission to modify the job, or the job does not exist.

### parameters

- job_id
- timeout
- code
- admin

| key | required | type | description |
| --- | -------- | ---- | ----------- ||
| job_id  | *        | integer     | the id of the job to be canceled                      |
| timeout | *        | integer     | timeout in ms for calls out to upstream services      |
| code    |          | integer 0-1 | termination code; defaults to 1 if admin, 0 otherwise |
| admin   |          | boolean     | whether admin privs should be applied                 |

#### job_id

The id of the job to be canceled.

#### timeout

The timeout is supplied as an integer representing the time in milliseconds to wait for any upstream service requests to complete. 

#### code

A job termination (of which cancellation is one kind) always carries a reason code to record why the job was terminated.

These are:

| code | description                          |
| ---- | ------------------------------------ |
| 0    | user cancellation                    |
| 1    | admin cancellation                   |
| 2    | terminated by some automatic process |

#### admin

The admin parameter specifies whether the request is to be applied as an administrator. This call will fail if the authentication token supplied in the request does not correspond to a user with admin access for the EE2 service.

### Result

This method does not have a result.

### Errors

The following errors may be returned (in addition to [standard JSON RPC 2.0 errors](standard-errors.md).

| code | message                                                  |
| ---- | -------------------------------------------------------- |
| 10   | The requested job could not be found                     |
| 20   | Job could not be canceled because it is not active       |
| 21   | Job could not be canceled due to insufficient privileges |
