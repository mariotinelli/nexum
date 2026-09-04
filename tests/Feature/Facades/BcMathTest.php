<?php

declare(strict_types = 1);

use App\Actions\BcMath as BcMathAction;
use App\Facades\BcMath as BcMathFacade;

it('resolves the facade root to BcMath action', function (): void {
    expect(BcMathFacade::getFacadeRoot())->toBeInstanceOf(BcMathAction::class);
});

it('proxies static calls to the underlying action', function (): void {
    $result = BcMathFacade::make(10)
        ->add(2)
        ->sub(0.5);

    expect((string) $result)->toBe('11.50');
});
