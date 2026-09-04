<?php

declare(strict_types = 1);

return [

    /*
    |--------------------------------------------------------------------------
    | Root Directory
    |--------------------------------------------------------------------------
    |
    | This value set's the main directory where we will create all the workflows
    | actions, and queries.
    |
    | If you set this to null, we will use a *flat* structure within the app directory.
    | Meaning that everything will be created directly inside the app folder.
    | Ex: App\Workflows, App\Actions, App\Queries
    |
    */
    'root' => env('BRAIN_ROOT', 'Brain'),

    /*
    |--------------------------------------------------------------------------
    | Use Domains
    |--------------------------------------------------------------------------
    |
    | When enabled (true), this setting organizes workflows, actions, and queries
    | into domain-specific subdirectories within the main Brain directory.
    | This helps in maintaining a clear structure, especially in larger
    | applications with multiple domains.
    |
    */
    'use_domains' => env('BRAIN_USE_DOMAINS', true),

    /*
    |--------------------------------------------------------------------------
    | Suffix for Workflow, Action, and Query
    |--------------------------------------------------------------------------
    |
    | When enabled (true), this setting appends a suffix to class names based
    | on their type:
    | - "Action" for actions
    | - "Workflow" for workflows
    | - "Query" for queries
    |
    */
    'use_suffix' => env('BRAIN_USE_SUFFIX', true),

    'suffixes' => [
        'workflow' => env('BRAIN_WORKFLOW_SUFFIX', env('BRAIN_PROCESS_SUFFIX', 'Workflow')),
        'action'   => env('BRAIN_ACTION_SUFFIX', env('BRAIN_TASK_SUFFIX', 'Action')),
        'query'    => env('BRAIN_QUERY_SUFFIX', 'Query'),

        /** @deprecated Use 'workflow' instead. */
        'process' => env('BRAIN_PROCESS_SUFFIX', 'Process'),
        /** @deprecated Use 'action' instead. */
        'task' => env('BRAIN_TASK_SUFFIX', 'Task'),
    ],

    /*
    |--------------------------------------------------------------------------
    | Logging System
    |--------------------------------------------------------------------------
    |
    | When enabled (true), this setting activates logging for all workflows,
    | actions, and queries, allowing you to track their execution and outcomes.
    |
    */
    'log' => env('BRAIN_LOG_ENABLED', false),
];
