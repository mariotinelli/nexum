<?php

declare(strict_types = 1);

use App\Console\Commands\Traits\SearchControllerCommand;
use Illuminate\Filesystem\Filesystem;
use Illuminate\Support\Pluralizer;
use Illuminate\Support\Stringable;

it('creates search controller file when it does not exist', function (): void {
    $filesystem = Mockery::mock(Filesystem::class);

    $command = new class ($filesystem) {
        use SearchControllerCommand;

        public ?string $model = 'User';

        public ?string $searchAttribute = 'name';

        public string $directoryPath = '';

        public string $infoMessage = '';

        public string $errorMessage = '';

        public function __construct(public Filesystem $filesystem)
        {
        }

        public function runMakeSearchController(): void
        {
            $this->makeSearchController();
        }

        protected function getSearchControllerPath(): string
        {
            return 'C:\\tmp\\Search\\UsersController.php';
        }

        protected function getSearchControllerSourceFile(): string
        {
            return 'controller-content';
        }

        protected function makeDirectory(string $path): string
        {
            $this->directoryPath = $path;

            return $path;
        }

        protected function info($string, $verbosity = null): void
        {
            $this->infoMessage = $string;
        }

        protected function error($string, $verbosity = null): void
        {
            $this->errorMessage = $string;
        }
    };

    $path = 'C:\\tmp\\Search\\UsersController.php';

    $filesystem->shouldReceive('exists')->once()->with($path)->andReturnFalse();
    $filesystem->shouldReceive('put')->once()->with($path, 'controller-content');

    $command->runMakeSearchController();

    expect($command->directoryPath)->toBe('C:\\tmp\\Search')
        ->and($command->infoMessage)->toBe("File : {$path} created")
        ->and($command->errorMessage)->toBeEmpty();
});

it('shows error when search controller file already exists', function (): void {
    $filesystem = Mockery::mock(Filesystem::class);

    $command = new class ($filesystem) {
        use SearchControllerCommand;

        public ?string $model = 'User';

        public ?string $searchAttribute = 'name';

        public string $infoMessage = '';

        public string $errorMessage = '';

        public function __construct(public Filesystem $filesystem)
        {
        }

        public function runMakeSearchController(): void
        {
            $this->makeSearchController();
        }

        protected function getSearchControllerPath(): string
        {
            return 'C:\\tmp\\Search\\UsersController.php';
        }

        protected function getSearchControllerSourceFile(): string
        {
            return 'controller-content';
        }

        protected function makeDirectory(string $path): string
        {
            return $path;
        }

        protected function info($string, $verbosity = null): void
        {
            $this->infoMessage = $string;
        }

        protected function error($string, $verbosity = null): void
        {
            $this->errorMessage = $string;
        }
    };

    $path = 'C:\\tmp\\Search\\UsersController.php';

    $filesystem->shouldReceive('exists')->once()->with($path)->andReturnTrue();
    $filesystem->shouldReceive('put')->never();

    $command->runMakeSearchController();

    expect($command->errorMessage)->toBe("File : {$path} already exits")
        ->and($command->infoMessage)->toBeEmpty();
});

it('returns expected search controller stub path', function (): void {
    $command = new class (new Filesystem()) {
        use SearchControllerCommand;

        public function __construct(public Filesystem $filesystem)
        {
        }

        public function getStubPath(): string
        {
            return $this->getSearchControllerStub();
        }
    };

    expect($command->getStubPath())->toEndWith('stubs/search-controller.stub');
});

it('builds expected search controller file path', function (): void {
    $command = new class (new Filesystem()) {
        use SearchControllerCommand;

        public ?string $model = 'User';

        public function __construct(public Filesystem $filesystem)
        {
        }

        public function getControllerPath(): string
        {
            return $this->getSearchControllerPath();
        }

        protected function getPluralModel(string $model): Stringable
        {
            return str(Pluralizer::plural($model));
        }
    };

    $path = $command->getControllerPath();

    expect($path)->toBe(app_path('Http/Controllers/Search/UsersController.php'));
});

it('builds source and stub variables for controller file', function (): void {
    $command = new class (new Filesystem()) {
        use SearchControllerCommand;

        public ?string $model = 'User';

        public ?string $searchAttribute = 'email';

        public string $receivedStub = '';

        public array $receivedVariables = [];

        public function __construct(public Filesystem $filesystem)
        {
        }

        public function getVariables(): array
        {
            return $this->getSearchControllerStubVariables();
        }

        public function getSourceFile(): string
        {
            return $this->getSearchControllerSourceFile();
        }

        protected function getPluralModel(string $model): Stringable
        {
            return str(Pluralizer::plural($model));
        }

        protected function getStubContents(string $stub, array $stubVariables = []): string
        {
            $this->receivedStub      = $stub;
            $this->receivedVariables = $stubVariables;

            return 'compiled-source';
        }
    };

    expect($command->getVariables())->toBe([
        'model'           => 'User',
        'variable'        => 'users',
        'pluralModel'     => 'Users',
        'searchAttribute' => 'email',
    ])
        ->and($command->getSourceFile())->toBe('compiled-source')
        ->and($command->receivedStub)->toEndWith('stubs/search-controller.stub')
        ->and($command->receivedVariables)->toBe([
            'model'           => 'User',
            'variable'        => 'users',
            'pluralModel'     => 'Users',
            'searchAttribute' => 'email',
        ]);
});
