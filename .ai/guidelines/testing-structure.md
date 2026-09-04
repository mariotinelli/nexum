# Test Structure

- Every behavior-bearing application file must have its own dedicated test file. Do not group multiple production classes into a single broad test file.
- Mirror the production file's directory structure under the owning test suite and append `Test` to the production class name.
- Apply this one-to-one structure to Livewire components, controllers, Brain Actions, Workflows, Queries, services, jobs, listeners, commands, and other application classes that contain behavior.
- Follow the nearest existing test conventions for setup, helpers, factories, naming, and Pest syntax.

Examples:

- `app/Livewire/Users/Create.php` → `tests/Feature/Livewire/Users/CreateTest.php`
- `app/Livewire/Users/Index.php` → `tests/Feature/Livewire/Users/IndexTest.php`
- `app/Http/Controllers/Users/IndexController.php` → `tests/Feature/Http/Controllers/Users/IndexControllerTest.php`
- `app/Brain/Users/Actions/CreateUserAction.php` → `tests/Brain/Users/Actions/CreateUserActionTest.php`
- `app/Brain/Users/Workflows/CreateUserWorkflow.php` → `tests/Brain/Users/Workflows/CreateUserWorkflowTest.php`
- `app/Brain/Users/Queries/SearchUsersQuery.php` → `tests/Brain/Users/Queries/SearchUsersQueryTest.php`
