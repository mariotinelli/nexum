<?php

declare(strict_types = 1);

namespace App\Traits\Components;

trait WithRepeater
{
    use WithAlert;

    public array $repeaterFields = [];

    public function addItem(string $model): void
    {
        if (substr_count($model, '.') === 2) {
            [$parent, $index, $model]        = str($model)->explode('.')->toArray();
            $this->$parent[$index][$model][] = [...array_fill_keys($this->getRepeaterFields($model), null)];

            return;
        }

        $fields         = $this->getRepeaterFields($model);
        $this->$model[] = [...array_fill_keys($fields, null)];
    }

    public function duplicateItem(string $model): void
    {
        if (substr_count($model, '.') === 3) {
            [$parent, $parentIndex, $model, $modelIndex] = str($model)->explode('.')->toArray();
            $this->$parent[$parentIndex][$model][]       = $this->$parent[$parentIndex][$model][$modelIndex];

            return;
        }

        [$model, $index] = str($model)->explode('.')->toArray();

        $this->$model[] = $this->$model[$index];

        unset($this->$model[$index + 1]['id']);
    }

    public function removeItem(string $model): void
    {
        $this->confirmAlert(
            'Tem certeza que deseja remover este item?',
            'O item será removido definitivamente a partir do momento que você salvar o formulário.',
            'confirmRemoveItem',
            $model
        );
    }

    public function confirmRemoveItem(string $model): void
    {
        if (substr_count($model, '.') === 3) {
            [$parent, $parentIndex, $model, $modelIndex] = str($model)->explode('.')->toArray();
            unset($this->$parent[$parentIndex][$model][$modelIndex]);
            $this->$parent[$parentIndex][$model] = array_values($this->$parent[$parentIndex][$model]);

            return;
        }

        [$model, $index] = str($model)->explode('.')->toArray();

        unset($this->$model[$index]);
        $this->$model = array_values($this->$model);
    }

    public function getRepeaterFields(string $model): array
    {
        return $this->repeaterFields[$model];
    }

    public function setRepeaterFields(string $model, array $fields): void
    {
        $this->repeaterFields[$model] = $fields;
    }
}
