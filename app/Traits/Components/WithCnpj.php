<?php

declare(strict_types = 1);

namespace App\Traits\Components;

use App\Enums\Toast;
use App\Services\Cnpj\CnpjService;
use App\Services\Cnpj\Exceptions\CnpjLimitException;
use App\Services\Cnpj\Exceptions\CnpjNotFoundException;
use Illuminate\Http\Client\ConnectionException;

trait WithCnpj
{
    use WithAddress;

    public function updateCustomerCnpj(?string $cnpj): void
    {
        if (!$this->cnpjIsValid($cnpj)) {
            return;
        }

        try {
            $response = app(CnpjService::class)->getCustomer($cnpj);

            $this->customer = $response->toModel($this->customer);

            $this->cityName  = $response->address->cityName;
            $this->stateName = $response->address->stateName;

            $this->address = $response->address->toModel($this->address);

            $this->user->email = $response->email;

            $this->partners = $response->partners;

        } catch (CnpjNotFoundException | ConnectionException) {
            $this->sendError();

        } catch (CnpjLimitException) {

            $this->toast(title: 'Limite de consultas atingido, tente novamente após alguns minutos.', type: Toast::Error);
        }
    }

    private function cnpjIsValid(?string $cnpj): bool
    {
        if ($cnpj === null || $cnpj === '' || $cnpj === '0') {
            return false;
        }

        $cnpj = preg_replace('/\D/', '', $cnpj);

        return strlen((string) $cnpj) === 14;
    }

    private function sendError(): void
    {
        $this->toast(title: 'Erro ao buscar o CNPJ, tente novamente mais tarde.', type: Toast::Error);
    }
}
