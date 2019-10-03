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

    /* narrative, export, workspace, unknown */
    typedef string JobType;

    typedef structure {
        string UserID;
        string realname;
    } User;

    /* queued, running, completed, errored_queued, errored_running, canceled_queued, canceled_running */
    typedef string JobStatus;

    typedef structure {
        string module_name;
        string function_name;
        string title;
    } AppInfo;

    typedef structure {
        int workspace_id;
        string workspace_name;
        string title;
        bool is_deleted;
    } NarrativeInfo;

    /* njs, bigmem, bigmemlong, kb_import, ...*/
    typedef string ClientGroup;

    typedef structure {
        JobID job_id;
        JobType type;
        User owner;
        JobStatus status;
        epoch_time queued_at;
        epoch_time started_at;
        epoch_time finished_at;
        AppInfo app;
        NarrativeInfo narrative;
        ClientGroup client_group;
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

    /*******************
     * get_jobs
     *******************/

    typedef structure {
        list<JobID> job_ids;
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
    } DateRangeSpec;

    typedef structure {
        list<UserID> users;
        list<JobID> jobs;
        list<SortSpec> sort;
        SearchSpec search;
        DateRangeSpec date_range;
        list<ClientGroup> client_groups;
        int offset;
        int limit;
    } QueryJobsParams;

    typedef structure {
        list<JobInfo> jobs;
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
        string entry;
        LogLevel level;
    } LogEntry;

     typedef structure {
        JobID job_id;
        SearchSpec search;
        list<LogLevel> level;
        int offset;
        int limit;
     } GetJobLogParams;


    typedef structure {
        list<LogEntry> log;
        int total_count;
    } GetJobLogResult;

    funcdef get_job_log(GetJobLogParams params) returns (GetJobLogResult result) authentication required;

    /**********
     * cancel_job
     **********/

     typedef structure {
         JobID job_id;
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
