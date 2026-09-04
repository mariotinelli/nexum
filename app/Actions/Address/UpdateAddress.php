<?php

declare(strict_types = 1);

namespace App\Actions\Address;

use App\Models\Address;

class UpdateAddress
{
    public function handle(Address $address, array $data): Address
    {
        $address->update([
            'city_id'     => $data['city_id'],
            'street'      => $data['street'],
            'number'      => $data['number'],
            'district'    => $data['district'],
            'postal_code' => $data['postal_code'],
            'complement'  => $data['complement'],
        ]);

        return $address->refresh();
    }
}
