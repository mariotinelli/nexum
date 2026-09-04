<?php

declare(strict_types = 1);

use App\Console\Commands\Traits\SearchQuestionsCommand;
use Illuminate\Support\Collection;
use Laravel\Prompts\SelectPrompt;

beforeEach(function (): void {
    SelectPrompt::fallbackUsing(fn (SelectPrompt $prompt): int | string | null => $prompt->default);
    SelectPrompt::fallbackWhen(true);
});

it('returns selected model and loads columns', function (): void {
    $command = new class () {
        use SearchQuestionsCommand;

        public Collection $models;

        public string $receivedModel = '';

        public function __construct()
        {
            $this->models = collect([
                'User' => 'User',
                'Role' => 'Role',
            ]);
        }

        public function getModelProxy(): ?string
        {
            return $this->getModel();
        }

        protected function getColumns(string $model): Collection
        {
            $this->receivedModel = $model;

            return collect([
                (object) ['name' => 'id', 'type' => 'int'],
                (object) ['name' => 'name', 'type' => 'string'],
            ]);
        }
    };

    $model = $command->getModelProxy();

    expect($model)->toBe('User')
        ->and($command->receivedModel)->toBe('User')
        ->and($command->columns)->toHaveCount(2);
});

it('returns search, value and label options using defaults', function (): void {
    $command = new class () {
        use SearchQuestionsCommand;

        public function __construct()
        {
            $this->columns = collect([
                (object) ['name' => 'id', 'type' => 'int'],
                (object) ['name' => 'name', 'type' => 'string'],
                (object) ['name' => 'total', 'type' => 'float'],
            ]);
        }

        public function getSearchAttributeProxy(): string
        {
            return $this->getSearchAttribute();
        }

        public function getOptionValueProxy(): string
        {
            return $this->getOptionValue();
        }

        public function getOptionLabelProxy(): ?string
        {
            return $this->getOptionLabel();
        }
    };

    expect($command->getSearchAttributeProxy())->toBe('name')
        ->and($command->getOptionValueProxy())->toBe('id')
        ->and($command->getOptionLabelProxy())->toBe('name');
});

it('formats database column types to primitive aliases', function (): void {
    $command = new class () {
        use SearchQuestionsCommand;

        public function formatTypeProxy(string $type): string
        {
            return $this->formatType($type);
        }
    };

    expect($command->formatTypeProxy('tinyint'))->toBe('int')
        ->and($command->formatTypeProxy('decimal'))->toBe('float')
        ->and($command->formatTypeProxy('varchar'))->toBe('string')
        ->and($command->formatTypeProxy('json'))->toBe('mixed');
});

it('loads and filters model columns to supported output types', function (): void {
    $command = new class () {
        use SearchQuestionsCommand;

        public function getColumnsProxy(string $model): Collection
        {
            return $this->getColumns($model);
        }
    };

    $columns = $command->getColumnsProxy('User');

    expect($columns)->toBeInstanceOf(Collection::class)
        ->and($columns->pluck('name')->all())->toContain('name', 'email')
        ->and($columns->pluck('name')->all())->not->toContain('created_at', 'updated_at', 'deleted_at', 'email_verified_at')
        ->and($columns->every(fn (object $column): bool => in_array($column->type, ['int', 'string', 'float'], true)))->toBeTrue();
});
