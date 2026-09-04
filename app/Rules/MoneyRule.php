<?php

declare(strict_types = 1);

namespace App\Rules;

use App\Rules\Traits\MoneyValidations;
use Closure;
use Illuminate\Contracts\Validation\ValidationRule;

class MoneyRule implements ValidationRule
{
    use MoneyValidations;

    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        $this->checkValidations($attribute, $value, $fail);
    }
}
