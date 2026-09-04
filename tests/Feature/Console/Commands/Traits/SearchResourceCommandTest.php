<?php

declare(strict_types = 1);

use App\Console\Commands\Traits\SearchResourceCommand;
use Illuminate\Filesystem\Filesystem;
use Illuminate\Support\Collection;

it('creates search resource file when it does not exist', function (): void {
    $filesystem = Mockery::mock(Filesystem::class);

    $command = new class ($filesystem) {
        use SearchResourceCommand;

        public ?string $model = 'User';

        public ?string $optionValue = 'id';

        public ?string $optionLabel = 'name';

        public Collection $columns;

        public string $directoryPath = '';

        public int $newLines = 0;

        public string $infoMessage = '';

        public string $errorMessage = '';

        public function __construct(public Filesystem $filesystem)
        {
            $this->columns = collect([
                (object) ['name' => 'id', 'type' => 'int'],
                (object) ['name' => 'name', 'type' => 'string'],
            ]);
        }

        public function runMakeSearchResource(): void
        {
            $this->makeSearchResource();
        }

        protected function getSearchResourcePath(): string
        {
            return 'C:\\tmp\\Search\\UserResource.php';
        }

        protected function getSearchResourceSourceFile(): string
        {
            return 'resource-content';
        }

        protected function makeDirectory(string $path): string
        {
            $this->directoryPath = $path;

            return $path;
        }

        protected function newLine($count = 1): void
        {
            $this->newLines += $count;
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

    $path = 'C:\\tmp\\Search\\UserResource.php';

    $filesystem->shouldReceive('exists')->once()->with($path)->andReturnFalse();
    $filesystem->shouldReceive('put')->once()->with($path, 'resource-content');

    $command->runMakeSearchResource();

    expect($command->directoryPath)->toBe('C:\\tmp\\Search')
        ->and($command->newLines)->toBe(1)
        ->and($command->infoMessage)->toBe("File : {$path} created")
        ->and($command->errorMessage)->toBeEmpty();
});

it('shows error when search resource file already exists', function (): void {
    $filesystem = Mockery::mock(Filesystem::class);

    $command = new class ($filesystem) {
        use SearchResourceCommand;

        public ?string $model = 'User';

        public ?string $optionValue = 'id';

        public ?string $optionLabel = 'name';

        public Collection $columns;

        public string $infoMessage = '';

        public string $errorMessage = '';

        public int $newLines = 0;

        public function __construct(public Filesystem $filesystem)
        {
            $this->columns = collect([
                (object) ['name' => 'id', 'type' => 'int'],
                (object) ['name' => 'name', 'type' => 'string'],
            ]);
        }

        public function runMakeSearchResource(): void
        {
            $this->makeSearchResource();
        }

        protected function getSearchResourcePath(): string
        {
            return 'C:\\tmp\\Search\\UserResource.php';
        }

        protected function getSearchResourceSourceFile(): string
        {
            return 'resource-content';
        }

        protected function makeDirectory(string $path): string
        {
            return $path;
        }

        protected function newLine($count = 1): void
        {
            $this->newLines += $count;
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

    $path = 'C:\\tmp\\Search\\UserResource.php';

    $filesystem->shouldReceive('exists')->once()->with($path)->andReturnTrue();
    $filesystem->shouldReceive('put')->never();

    $command->runMakeSearchResource();

    expect($command->newLines)->toBe(1)
        ->and($command->errorMessage)->toBe("File : {$path} already exits")
        ->and($command->infoMessage)->toBeEmpty();
});

it('returns expected search resource stub and file path', function (): void {
    $command = new class (new Filesystem()) {
        use SearchResourceCommand;

        public ?string $model = 'User';

        public function __construct(public Filesystem $filesystem)
        {
        }

        public function getStubPath(): string
        {
            return $this->getSearchResourceStub();
        }

        public function getResourcePath(): string
        {
            return $this->getSearchResourcePath();
        }
    };

    expect($command->getStubPath())->toEndWith('stubs/search-resource.stub')
        ->and($command->getResourcePath())->toBe(app_path('Http/Resources/Search/UserResource.php'));
});

it('builds source and stub variables for resource file', function (): void {
    $command = new class (new Filesystem()) {
        use SearchResourceCommand;

        public ?string $model = 'User';

        public ?string $optionValue = 'id';

        public ?string $optionLabel = 'name';

        public Collection $columns;

        public string $receivedStub = '';

        public array $receivedVariables = [];

        public function __construct(public Filesystem $filesystem)
        {
            $this->columns = collect([
                (object) ['name' => 'id', 'type' => 'int'],
                (object) ['name' => 'name', 'type' => 'string'],
                (object) ['name' => 'amount', 'type' => 'float'],
            ]);
        }

        public function getVariables(): array
        {
            return $this->getSearchResourceStubVariables();
        }

        public function getSourceFile(): string
        {
            return $this->getSearchResourceSourceFile();
        }

        protected function getStubContents(string $stub, array $stubVariables = []): string
        {
            $this->receivedStub      = $stub;
            $this->receivedVariables = $stubVariables;

            return 'compiled-resource-source';
        }
    };

    expect($command->getVariables())->toBe([
        'model'           => 'User',
        'optionValue'     => 'id',
        'optionLabel'     => 'name',
        'optionValueType' => 'int',
        'optionLabelType' => 'string',
    ])
        ->and($command->getSourceFile())->toBe('compiled-resource-source')
        ->and($command->receivedStub)->toEndWith('stubs/search-resource.stub')
        ->and($command->receivedVariables)->toBe([
            'model'           => 'User',
            'optionValue'     => 'id',
            'optionLabel'     => 'name',
            'optionValueType' => 'int',
            'optionLabelType' => 'string',
        ]);
});
