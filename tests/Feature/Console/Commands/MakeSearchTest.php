<?php

declare(strict_types = 1);

use App\Console\Commands\MakeSearch;
use Illuminate\Filesystem\Filesystem;
use Illuminate\Support\Facades\File;

it('loads available models on construct excluding base model', function (): void {
    File::shouldReceive('allFiles')
        ->once()
        ->andReturn([
            new SplFileInfo('User.php'),
            new SplFileInfo('BaseModel.php'),
            new SplFileInfo('Role.php'),
        ]);

    $command = new MakeSearch(new Filesystem());

    expect($command->models->values()->all())->toBe(['User', 'Role']);
});

it('executes handle workflow in expected order', function (): void {
    File::shouldReceive('allFiles')
        ->once()
        ->andReturn([new SplFileInfo('User.php')]);

    $command = new class (new Filesystem()) extends MakeSearch {
        public array $events = [];

        protected function getModel(): ?string
        {
            $this->events[] = 'getModel';

            return 'User';
        }

        protected function getSearchAttribute(): string
        {
            $this->events[] = 'getSearchAttribute';

            return 'name';
        }

        protected function getOptionValue(): string
        {
            $this->events[] = 'getOptionValue';

            return 'id';
        }

        protected function getOptionLabel(): ?string
        {
            $this->events[] = 'getOptionLabel';

            return 'name';
        }

        protected function makeSearchResource(): void
        {
            $this->events[] = 'makeSearchResource';
        }

        protected function makeSearchController(): void
        {
            $this->events[] = 'makeSearchController';
        }

        public function newLine($count = 1): void
        {
            $this->events[] = 'newLine';
        }

        public function info($string, $verbosity = null): void
        {
            $this->events[] = 'info:' . $string;
        }
    };

    $command->handle();

    expect($command->model)->toBe('User')
        ->and($command->searchAttribute)->toBe('name')
        ->and($command->optionValue)->toBe('id')
        ->and($command->optionLabel)->toBe('name')
        ->and(array_slice($command->events, 0, 7))->toBe([
            'getModel',
            'getSearchAttribute',
            'getOptionValue',
            'getOptionLabel',
            'makeSearchResource',
            'makeSearchController',
            'newLine',
        ])
        ->and($command->events[7])->toStartWith('info:Agora');
});

it('creates missing directory and returns path', function (): void {
    File::shouldReceive('allFiles')
        ->once()
        ->andReturn([new SplFileInfo('User.php')]);

    $command = new class (new Filesystem()) extends MakeSearch {
        public function makeDirectoryProxy(string $path): string
        {
            return $this->makeDirectory($path);
        }
    };

    $path = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'make-search-test-' . uniqid();

    expect(is_dir($path))->toBeFalse();

    $result = $command->makeDirectoryProxy($path);

    expect($result)->toBe($path)
        ->and(is_dir($path))->toBeTrue();

    (new Filesystem())->deleteDirectory($path);
});

it('returns plural model and replaces stub variables', function (): void {
    File::shouldReceive('allFiles')
        ->once()
        ->andReturn([new SplFileInfo('User.php')]);

    $command = new class (new Filesystem()) extends MakeSearch {
        public function getPluralModelProxy(string $model): string
        {
            return $this->getPluralModel($model)->toString();
        }

        /**
         * @param  array<string, string>  $variables
         */
        public function getStubContentsProxy(string $stub, array $variables): array | false | string
        {
            return $this->getStubContents($stub, $variables);
        }
    };

    $stubPath = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'make-search-stub-' . uniqid() . '.stub';
    file_put_contents($stubPath, 'Controller {{ model }} {{ action }}');

    $contents = $command->getStubContentsProxy($stubPath, [
        'model'  => 'User',
        'action' => 'Index',
    ]);

    expect($command->getPluralModelProxy('User'))->toBe('Users')
        ->and($contents)->toBe('Controller User Index');

    @unlink($stubPath);
});
