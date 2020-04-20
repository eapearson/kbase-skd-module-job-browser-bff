/*
A KBase module: JobBrowserBFF
*/

module JobBrowserBFF {
    /* Type synonym conveniences */
    typedef int bool;
    typedef int epoch_time;
    typedef string UserID;

    /* Core types */
    typedef string JobID;

    typedef structure {
        string UserID;
        string realname;
    } User;

    /* create | queue | run | complete | error | terminate */
    typedef string JobStatus;

    typedef structure {
        string module_name;
        string function_name;
        string title;
        list<string> client_groups;
    } AppInfo;

    /* njs, bigmem, bigmemlong, kb_import, ...*/
    typedef string ClientGroup;

    typedef structure {
        int code;
        string message;
        UnspecifiedObject error; /* may be object, string, or null */
    } JSONRPC11Error;

    typedef int JobErrorCode;

    typedef structure {
        JobErrorCode code;
        string message;
        JSONRPC11Error service_error;
    } JobError;

    typedef int JobTerminationCode;

    typedef structure {
        JobTerminationCode code;
        string message;
    } JobTermination;
    
    /* Superset of all fields used to represent job state
      See the TS typing and json-schema */
    typedef structure {
        JobStatus status;
        epoch_time create_at;
        epoch_time queue_at;
        epoch_time run_at;
        epoch_time finish_at; 
        ClientGroup client_group;
        JobError error;
        JobTermination termination;
    } JobState;

    /*
      represents the context in which the job was spawned.
      should collapse to narrative, perhaps, when all is said and
      done, but at the moment there are:
      narrative, export, workspace, unknown
    */
    typedef structure  {
        int id;
        bool is_accessible;
        /* fields below only populated if workspace is accessible */
        string name;
        bool is_deleted;
    } WorkspaceInfo;

    typedef structure {
        string title;
        bool is_temporary;
    } NarrativeInfo;

    /* narrative, export, workspace, unknown */
    typedef string JobContextType;
    
    typedef structure {
        JobContextType type; 
        WorkspaceInfo workspace;
        NarrativeInfo narrative;
    } JobContext;

    typedef structure {
        JobID job_id;
        User owner;
        JobState state;
        AppInfo app;
        JobContext context;
    } JobInfo;

    typedef structure {
         string code;
         string description;
         string notes;
     } DomainDefinition;

    typedef structure {
         string code;
         int order;
         string description;
         string notes;
    } OrderedDomainDefinition;

    /*
     get_jobs

     Given a set of job ids, returns the job information for each job, in the same order as 
     the ids were provided.

     As with other methods, this one takes an "admin" parameter which indicates whether the call is 
     intended for administrator usage or not. If for administrator usage, the token provided in the call
     must be associated with an account with admin privileges for the upstream service. An error with 
     code 50 is returned otherwise.

     Params:
     - job_ids: a list of job ids to look up and provide information about
     - admin: a boolean indicating whether the request is for a admin usage or not

     Returns:
     - jobs - list of JobStatus

     Throws:
     - 10 - Job not found: If the any of the given job ids are not found
     */

    typedef structure {
        list<JobID> job_ids;
        bool admin;
    } GetJobsParams;

    typedef structure {
        list<JobInfo> jobs;
    } GetJobsResult;

    funcdef get_jobs(GetJobsParams params) returns (GetJobsResult result) authentication required;


    /*******************
     * query_jobs
     *******************/

    /* behaves as an enum: narrative, app, submitted, status */
    typedef string SortKey;

    /* behaves as an enum: ascending, descending */
    typedef string SortDirection;

    typedef structure {
        SortKey key;
        SortDirection direction;
    } SortSpec;

    typedef structure {
        list<string> terms;
    } SearchSpec;

    typedef structure {
        epoch_time from;
        epoch_time to;
    } TimeSpanSpec;

    typedef structure {
        list<int> workspace_id;
        list<string> status;
        list<string> username;
        list<string> app_id;
        list<string> job_id;
        list<int> error_code;
        list<int> terminated_code;
    } FilterSpec;

    /* TODO: expand to match the filtering, sorting, searching of kb_metrics */
    typedef structure {
        list<JobID> jobs;
        list<SortSpec> sort;
        SearchSpec search;
        FilterSpec filter;
        TimeSpanSpec time_span;
        list<ClientGroup> client_groups;
        int offset;
        int limit;
        bool admin;
    } QueryJobsParams;

    typedef structure {
        list<JobInfo> jobs;
        int found_count;
        int total_count;
    } QueryJobsResult;

    funcdef query_jobs(QueryJobsParams params) returns (QueryJobsResult result) authentication required;

    /**********
     * get_job_log
     **********/

    /* enum-like: default, error */
    typedef string LogLevel;

    typedef structure {
        int entry_number;
        int created;
        string entry;
        LogLevel level;
    } LogEntry;

     typedef structure {
        JobID job_id;
        SearchSpec search;
        list<LogLevel> level;
        int offset;
        int limit;
        bool admin;
     } GetJobLogParams;


    typedef structure {
        list<LogEntry> log;
        int total_count;
    } GetJobLogResult;

    funcdef get_job_log(GetJobLogParams params) returns (GetJobLogResult result) authentication required;

    /*
      cancel_job
     
      Given a job id, attempt to cancel the associated job.

      Params:
      - job_id: The id for the job to cancel
     
      Returns:
      - nothing.
     
      Throws:
      - 10 - Job not found: If the given job id was not found 
     
      Note that attempting to cancel a job which is not cancelable will not throw an error.
      This behavior may change in the future.
      At present one upstream service (njsw) ignores this condition, but another (ee2) returns an error.
      For ee2 that error is ignored.
     
    */

     typedef structure {
         JobID job_id;
         bool admin;
         int timeout;
     } CancelJobParams;

     typedef structure {
         bool canceled;
     } CancelJobResult;

     funcdef cancel_job(CancelJobParams params) returns (CancelJobResult result) authentication required;

    /**********
     * get_job_types
     **********/
     typedef structure  {
         list<DomainDefinition> job_type_definitions;
     } GetJobTypesResult;

     funcdef get_job_types() returns (GetJobTypesResult result) authentication required;

    /**********
     * get_job_states
     **********/

    typedef structure {
        list<DomainDefinition> job_states;
    } GetJobStatesResult;

    funcdef get_job_states() returns (GetJobStatesResult result) authentication required;

     /**********
     * get_client_groups
     **********/
     typedef structure {
        list<DomainDefinition> searchable_job_fields;
    } GetClientGroupsResult;

     funcdef get_client_groups() returns (GetClientGroupsResult result) authentication required;

    /**********
    * get_searchable_job_fields
    **********/
    typedef structure {
        list<DomainDefinition> searchable_job_fields;
    } GetSearchableJobFieldsResult;

    funcdef get_searchable_job_fields() returns (GetSearchableJobFieldsResult result) authentication required;

    /**********
    * get_sort_keys
    **********/
    typedef structure {
        string key;
        list<string> fields;
        string description;
    } SortSpecDefinition;

    typedef structure {
        list<SortSpecDefinition> sort_fields;
    } GetSortSpecsResult;

    funcdef get_sort_specs() returns (GetSortSpecsResult result) authentication required;


     /**********
    * get_log_levels
    **********/
    typedef structure {
        list<OrderedDomainDefinition> log_levels;
    } GetLogLevelsResult;

    funcdef get_log_levels() returns (GetLogLevelsResult result) authentication required;

    /**********
    * is_admin
    **********/
    typedef structure {
        bool is_admin;
    } IsAdminResult;

    funcdef is_admin() returns (IsAdminResult result) authentication required;

};
