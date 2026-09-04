<?php

declare(strict_types = 1);

use App\Enums\Rules;
use App\Rules\MoneyRule;

class TestableMoneyRule extends MoneyRule
{
    public function orderedRulesProxy(): array
    {
        return $this->correctOrderRules();
    }

    public function hasRuleProxy(Rules $rule): bool
    {
        return $this->hasRule($rule);
    }
}

it('validates values using between, min and max rules', function (): void {
    $failMessages = [];
    $fail         = function (string $message) use (&$failMessages): void {
        $failMessages[] = $message;
    };

    $rule = (new MoneyRule())
        ->between(10, 20)
        ->min(10)
        ->max(20);

    $rule->validate('total', '15,00', $fail);
    expect($failMessages)->toHaveCount(0);

    $rule->validate('total', '5,00', $fail);
    expect($failMessages)->not->toBeEmpty();
});

it('returns default rule and skips empty between/min values', function (): void {
    $failMessages = [];
    $fail         = function (string $message) use (&$failMessages): void {
        $failMessages[] = $message;
    };

    $rule = (new MoneyRule())->default()->between(10, 20)->min(10);
    $rule->validate('total', null, $fail);

    expect($failMessages)->toHaveCount(0);
});

it('orders rules according to money rule precedence', function (): void {
    $rule = new TestableMoneyRule();
    $rule->max(50)->between(10, 40)->min(5);

    expect(array_keys($rule->orderedRulesProxy()))->toBe([
        Rules::Between->value,
        Rules::Min->value,
        Rules::Max->value,
    ])
        ->and($rule->hasRuleProxy(Rules::Min))->toBeTrue()
        ->and($rule->hasRuleProxy(Rules::Required))->toBeFalse();
});
