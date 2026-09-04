<?php

declare(strict_types = 1);

namespace App\Services\Cnpj;

use App\Services\Cnpj\Entities\Customer;
use App\Services\Cnpj\Exceptions\CnpjLimitException;
use App\Services\Cnpj\Exceptions\CnpjNotFoundException;
use App\Services\Cnpj\Exceptions\CnpjOutOfServiceException;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Support\Facades\Http;

class CnpjService
{
    private readonly PendingRequest $api;

    public function __construct()
    {
        $this->api = Http::baseUrl('https://publica.cnpj.ws/cnpj/');
    }

    /**
     * @throws CnpjNotFoundException
     * @throws CnpjLimitException
     * @throws ConnectionException|CnpjOutOfServiceException
     */
    public function getCustomer(string $cnpj): Customer
    {
        $cnpj = preg_replace('/\D/', '', $cnpj);

        $response = $this->api->get("{$cnpj}");

        if ($response->status() === 404 || $response->status() === 400) {
            throw new CnpjNotFoundException();
        }

        if ($response->status() === 429) {
            throw new CnpjLimitException();
        }

        if ($response->status() === 504) {
            throw new CnpjOutOfServiceException();
        }

        throw new CnpjNotFoundException();
    }
}
