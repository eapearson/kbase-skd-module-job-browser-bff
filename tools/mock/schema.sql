create table jobs (

)

create table job_logs (
    job_id char(32) not null,
    logged_at integer not null,
    message text not null,
    is_error boolean not null,

    primary key (job_id, logged_at)
)