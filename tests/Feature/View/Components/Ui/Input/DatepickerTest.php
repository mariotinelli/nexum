<?php

declare(strict_types = 1);

use App\View\Components\Ui\Input\Datepicker;

it('builds datepicker config for range mode', function (): void {
    $component = new Datepicker(range: true, showMonths: 1, date: true);
    $config    = $component->getConfig();

    expect($config['mode'])->toBe('range')
        ->and($config['showMonths'])->toBe(2)
        ->and($config['dateFormat'])->toBe('d/m/Y')
        ->and($config['allowInput'])->toBeFalse();
});

it('builds datepicker config for time and datetime modes', function (): void {
    $time     = new Datepicker(time: true, minTime: '08:00', maxTime: '18:00');
    $dateTime = new Datepicker(datetime: true);

    expect($time->getConfig()['dateFormat'])->toBe('H:i')
        ->and($time->getConfig()['enableTime'])->toBeTrue()
        ->and($time->getConfig()['noCalendar'])->toBeTrue()
        ->and($dateTime->getConfig()['dateFormat'])->toBe('d/m/Y H:i');
});

it('returns mask according to mode and renders view', function (): void {
    expect((new Datepicker(time: true))->mask())->toBe('99:99')
        ->and((new Datepicker(date: true))->mask())->toBe('99/99/9999')
        ->and((new Datepicker(datetime: true))->mask())->toBe('99/99/9999 99:99')
        ->and((new Datepicker())->mask())->toBeNull()
        ->and((new Datepicker(range: true))->isRange())->toBeTrue()
        ->and((new Datepicker())->render()->name())->toBe('components.ui.input.datepicker');
});
