<?php

declare(strict_types = 1);

namespace App\Services\ViaCep;

use App\Services\ViaCep\Entities\Address;
use App\Services\ViaCep\Exceptions\BadRequestException;
use App\Services\ViaCep\Exceptions\CepNotFoundException;
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Support\Facades\Http;

class ViaCepService
{
    private readonly PendingRequest $api;

    public function __construct()
    {
        $this->api = Http::baseUrl('https://viacep.com.br/ws/');
    }

    /**
     * @throws BadRequestException
     * @throws CepNotFoundException
     *
     */
    public function getAddress(string $cep): Address
    {
        $cep = str_replace('-', '', $cep);

        $response = $this->api->get("{$cep}/json/");

        if ($response->status() === 400) {
            throw new BadRequestException();
        }

        if (isset($response->json()['erro']) && $response->json()['erro'] === "true") {
            throw new CepNotFoundException();
        }

        return Address::createFromApi($response->json());
    }
}
