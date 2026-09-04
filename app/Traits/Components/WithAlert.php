<?php

declare(strict_types = 1);

namespace App\Traits\Components;

trait WithAlert
{
    protected function alert(
        string $title,
        ?string $description = null,
        string $type = 'alert',
        ?string $method = 'confirm',
        array | int | string | null $params = null,
        string $textConfirm = 'Confirmar',
        ?string $textCancel = 'Cancelar',
        bool $actionConfirm = true,
        ?string $cancelMethod = null,
    ): void {
        $this->dispatch(
            'alert',
            description: $description,
            title: $title,
            type: $type,
            method: $method,
            params: $params,
            componentId: $this->getId(),
            actionConfirm: $actionConfirm,
            textConfirm: $textConfirm,
            textCancel: $textCancel,
            actionCancel: $cancelMethod,
        );
    }

    protected function confirmAlert(
        string $title,
        ?string $description = null,
        ?string $method = 'confirm',
        array | int | string | null $params = null,
        string $textConfirm = 'Confirmar',
        ?string $textCancel = 'Cancelar',
        bool $actionConfirm = true,
        ?string $cancelMethod = null,
    ): void {

        $this->alert(
            $title,
            $description,
            'confirmation',
            $method,
            $params,
            $textConfirm,
            $textCancel,
            $actionConfirm,
            $cancelMethod,
        );
    }
}
