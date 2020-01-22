# Job Browser Front End Service (BFF)

## Strategy

## Considerations

## General

### Parameter and Return Structure

This is a dynamic service which follows the standard SDK application structure. As such, it uses the somewhat unusual JSONRPC protocol defined by the SDK. This protocol is cited as version "1.1", although no such JSONRPC version was ever officially published or adopted (there were several proposals for a 1.1, but none were ever finalized.)

The request structure is like:

```json
{
  "id": "a string identifier",
  "version": "1.1",
  "method": "Module.function",
  "params": [{
      "param1": "value1",
      "param2": 123,
      "param3": ["an", "array", 123]
   }]
}
```

The `id` is generally ignored, the `version` is always `"1.1"`, and the `method` must be a valid sdk service app identifier in the format `ModuleName.function_name`, where `Module` is the module name (usually PascalCased) and `function` is the function name (usually snake_cased.)

The `params` is an array of values. KBase only utilizes the first parameter, which is typically, but not always, an object. In this service, the first parameter is always an object.

The return structure has one of two forms, the result of a successful execution or an error.

A successful response looks like:

```json
{
    "id": "a string identifier",
    "version": "1.1",
    "result": [{
         "prop1": 123,
         "prop2": "abc"
     }]
}
```

The `id` and `version` comments are the same as for the request. The `result` field is similar to the request params in that it is always an array. KBase typically only uses the first array element to return a result, and that is true for this service. The result may be any json value, but is typically an object. In this service, it is always an object, even for simple results.

An error response looks like:

```json
{
    "id": "a string identifier",
    "version": "1.1",
    "error": {
         "code": 1234,
         "message": "My error message",
         "data": {
              "trace": ["maybe", "a", "stack", "trace"]
         }
    }
}
```

Specific error `code`s are reserved for JSONRPC usage, as specified in the [spec]( https://www.jsonrpc.org/specification#error_object) and in the libraries used to implement JSONRPC for the service. E.g. in the case of Python, the library is [`jsonrpcbase`](https://github.com/level12/jsonrpcbase/blob/39f5f66206fe9fa536fcd059ba9984033e5768b3/jsonrpcbase.py#L485).

Error codes are described in detail below.

THe `message` is a short phrase or sentence which describes the error succinctly. It may be shown to an end user or a developer, so the language should be crafted appropriately.

The `data` property is an object with undefined properties. It should be used to provide information relevant to the type of error. A common field is `trace`, which may be used to provide stacktrace as an array of strings.

Individual errors described in the documentation for this module will also describe the data structure returned.

Standard and module-specific errors are describedin the [errors](./errors.md) document.



## API

- [`get_jobs`](#get_jobs)
- [`query_jobs`](#query_jobs)
- [`get_job_log`](#get_job_log)
- [`cancel_job`](#cancel_job)
- [`get_job_types`](#get_job_types)
- [`get_job_statuses`](#get_job_statuses)
- [`get_client_groups`](#get_client_groups)
- [`get_searchable_job_fields`](#get_searchable_fields)
- [`get_sortable_job_fields`](#get_sortable_fields)
- [`get_log_levels`](#get_log_levels)
- [`is_admin`](#is_admin)

### `get_jobs`

Given one or more job ids, return the associated job information in the same order as job ids are provided. Any job id for which job information cannot be found will be represented with a null value in the same position.

#### Parameters

| Name    | Type           | Required? | Description                               |
| ------- | -------------- | --------- | ----------------------------------------- |
| job_ids | Array\<string> or null | yes       | The unique identifier assigned to the job |

E.g.

```json
{
  "job_ids": ["5d769018aa5a4d298c5dc97a"]
}
```

##### `job_ids`

Each job is assigned a unique identifier when it is accepted by the job service. It is a string value and should be considered opaque.

#### Results

Returns a list of job information objects, corresponding to the job ids passed in the `job_ids` parameter.

E.g.:

```json
[{
    "jobs": [{
        "job_id": "5d769018aa5a4d298c5dc97a",
        "owner": {
            "username": "eapearson",
            "realname": "Erik Pearson"
        },
        "state": {
            "type": "complete",
            "create_at": 1568051224316,
            "queue_at": 1568051224318,
            "run_at": 1568051233294,
            "finish_at": 1568051547380
        },
        "context": {
            "type": "narrative",
            "workspace": {
                "id": 43676,
                "is_accessible": true,
                "is_deleted": false
            },
            "narrative": {
                "title": "Another job browser test"
            }
        },
        "app": {
            "module_name": "ProkkaAnnotation",
            "function_name": "annotate_contigs",
            "title": "Annotate Assembly and ReAnnotate Genomes with Prokka v1.12"
        },
        "client_groups": [
            "njs"
        ]
    }],
    "total_count": 1
}]
```

##### job_id

Every job accepted by the job service is immediately assigned a job id. The job id should be treated as an opaque (devoid of structure) string.

##### type

Jobs are typically spawned from narratives, but there are cases in which jobs are not or in which the job information is incomplete and the narrative is unknown. The `type` field allows us to categories jobs into the following categories:

narrative
: Job was spawned from a a narrative; the job state will contain the narratives workspace information and the narrative title

workspace
: The job was spawned from a non-narrative workspace, or an inaccessible workspace about which nothing can be determined, due to the insufficient authorization.

unknown
: No workspace information is available for the job at all; this should be rare, but instances exist so we must handle it.

##### owner

Every job was spawned by a KBase user, who is responsible for that job and considered to be its owner. 

##### status

A job may exist in one of several states, which is recorded in the `"status"` field. These states are described here because the state determines the shape of the job info object.

create
: Job has been accepted by the job service, but no action has been taken yet.

queue
: Job has been accepted and is in the job queue for a given client group, awaiting its turn to run

run
: Job has been pulled from the queue and is now executing.

complete
: Job has run and successfully finished

error
: Job has stopped with an error; the error is recorded in the job state; an associated code in the job state describes the error.

terminate:
: Job has stopped due to human intervention - either the user or administrator canceled it, or some other process did so; an associated termination code in the job state provides the reason.

The job state determines the structure of the job info object returned. For instance, a job which is currently `queued` will have no `run_at` or `finish_at` time.

##### create_at

Examples:

##### create

When a job is initially created it is in the create state.

```json
{
    "job_id": "5d769018aa5a4d298c5dc97a",
    "type": "narrative",
    "owner": {
        "username": "eapearson",
        "realname": "Erik Pearson"
    },
    "status": "create",
    "create_at": 1568051224317,
    "app": {
        "module": "ProkkaAnnotation",
        "function": "annotate_contigs",
        "title": "Annotate Assembly and ReAnnotate Genomes with Prokka v1.12"
    },
    "workspace": {
         "id": 43676,
         "name": "eapearson:narrative_1564775265770",
         "is_accessible": true,
         "is_deleted": false,
         "narrative": {
             "title": "Another job browser test",
         }
    },
    "client_groups": [
        "njs"
    ]
}
```

##### queue

```json
{
    "job_id": "5d769018aa5a4d298c5dc97a",
    "type": "narrative",
    "owner": {
        "username": "eapearson",
        "realname": "Erik Pearson"
    },
    "status": "queue",
    "create_at": 1568051224317,
    "queue_at": 1568051224317,
    "app": {
        "module": "ProkkaAnnotation",
        "function": "annotate_contigs",
        "title": "Annotate Assembly and ReAnnotate Genomes with Prokka v1.12"
    },
    "workspace": {
         "id": 43676,
         "name": "eapearson:narrative_1564775265770",
         "is_accessible": true,
         "is_deleted": false,
         "narrative": {
             "title": "Another job browser test",
         }
    },
    "client_groups": [
        "njs"
    ]
}
```

##### run

The running state is similar to the queued, with the addition of the "started_at" time which represents the moment the execution engine started running the indicated app.

```json
{
    "job_id": "5d769018aa5a4d298c5dc97a",
    "job_type": "narrative",
    "owner": {
        "username": "eapearson",
        "realname": "Erik Pearson"
    },
    "status": "queued",
    "queued_at": 1568051224317,
    "started_at": 1568051233294,
      "app": {
        "module": "ProkkaAnnotation",
        "function": "annotate_contigs",
        "title": "Annotate Assembly and ReAnnotate Genomes with Prokka v1.12"
    }
     "narrative": {
         "id": 43676,
         "name": "eapearson:narrative_1564775265770",
         "title": "Another job browser test",
         "is_deleted": false,
     },
     "client_groups": [
        "njs"
    ]
}
```

##### complete

The completed state is similar to the queued state, with the addition of the "finished_at" time which represents the moment the execution engine started running the indicated app.

Other states which represent a "finished" app run will also contain the "finished_at" state, including the errored_ and canceled_ states.

```json
{
    "job_id": "5d769018aa5a4d298c5dc97a",
    "job_type": "narrative",
    "owner": {
        "username": "eapearson",
        "realname": "Erik Pearson"
    },
    "status": "queued",
    "queued_at": 1568051224317,
    "started_at": 1568051233294,
    "finished_at": 1568051547380,
    "app": {
        "module": "ProkkaAnnotation",
        "function": "annotate_contigs",
        "title": "Annotate Assembly and ReAnnotate Genomes with Prokka v1.12"
    },
     "narrative": {
         "id": 43676,
         "name": "eapearson:narrative_1564775265770",
         "title": "Another job browser test",
         "is_deleted": false,
     },
     "client_groups": [
        "njs"
    ]
}
```

#### Errors

As with all methods, any general error, unhandled exception, or server error may occur. These are not described here.

##### job not found

Returned when the specified job does not exist.

```json
{
    "code": 40000,
    "message": "A job with this id could not be found, thus it could not be canceled",
    "data": {
        "job_id": "5d769018aa5a4d298c5dc97a"
    }
}
```

### `get_jobs`

Like `get_job` but accepts multiple job ids.

### `query_jobs`

The `query_jobs` method allows one to retrieve a set of jobs matching optional search constraints. It provides for full "paging", allowing both search and sort to be carried out in the service, and also providing for an offset and limit to return only a subset of the found jobs.

The individual jobs returned match the structure defined for [`get_job`](#get_job) so will not be repeated here.

#### Parameters

| Name          | Type           | Required? | Description                                                                                                                          |
| ------------- | -------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| users      | Array\<string> | no        | If provided, filter returned jobs to those owned by at least one of the users in the provided list                                   |
| jobs       | Array\<string> | no        | If provided, filter returned jobs matching the ids in the provided list                                                              |
| sort          | SortSpec       | no        | If provided, indicates a sort order to apply to the queried jobs; see the section below for details.                                 |
| search        | SearchSpec     | no        | If provided, indicates a search condition used to filter jobs; see the section below for details                                     |
| timespan    | TimespanSpec  | no        | If provided, restricts the search by a date range applied to jobs (see below)                                                        |
| client_groups | Array\<string> | no        | If provided, include only jobs whose client groups intersect with this list of client group ids                                      |
| offset        | integer        | no        | If provided, this indicates the starting position within the queried jobs to return the list of jobs; if not provided, defaults to 0 |
| limit         | integer        | no        | If provided, indicates the maximum number of jobs to be returned in the results; defaults to 100                                     |

##### `user_ids`

An optional list of user ids used to constrain the jobs to those owned by a user in this list. 

If omitted, the default behavior is to not filter by user at all. An empty list is considered the same as omitting the parameter.

E.g.

```json
{
  "user_ids": ["mmouse", "dduck", "scoobydoo"]
}
```

##### `job_ids`

An optional list of job ids used to constrain jobs with a job id in this list.

If omitted, the default behavior is to not filter by job id at all. An empty list is considered the same as omitting the parameter.

E.g.

```json
{
  "job_ids": ["5d769018aa5a4d298c5dc97a", "5d768a85aa5a4d298c5dc979"]
}
```

##### `search`

The `search` parameter provides an optional set of search terms which may be used to filter the jobs. It is a list of strings, each of which is a search term. The search applied is simply a case insensitive, substring comparison of each search term to the following fields:
- job id
- narrative title
- app module
- app function
- app function title
- client group
- owner username
- owner real name

At least one field field must match a term, and all terms must match. In other words, the matching per field is rather loose, but adding additional terms restricts the search further.

E.g.

```json
{
  "search": "jsmith fba_tools"
}
```

may match all jobs with owner "jsmith" which are run for apps in the "fba_tools" module.

##### `time_span`

The `time_span` parameter provides a date range which, when present, restricts the returned jobs to those which fall within the given range.

E.g. this restricts the jobs to those which were active from 1/1/2019 up to 2/1/2019.

```json
{
    "time_span": {
        "from": 1546300800,
        "to": 1548979200
    }
}
```

The range is specified by a `from` point in time and a `to` point in time. Either or both may be provided. If either `from` or `to` is omitted, that side of the range is open-ended. The time measurement is epoch time in milliseconds. The `from` time is inclusive, in other words it implies that the lower bound for the range is equal to or greater than the `from` time. The `to` time is normally exclusive, in other words it implies that the upper bound for the range is less than the `to` time.

In order to provide the ability for a fully inclusive range, the `from_inclusive` and `to_inclusive` parameters may be provide to change this behavior. For example, `{"to_inclusive": true}` changes the `to` time to be inclusive, thus forming a "less than or equal to" upper boundary for the range.

If either `from` or `to` is omitted, that side of the range is open-ended.

This range is applied to all timestamps present, queued_at, run_at, finished_at.

The pseudo-logic is:

- if the job is finished
  - if `from` is provided
    - if the `finished_at` time is less than `from`, *omit it*
    - if `to` is provided
      - and `finished_at` is greater than `to`, *omit it*
      - otherwise, **accept it**
  - otherwise (`from` is not provided)
    - if `to` is provided
      - and the `queued_at` time is greater than the `to`, *omit it*
    - otherwise **accept it**
- if the job is running:
  - if `to` is provided
    - and the `queued_at` time is greater than `to`, *omit it*
    - otherwise *accept it*
  - if `from` is provided:
    - **accept it**
  - otherwise **accept it**


##### `sort`

The `sort` parameter is used to provide server-side sorting for the returned jobs. This is important when using paging, because the offset and limit need to apply to the sorted (as well as filtered) jobs.

The default sort order is by submission date in descending order.

The sort parameter is provided as a sort "spec". A sort spec is list of field sort specs. The sort spec is applied in order of the field sort specs. The field sort spec consists of two properties, a `key` and a `direction`.

Due to the need for multiple field sorting, the `key` corresponds to a set of one or more job info properties

narrative
: narrative title

app
: app title, module, app name

submitted
:  submission time

status
: job statuses are ordered by: queued, running, finished, errored_queued, errored_running, canceled_queued, canceled_running

The `direction` corresponds to the sorting direction, and defaults to `ascending`:

- ascending
- descending

E.g. to return jobs ordered primarily by narrative title in alphabetic order and secondarily by submission time with most recent first:

```json
{
  "sort": [
    {
      "key": "narrative",
      "direction": "ascending"
    },
    {
       "key": "submitted",
       "direction": "descending"
    }
  ]
}
```

See also [`get_sort_keys`](#get_sort_keys)

##### `offset`

The `offset` parameter works in concert with the `limit` parameter described below to provide paging or batching behavior. This is necessary because the number of jobs for a given request may be quite high, and for certain applications or constraints large result sets cause performance problems. For instance, accessing a job browser over a slow network connection could cause high latencies for large numbers of jobs.

The `offset` parameter indicates the first job in a sorted, filtered set of jobs to be returned. It is a `0`-based count, so `{"offset": 0}` indicates the first job. An offset greater than the total number of jobs available the the result set results in an error `40003 - Offset greater than available results  `.

E.g.
This will cause the return of jobs starting with the 100th job retrieved, or any empty array if there are fewer than 100 jobs available.

```json
{
  "offset": 100
}
```

##### `limit`

The `limit` parameter determines the maximum number of items to be returned. In concert with `offset` it provides for paging and batching. 

If there are less than `limit` number of items to return, it is not an error; it is simply that the available items are returned.

The default `limit` is 100; the maximum is `1000`.

E.g.

This will cause the return of at most 100 jobs.

```json
{
  "limit": 100
}
```


#### Errors

##### Offset greater than available results

```json
{
    "code": 40003,
    "message" : "Offset greater than available results",
    "data": {
        "offset": 123,
        "result_count": 120
    }
}
```



### `get_job_log`

This method returns a list of log entries for a given job. Like `query_jobs` this method provides full paging support, due the fact that a job log may contain a great many (10s of thousands of) lines. It does not support sorting, always sorting by natural (time) order since that is all that makes sense for dealing with a log.

It supports search as well as filtering by error status.

#### Parameters

| Name   | Type             | Required? | Description                                                                                                                                                   |
| ------ | ---------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| job_id | String           | yes       | The unique identifier assigned to the job                                                                                                                     |
| search | SearchSpec       | no        | If provided, indicates a search condition used to filter jobs; see the section below for details                                                              |
| level  | Array\<LogLevel> | no        | If provided, limits the log lines to those whose logging level can be found in this list.                                                                     |
| offset | integer          | no        | If provided, this indicates the starting position within the queried log to return the list of log lines; if not provided, defaults to 0, there is no maximum |
| limit  | integer          | no        | If provided, indicates the maximum number of log lines to be returned in the results; defaults to 100, maximum is 1000.                                       |

E.g.

This parameter set fetches up to the first 20 log entries for job `"5d769018aa5a4d298c5dc97a"`, limited to log entries which include the text `"dna"` and are of log level `"error"`.

```json
{
  "job_id": "5d769018aa5a4d298c5dc97a",
  "search": "dna",
  "offset": 0,
  "limit": 20,
  "level": ["error"]
}
```

##### `job_id`

The job id for which to fetch the associated jobs.

##### `search`

See [`query_jobs`](#query_jobs) for discussion of the search parameter. This parameter has the same format and behavior.

The fields searched by this method is only the log entry itself.

##### level

Each log entry is assigned a log level. At present this is limited to "default" and "error", since the job logs do not actually contain a log level, but rather a flag indicating whether the log entry is an error or not.

The log level filter is provided as list of strings. Each string must be from the set of log level codes available:

"default"
: An unclassified log entry.

"error"
: The log entry is an error message.

##### `offset`

See [`query_jobs`](#query_jobs).

##### `limit`

[`query_jobs`](#query_jobs)

#### Results
| Name | Type            | Required? | Description                   |
| ---- | --------------- | --------- | ----------------------------- |
| log  | Array\<LogEntry> | yes       | An array (list) of log entries) |

A log line is a structure:

```json
{
  "entry_number": 0,
  "entry": "this is my log entry",
  "level": "default"
}
```

#### Errors

If there is no job found associated with the given id, the code `job_not_found` will be set, and a message similar to `No job could be found associated with job id 5d769018aa5a4d298c5dc97a` will be set.

Other general errors may be returned, indicating runtime or system failures. These may or may not have an error code, and will have various error messages.


### `cancel_job`

Cancels the specified job if it is in an active state (queued or running).

For the current user's own jobs, this method requires no special privileges. For cancellation of another user's jobs, this method requires that the current user be registered as an admin as set in the `kbase.cfg` service configuration file.

See `is_admin` for support in determining whether such privileges exist for the current user.

#### Parameters

| Name   | Type   | Required? | Description                               |
| ------ | ------ | --------- | ----------------------------------------- |
| job_id | String | yes       | The unique identifier assigned to the job |


E.g.,

```json
{
    "job_id": "5d769018aa5a4d298c5dc97a"
}
```

#### Result

The result of a successful call to cancel a job will be an object with a single property `"success"` with value `true`:

```json
{
    "success": true
}
```

#### Errors

##### job not found

Returned when the specified job does not exist.

```json
{
    "code": 10,
    "message": "A job with this id could not be found, thus it could not be canceled",
    "data": {
        "job_id": "5d769018aa5a4d298c5dc97a"
    }
}
```

##### job not active

Returned when the specified job is not in an "active" state, which is either "queued" or "running".

```json
{
    "code": 20,
    "message": "This job is not active, thus it could not be canceled",
    "data": {
        "job_id": "5d769018aa5a4d298c5dc97a",
        "status": "completed"
    }
}
```

##### no permission to cancel

Returned when attempting to cancel another user's job but the current user does not have admin privileges (as defined in `kbase.cfg`).

```json
{
    "code": 21,
    "message": "Permission denied to cancel this job",
    "data": {
        "job_id": "5d769018aa5a4d298c5dc97a",
    }
}
```

### `get_job_types`

This is one of a handful of methods which return the domain of certain fields. In this case it returns all of the job types recognized by the service. As with other domain methods, it provides the code and definition.

#### Parameters

none

#### Result

Returns a list of job types as configured in the service.

```json
{
    "job_types": [
        {
            "code": "narrative",
            "description": "The job was spawned from a Narrative"
        },
        {
            "code": "export",
            "description": "The job was spawned by an export request"
        },
        {
            "code": "unknown",
            "description": "The job type could not be determined"
        }
    ]
}
```

#### Errors

none, since job types must always be defined.

### `get_job_states`

Returns a list of all job state codes recognized by the service.

#### Parameters

none

#### Result

```json
{
    "job_statuses": [
        {
            "code": "queued",
            "description": "The job has been accepted by the execution engine and has been queued for execution."
        },
        {
            "code": "running",
            "description": "The job is executing",
            "notes": "Logs should be available"
        },
        {
            "code": "completed",
            "description": "The job has finished successfully"
        },
        {
            "code": "errored_queued",
            "description": "The job has finished with an error while it was in the queue; it was never run"
        },
        {
            "code": "errored_running",
            "description": "the job has finished with an error while it was running."
        },
        {
            "code": "canceled_queued",
            "description": "The job was canceled, either by the user or an admin, while it was still in the queue"
        },
        {
            "code": "canceled_running",
            "description": "The job was canceled, either by the user or an admin, while it was running"
        }

    ]
}
```

#### Errors

none, as job statuses must be defined by the service.

### `get_client_groups`

Returns a list of client groups.

> TODO: should return more descriptive information about each client group, such as memory, cpus, disk space.

#### Parameters

none

#### Result

```json
{
    "client_groups": [
        {
            "code": "njs",
            "description": "Narrative Job Service"
        },
        {
            "code": "kb_upload",
            "description": "For running uploaders"
        },
        {
            "code": "bigmem", 
            "description": "",

        },
        {
            "code": "extreme",
            "description": ""
        },
        {
            "code": "bigmemlong",
            "description": ""
        },
        {
        		"code": "hpc",
        		"description": ""
        },
        {
            "code": "extreme",
            "description": ""
        }
    ]
}
```

> TODO: get basic descriptors for each of the queues / client groups.
> TODO: normalize language -- are they queues or client groups?
> TODO: what about the difference between queues in different environments. should be superset?

#### Errors

none

### `get_searchable_job_fields`

Returns a list of job info fields which are searched over when a search is conducted by query_jobs. This information can be used for client hints, but because the API provides no field-level search in is purely informational.

#### Parameters

none

#### Result

```json
{
    "searchable_job_fields": [
        {
            "field": "job_id",
            "description": "The Job ID"
        },
        {
            "field": "narrative.title",
            "description": "The narrative title"
        },
        {
            "field": "app.module",
            "description": "The app's module name"
        },
        {
            "field": "app.function",
            "description": "The app's function name"
        },
        {
            "field": "app.title",
            "description": "The app functions title"
        },
        {
            "field": "client_group",
            "description": "The client group list"
        },
        {
            "field": "owner.username",
            "description": "The job owner's username"
        },
        {
            "field": "owner.realname",
            "description": "The job owner's real name"
        }
    ]
}
```

Note that the `"field"` is the path into the job info object.

#### Errors

none

### `get_sort_specs`

Returns a list of sort specs which may be used in a sort spec. The mapping of sort spec key to actual fields is provided. This does not return sort fields, per se, since some sort keys may correspond to more than one field, and the strategy for sorting is provided as a text description rather than as some sort of search expression.

#### Parameters

none

#### Result

```json
{
    "sort_specs": [
        {
            "key": "narrative",
            "fields": ["narrative.title", "queued_at"],
            "description": "Alphabetical sort by narrative title, with a secondary sort on the queue time."
        },
        {
            "key": "app",
            "fields": ["app.module", "app.title"],
            "description": "Alphabetical sort by the app's module name and title"
        },
        {
            "key": "submitted",
            "fields": ["queued_at", "run_at"],
            "description": "Numeric sort by the apps submission (queue) time, and in the unlikely event that two jobs were started at precisely the same time, the run time is used secondarily"
        },
        {
            "key": "status",
            "fields": ["job_status"],
            "description": "A special sort which orders by job status codes in the following order: queued, running, finished, errored_queued, errored_running, canceled_queued, canceled_running"
        }
    ]
}
```

The `key` is the string sent in a call to `query_jobs` to indicate the sorter to select. 

The `fields` is a list of fields considered in the sort. Note that there isn't enough information to replicate the sort.

#### Errors

none

### `get_log_levels`

Returns a list of log level codes and their definitions.

#### Parameters

none

#### Returns

```json
{
    "log_levels": log_
}
```

#### Errors

none

### `is_admin`

Returns a determination of whether the current user is a service administrator or not.

#### Parameters

none

#### Returns

```json
{
    "is_admin": true
}
```

#### Errors

none

## Schema

> TODO: this section incomplete and probably out of date. Leaving it in place to address later. 

These schemas initially generated from sample data in this document via https://www.jsonschema.net.

### `get_job`

#### Parameters

```json
{
  "definitions": {},
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "http://example.com/root.json",
  "type": "object",
  "title": "The Root Schema",
  "required": [
    "job_id"
  ],
  "properties": {
    "job_id": {
      "$id": "#/properties/job_id",
      "type": "string",
      "title": "The Job_id Schema",
      "default": "",
      "examples": [
        "5d769018aa5a4d298c5dc97a"
      ],
      "pattern": "^(.*)$"
    }
  }
}

```

#### Results

```json
{
  "definitions": {},
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "http://example.com/root.json",
  "type": "object",
  "title": "The Root Schema",
  "required": [
    "job_id",
    "job_type",
    "owner",
    "status",
    "queued_at",
    "started_at",
    "finished_at",
    "app_id",
    "app_title",
    "narrative_workspace_id",
    "narrative_workspace_name",
    "narrative_title",
    "narrative_is_deleted",
    "client_groups",
    "error"
  ],
  "properties": {
    "job_id": {
      "$id": "#/properties/job_id",
      "type": "string",
      "title": "The Job_id Schema",
      "default": "",
      "examples": [
        "5d769018aa5a4d298c5dc97a"
      ],
      "pattern": "^(.*)$"
    },
    "job_type": {
      "$id": "#/properties/job_type",
      "type": "string",
      "title": "The Job_type Schema",
      "default": "",
      "examples": [
        "narrative"
      ],
      "pattern": "^(.*)$"
    },
    "owner": {
      "$id": "#/properties/owner",
      "type": "string",
      "title": "The Owner Schema",
      "default": "",
      "examples": [
        "eapearson"
      ],
      "pattern": "^(.*)$"
    },
    "status": {
      "$id": "#/properties/status",
      "type": "string",
      "title": "The Status Schema",
      "default": "",
      "examples": [
        "finished"
      ],
      "pattern": "^(.*)$"
    },
    "queued_at": {
      "$id": "#/properties/queued_at",
      "type": "integer",
      "title": "The Queued_at Schema",
      "default": 0,
      "examples": [
        1568051224317
      ]
    },
    "started_at": {
      "$id": "#/properties/started_at",
      "type": "integer",
      "title": "The Started_at Schema",
      "default": 0,
      "examples": [
        1568051233294
      ]
    },
    "finished_at": {
      "$id": "#/properties/finished_at",
      "type": "integer",
      "title": "The Finished_at Schema",
      "default": 0,
      "examples": [
        1568051547380
      ]
    },
    "app_id": {
      "$id": "#/properties/app_id",
      "type": "string",
      "title": "The App_id Schema",
      "default": "",
      "examples": [
        "ProkkaAnnotation/annotate_contigs"
      ],
      "pattern": "^(.*)$"
    },
    "app_title": {
      "$id": "#/properties/app_title",
      "type": "string",
      "title": "The App_title Schema",
      "default": "",
      "examples": [
        "Annotate Assembly and ReAnnotate Genomes with Prokka v1.12"
      ],
      "pattern": "^(.*)$"
    },
    "narrative_workspace_id": {
      "$id": "#/properties/narrative_workspace_id",
      "type": "integer",
      "title": "The Narrative_workspace_id Schema",
      "default": 0,
      "examples": [
        43676
      ]
    },
    "narrative_workspace_name": {
      "$id": "#/properties/narrative_workspace_name",
      "type": "string",
      "title": "The Narrative_workspace_name Schema",
      "default": "",
      "examples": [
        "eapearson:narrative_1564775265770"
      ],
      "pattern": "^(.*)$"
    },
    "narrative_title": {
      "$id": "#/properties/narrative_title",
      "type": "string",
      "title": "The Narrative_title Schema",
      "default": "",
      "examples": [
        "Another job browser test"
      ],
      "pattern": "^(.*)$"
    },
    "narrative_is_deleted": {
      "$id": "#/properties/narrative_is_deleted",
      "type": "boolean",
      "title": "The Narrative_is_deleted Schema",
      "default": false,
      "examples": [
        false
      ]
    },
    "client_groups": {
      "$id": "#/properties/client_groups",
      "type": "array",
      "title": "The Client_groups Schema",
      "items": {
        "$id": "#/properties/client_groups/items",
        "type": "string",
        "title": "The Items Schema",
        "default": "",
        "examples": [
          "njs"
        ],
        "pattern": "^(.*)$"
      }
    },
    "error": {
      "$id": "#/properties/error",
      "type": "string",
      "title": "The Error Schema",
      "default": "",
      "examples": [
        "some error"
      ],
      "pattern": "^(.*)$"
    }
  }
}
```

### `get_job_log`

#### Parameters

```json
{
  "definitions": {},
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "http://example.com/root.json",
  "type": "object",
  "title": "The Root Schema",
  "required": [
    "job_id",
    "search",
    "offset",
    "limit"
  ],
  "properties": {
    "job_id": {
      "$id": "#/properties/job_id",
      "type": "string",
      "title": "The Job_id Schema",
      "default": "",
      "examples": [
        "5d769018aa5a4d298c5dc97a"
      ],
      "pattern": "^(.*)$"
    },
    "search": {
      "$id": "#/properties/search",
      "type": "string",
      "title": "The Search Schema",
      "default": "",
      "examples": [
        "dna"
      ],
      "pattern": "^(.*)$"
    },
    "offset": {
      "$id": "#/properties/offset",
      "type": "integer",
      "title": "The Offset Schema",
      "default": 0,
      "examples": [
        0
      ]
    },
    "limit": {
      "$id": "#/properties/limit",
      "type": "integer",
      "title": "The Limit Schema",
      "default": 0,
      "examples": [
        20
      ]
    }
  }
}
```

#### Results

```json
{
  "definitions": {},
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "http://example.com/root.json",
  "type": "object",
  "title": "The Root Schema",
  "required": [
    "line_number",
    "entry",
    "is_error"
  ],
  "properties": {
    "line_number": {
      "$id": "#/properties/line_number",
      "type": "integer",
      "title": "The Line_number Schema",
      "default": 0,
      "examples": [
        0
      ]
    },
    "entry": {
      "$id": "#/properties/entry",
      "type": "string",
      "title": "The Entry Schema",
      "default": "",
      "examples": [
        "this is my log entry"
      ],
      "pattern": "^(.*)$"
    },
    "is_error": {
      "$id": "#/properties/is_error",
      "type": "boolean",
      "title": "The Is_error Schema",
      "default": false,
      "examples": [
        false
      ]
    }
  }
}
```

## Error Codes

### Built In

These errors are returned by the SDK-provided components (like the server) or the execution engine dispatch mechanism.

| Code             | Message          | Definition                                                                                            |
| ---------------- | ---------------- | ----------------------------------------------------------------------------------------------------- |
| -32700           | Parse error      | Invalid JSON was received by the server. An error occurred on the server while parsing the JSON text. |
| -32600           | Invalid Request  | The JSON sent is not a valid Request object.                                                          |
| -32601           | Method not found | The method does not exist / is not available.                                                         |
| -32602           | Invalid params   | Invalid method parameter(s).                                                                          |
| -32603           | Internal error   | Internal JSON-RPC error.                                                                              |
| -32000 to -32099 | Server error     | Reserved for implementation-defined server-errors.                                                    |


### This Service

> TODO: these error codes will be adjusted; placeholders for now.

General errors which may be returned by any method:

| Code   | Definition                                                                  |
| ------ | --------------------------------------------------------------------------- |
| -32602 | Invalid method parameter(s).                                                |
| 40200  | Connection to upstream service failed (no connection)                       |
| 40201  | Connection to upstream service timed out (timeout)                          |
| 40202  | Connection to upstream service experienced an error (upstream server error) |
| 40300  | Unauthorized - token is expired, missing, or invalid                        |


Note that the predefined `-32602` error is thrown by the service directly since, for some languages at least, the built-in parameter validation is not as extensive as the method implementation can be.

Method-specific errors:

| Code  | Definition                                                                        |
| ----- | --------------------------------------------------------------------------------- |
| 40000 | Unknown error                                                                     |
| 40001 | Invalid method result                                                             |
| 40100 | The specified job_id does not correspond to a job                                 |
| 40101 | The job is not active, and the operation is only applicable if it is active       |
| 40102 | The current user is attempting an operation for which they do not have permission |
| 40103 | Offset greater than available results                                             |
| 40200 | The specified user as identified by username was not found                        |
