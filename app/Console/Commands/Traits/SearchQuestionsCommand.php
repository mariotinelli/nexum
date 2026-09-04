<?php

declare(strict_types = 1);

namespace App\Console\Commands\Traits;

use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Schema;

use function Laravel\Prompts\select;

trait SearchQuestionsCommand
{
    public Collection $columns;

    public ?string $model = null;

    public ?string $searchAttribute = null;

    public ?string $optionValue = null;

    public ?string $optionLabel = null;

    protected function getModel(): ?string
    {
        $selectedModel = select('Selecione a model', options: $this->models->toArray(), default: $this->models->first());

        $model = $this->models->get($selectedModel);

        $this->columns = $this->getColumns((string) $model);

        return $model;
    }

    protected function getSearchAttribute(): string
    {
        return select(
            label: 'Selecione campo de busca',
            options: $this->columns->mapWithKeys(fn (object $column): array => [$column->name => $column->name])->toArray(),
            default: $this->columns->get(1)->name
        );
    }

    protected function getOptionValue(): string
    {
        return select(
            label: 'Selecione o campo de valor (armazena ao selecionar um item no select)',
            options: $this->columns->mapWithKeys(fn (object $column): array => [$column->name => $column->name])->toArray(),
            default: $this->columns->get(0)->name
        );
    }

    protected function getOptionLabel(): ?string
    {
        return select(
            label: 'Selecione o campo de label (exibido em cada item do select)',
            options: $this->columns->mapWithKeys(fn (object $column): array => [$column->name => $column->name])->toArray(),
            default: $this->columns->get(1)->name
        );
    }

    protected function formatType(string $type): string
    {
        return match ($type) {
            'tinyint', 'smallint', 'mediumint', 'int', 'bigint'             => 'int',
            'decimal', 'numeric', 'float', 'double', 'real'                 => 'float',
            'char', 'varchar', 'text', 'tinytext', 'mediumtext', 'longtext' => 'string',
            default                                                         => 'mixed',
        };
    }

    protected function getColumns(string $model): Collection
    {
        $modelInstance = app('App\Models\\' . $model);
        $columns       = Schema::getColumns($modelInstance->getTable());

        return collect($columns)
            ->map(fn (array $column): object => (object) [
                'name' => $column['name'],
                'type' => $this->formatType($column['type_name']),
            ])
            ->filter(fn (object $column): bool => in_array($column->type, [
                'int',
                'string',
                'float',
            ], true));
    }
}
