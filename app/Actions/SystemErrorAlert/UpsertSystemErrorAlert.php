<?php

declare(strict_types = 1);

namespace App\Actions\SystemErrorAlert;

use App\Enums\SystemErrorAlertStatuses;
use App\Models\SystemErrorAlert;
use Carbon\CarbonInterface;

class UpsertSystemErrorAlert
{
    /**
     * @param  array<string, mixed>  $attributes
     */
    public function handle(array $attributes): SystemErrorAlert
    {
        /** @var CarbonInterface $occurredAt */
        $occurredAt = $attributes['occurred_at'];

        /** @var SystemErrorAlert|null $systemErrorAlert */
        $systemErrorAlert = SystemErrorAlert::query()
            ->where('fingerprint', $attributes['fingerprint'])
            ->where('environment', $attributes['environment'])
            ->first();

        if ($systemErrorAlert) {
            $systemErrorAlert->update([
                'severity'        => $attributes['severity'],
                'exception_class' => $attributes['exception_class'],
                'message'         => $attributes['message'],
                'file'            => $attributes['file'],
                'line'            => $attributes['line'],
                'route_name'      => $attributes['route_name'],
                'request_method'  => $attributes['request_method'],
                'request_url'     => $attributes['request_url'],
                'request_id'      => $attributes['request_id'],
                'user_id'         => $attributes['user_id'],
                'context'         => $attributes['context'],
                'trace'           => $attributes['trace'],
                'occurrences'     => $systemErrorAlert->occurrences + 1,
                'last_seen_at'    => $occurredAt,
            ]);

            return $systemErrorAlert->refresh();
        }

        return SystemErrorAlert::query()->create([
            'fingerprint'     => $attributes['fingerprint'],
            'status'          => SystemErrorAlertStatuses::Open,
            'severity'        => $attributes['severity'],
            'environment'     => $attributes['environment'],
            'exception_class' => $attributes['exception_class'],
            'message'         => $attributes['message'],
            'file'            => $attributes['file'],
            'line'            => $attributes['line'],
            'route_name'      => $attributes['route_name'],
            'request_method'  => $attributes['request_method'],
            'request_url'     => $attributes['request_url'],
            'request_id'      => $attributes['request_id'],
            'user_id'         => $attributes['user_id'],
            'context'         => $attributes['context'],
            'trace'           => $attributes['trace'],
            'occurrences'     => 1,
            'first_seen_at'   => $occurredAt,
            'last_seen_at'    => $occurredAt,
        ]);
    }
}
